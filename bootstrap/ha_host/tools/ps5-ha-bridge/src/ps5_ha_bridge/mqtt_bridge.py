from __future__ import annotations

import asyncio
import json
import logging
import queue
import time
from dataclasses import asdict
from typing import Any

import paho.mqtt.client as mqtt

from .config import AppConfig
from .playstation import DeviceSnapshot, PlayStationClient


LOG = logging.getLogger(__name__)


class MqttBridge:
    def __init__(self, config: AppConfig) -> None:
        if config.ps5.host is None:
            raise ValueError("ps5.host is required for daemon mode")
        self._config = config
        self._ps = PlayStationClient(config.bridge.credential_storage_dir)
        self._commands: queue.Queue[str] = queue.Queue()
        self._command_task: asyncio.Task[None] | None = None
        self._pending_power_state: str | None = None
        self._pending_command: str | None = None
        self._pending_until = 0.0
        self._fast_poll_until = 0.0
        self._ps5_host = config.ps5.host
        self._confirmed_actual_power_state: str | None = None
        self._actual_candidate_state: str | None = None
        self._actual_candidate_count = 0
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=config.mqtt.client_id)
        if config.mqtt.username:
            self._client.username_pw_set(config.mqtt.username, config.mqtt.password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    async def run(self) -> None:
        self._client.connect(self._config.mqtt.host, self._config.mqtt.port, keepalive=60)
        self._client.loop_start()
        try:
            await self._run_loop()
        finally:
            self._publish_availability(False)
            self._client.loop_stop()
            self._client.disconnect()

    async def _run_loop(self) -> None:
        failures = 0
        next_poll_at = 0.0
        cleared_old_discovery = False
        while True:
            await self._drain_commands()
            now = time.monotonic()
            if now >= next_poll_at:
                try:
                    snapshot = await self._status()
                except Exception as exc:
                    failures += 1
                    LOG.warning(
                        "status poll failed (%s/%s): %s",
                        failures,
                        self._config.bridge.availability_failures,
                        exc,
                    )
                    if failures >= self._config.bridge.availability_failures:
                        self._publish_availability(False)
                        self._publish_json("diagnostic/state", {"error": str(exc)})
                else:
                    failures = 0
                    if not cleared_old_discovery:
                        self._clear_old_discovery()
                        cleared_old_discovery = True
                    self._publish_discovery(snapshot)
                    if self._should_hold_pending(snapshot, now):
                        self._publish_pending_snapshot(snapshot)
                        next_poll_at = now + self._config.bridge.command_transition_poll_seconds
                    else:
                        if self._pending_power_state is not None:
                            actual = _power_state(snapshot.status)
                            if actual == self._pending_power_state:
                                LOG.info(
                                    "command transition completed: %s -> %s",
                                    self._pending_command,
                                    actual,
                                )
                            else:
                                LOG.warning(
                                    "command transition timed out: %s expected %s, got %s",
                                    self._pending_command,
                                    self._pending_power_state,
                                    actual,
                                )
                            self._clear_pending()
                        self._publish_snapshot(snapshot, available=True)
                        next_poll_at = now + self._next_poll_interval(now)

            await asyncio.sleep(1)

    async def _drain_commands(self) -> None:
        if self._command_task is not None:
            if not self._command_task.done():
                return
            try:
                self._command_task.result()
            except Exception:
                LOG.exception("command task failed unexpectedly")
            self._command_task = None

        try:
            command = self._commands.get_nowait()
        except queue.Empty:
            return
        self._command_task = asyncio.create_task(self._handle_command(command))

    async def _handle_command(self, command: str) -> None:
        try:
            normalized = command.strip().upper()
            if normalized in {"WAKE", "ON"}:
                await self._refresh_host_for_command()
                self._start_pending("ON", normalized)
                snapshot = await self._ps.wake(
                    self._ps5_host or "",
                    self._config.ps5.device_id,
                    wait_seconds=self._config.bridge.command_transition_timeout_seconds,
                )
            elif normalized in {"STANDBY", "OFF"}:
                await self._refresh_host_for_command()
                self._start_pending("OFF", normalized)
                snapshot = await self._ps.standby(
                    self._ps5_host or "",
                    self._config.ps5.device_id,
                    wait_seconds=self._config.bridge.command_transition_timeout_seconds,
                )
            else:
                LOG.warning("ignoring unsupported command: %s", command)
                return
            actual = _power_state(snapshot.status)
            if actual == self._pending_power_state:
                self._clear_pending()
                self._publish_snapshot(snapshot, available=True)
            elif time.monotonic() < self._pending_until:
                self._publish_pending_snapshot(snapshot)
            else:
                LOG.warning(
                    "command transition timed out: %s expected %s, got %s",
                    self._pending_command,
                    self._pending_power_state,
                    actual,
                )
                self._clear_pending()
                self._publish_snapshot(snapshot, available=True)
            self._publish_json("diagnostic/state", {"last_command": normalized, "ok": True})
        except Exception as exc:
            self._clear_pending()
            LOG.exception("command failed: %s", command)
            self._publish_json("diagnostic/state", {"last_command": command, "ok": False, "error": str(exc)})
            try:
                snapshot = await self._status()
            except Exception as status_exc:
                LOG.warning("failed to refresh status after command failure: %s", status_exc)
            else:
                self._publish_snapshot(snapshot, available=True)

    async def _status(self) -> DeviceSnapshot:
        if self._config.ps5.device_id:
            snapshot = await self._ps.status_by_device_id(
                self._config.ps5.device_id,
                fallback_host=self._ps5_host,
            )
        else:
            snapshot = await self._ps.status(self._ps5_host or "")
        if snapshot is None:
            target = self._config.ps5.device_id or self._ps5_host
            raise RuntimeError(f"PlayStation not found: {target}")
        self._remember_snapshot(snapshot)
        return snapshot

    async def _refresh_host_for_command(self) -> None:
        if not self._config.ps5.device_id:
            return
        try:
            await self._status()
        except Exception as exc:
            LOG.debug("could not refresh PS5 host before command: %s", exc)

    def _remember_snapshot(self, snapshot: DeviceSnapshot) -> None:
        if snapshot.ip == self._ps5_host:
            return
        old_host = self._ps5_host
        self._ps5_host = snapshot.ip
        LOG.info("PS5 host changed from %s to %s; using discovered address.", old_host, snapshot.ip)
        self._persist_snapshot(snapshot)

    def _persist_snapshot(self, snapshot: DeviceSnapshot) -> None:
        path = self._config.bridge.state_path
        if path is None:
            return
        data: dict[str, Any] = {}
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                LOG.warning("could not read PS5 state before updating host: %s", exc)
            else:
                if isinstance(loaded, dict):
                    data = loaded
        data.update(
            {
                "host": snapshot.ip,
                "device_id": snapshot.device_id,
                "name": snapshot.name,
                "device_type": snapshot.device_type,
                "status": snapshot.status,
            }
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            LOG.warning("could not update PS5 state host to %s: %s", snapshot.ip, exc)

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        del userdata, flags, properties
        if getattr(reason_code, "is_failure", False):
            LOG.error("MQTT connection failed: %s", reason_code)
            return
        LOG.info("MQTT connected")
        client.subscribe(f"{self._config.mqtt.base_topic}/power/set")
        self._publish_availability(True)

    def _on_message(self, client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
        del client, userdata
        topic = message.topic
        if topic.endswith("/power/set"):
            self._commands.put(message.payload.decode("utf-8", errors="replace"))

    def _publish_snapshot(self, snapshot: DeviceSnapshot, *, available: bool) -> None:
        actual_power_state = self._confirmed_actual_power_state_for(snapshot)
        self._publish_availability(available)
        self._publish("status/state", snapshot.status)
        self._publish("power/actual_state", actual_power_state)
        self._publish("power/state", _power_state(snapshot.status))
        payload = asdict(snapshot)
        payload["actual_power_state"] = actual_power_state
        self._publish_json("attributes/state", payload)

    def _start_pending(self, target_power_state: str, command: str) -> None:
        self._pending_power_state = target_power_state
        self._pending_command = command
        self._pending_until = time.monotonic() + self._config.bridge.command_transition_timeout_seconds
        self._fast_poll_until = self._pending_until
        self._publish("power/state", target_power_state)
        self._publish_json(
            "attributes/state",
            {
                "command_pending": True,
                "target_power_state": target_power_state,
                "last_command": command,
            },
        )

    def _should_hold_pending(self, snapshot: DeviceSnapshot, now: float) -> bool:
        if self._pending_power_state is None:
            return False
        if _power_state(snapshot.status) == self._pending_power_state:
            return False
        return now < self._pending_until

    def _publish_pending_snapshot(self, snapshot: DeviceSnapshot) -> None:
        if self._pending_power_state is None:
            self._publish_snapshot(snapshot, available=True)
            return
        actual_power_state = self._confirmed_actual_power_state_for(snapshot)
        payload = asdict(snapshot)
        payload.update(
            {
                "actual_power_state": actual_power_state,
                "command_pending": True,
                "target_power_state": self._pending_power_state,
                "last_command": self._pending_command,
            }
        )
        self._publish_availability(True)
        self._publish("status/state", snapshot.status)
        self._publish("power/actual_state", actual_power_state)
        self._publish("power/state", self._pending_power_state)
        self._publish_json("attributes/state", payload)

    def _clear_pending(self) -> None:
        self._pending_power_state = None
        self._pending_command = None
        self._pending_until = 0.0

    def _next_poll_interval(self, now: float) -> int:
        if now < self._fast_poll_until:
            return self._config.bridge.command_transition_poll_seconds
        return self._config.bridge.poll_interval_seconds

    def _confirmed_actual_power_state_for(self, snapshot: DeviceSnapshot) -> str:
        raw_power_state = _power_state(snapshot.status)
        if raw_power_state not in {"ON", "OFF"}:
            return self._confirmed_actual_power_state or "UNKNOWN"

        if self._confirmed_actual_power_state is None:
            self._confirmed_actual_power_state = raw_power_state
            self._actual_candidate_state = None
            self._actual_candidate_count = 0
            return raw_power_state

        if raw_power_state == self._confirmed_actual_power_state:
            self._actual_candidate_state = None
            self._actual_candidate_count = 0
            return self._confirmed_actual_power_state

        if raw_power_state == self._actual_candidate_state:
            self._actual_candidate_count += 1
        else:
            self._actual_candidate_state = raw_power_state
            self._actual_candidate_count = 1

        required = max(1, self._config.bridge.actual_state_confirmations)
        if self._actual_candidate_count >= required:
            LOG.info(
                "actual power state confirmed: %s -> %s after %s reading(s)",
                self._confirmed_actual_power_state,
                raw_power_state,
                self._actual_candidate_count,
            )
            self._confirmed_actual_power_state = raw_power_state
            self._actual_candidate_state = None
            self._actual_candidate_count = 0

        return self._confirmed_actual_power_state

    def _publish_availability(self, available: bool) -> None:
        self._publish("availability", "online" if available else "offline")

    def _publish_discovery(self, snapshot: DeviceSnapshot) -> None:
        prefix = self._config.mqtt.discovery_prefix
        node = _slug(self._config.bridge.discovery_name)
        base = self._config.mqtt.base_topic
        device = {
            "identifiers": [f"ps5-ha-bridge-{snapshot.device_id}"],
            "name": self._config.bridge.discovery_name,
            "manufacturer": "Sony",
            "model": snapshot.device_type,
        }
        availability = [{"topic": f"{base}/availability"}]
        self._publish_json(
            f"{prefix}/switch/{node}/power/config",
            {
                "name": "Power",
                "unique_id": f"{node}_power",
                "command_topic": f"{base}/power/set",
                "state_topic": f"{base}/power/state",
                "payload_on": "ON",
                "payload_off": "OFF",
                "state_on": "ON",
                "state_off": "OFF",
                "json_attributes_topic": f"{base}/attributes/state",
                "availability": availability,
                "device": device,
                "icon": "mdi:sony-playstation",
            },
            retain=True,
            absolute=True,
        )
        self._publish_json(
            f"{prefix}/binary_sensor/{node}/actual_power/config",
            {
                "name": "Actual Power",
                "object_id": f"{node}_actual_power",
                "unique_id": f"{node}_actual_power",
                "state_topic": f"{base}/power/actual_state",
                "payload_on": "ON",
                "payload_off": "OFF",
                "json_attributes_topic": f"{base}/attributes/state",
                "availability": availability,
                "device": device,
                "device_class": "power",
                "entity_category": "diagnostic",
                "icon": "mdi:sony-playstation",
            },
            retain=True,
            absolute=True,
        )

    def _clear_old_discovery(self) -> None:
        prefix = self._config.mqtt.discovery_prefix
        node = _slug(self._config.bridge.discovery_name)
        for topic in (
            f"{prefix}/button/{node}/wake/config",
            f"{prefix}/button/{node}/standby/config",
            f"{prefix}/binary_sensor/{node}/power/config",
            f"{prefix}/sensor/{node}/status/config",
            f"{prefix}/sensor/{node}/activity/config",
            f"{prefix}/button/{node}/go_home/config",
        ):
            self._publish(topic, "", retain=True, absolute=True)

    def _publish_json(self, topic: str, payload: dict[str, Any], *, retain: bool = False, absolute: bool = False) -> None:
        self._publish(topic, json.dumps(payload, sort_keys=True), retain=retain, absolute=absolute)

    def _publish(self, topic: str, payload: str, *, retain: bool = False, absolute: bool = False) -> None:
        full_topic = topic if absolute else f"{self._config.mqtt.base_topic}/{topic}"
        self._client.publish(full_topic, payload, retain=retain)


def clear_discovery(config: AppConfig) -> None:
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"{config.mqtt.client_id}-cleanup",
    )
    if config.mqtt.username:
        client.username_pw_set(config.mqtt.username, config.mqtt.password)
    client.connect(config.mqtt.host, config.mqtt.port, keepalive=30)
    client.loop_start()
    try:
        for topic in _current_discovery_topics(config):
            client.publish(topic, "", retain=True).wait_for_publish()
        client.publish(f"{config.mqtt.base_topic}/availability", "offline").wait_for_publish()
    finally:
        client.loop_stop()
        client.disconnect()


def _current_discovery_topics(config: AppConfig) -> tuple[str, ...]:
    prefix = config.mqtt.discovery_prefix
    node = _slug(config.bridge.discovery_name)
    return (
        f"{prefix}/switch/{node}/power/config",
        f"{prefix}/binary_sensor/{node}/actual_power/config",
    )


def _power_state(status: str) -> str:
    normalized = status.upper()
    if normalized in {"AWAKE", "ON"}:
        return "ON"
    if normalized in {"STANDBY", "STANDBY_MODE", "OFF"}:
        return "OFF"
    return "UNKNOWN"


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_") or "ps5"
