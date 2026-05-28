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
                    self._publish_snapshot(snapshot, available=True)
                next_poll_at = now + self._config.bridge.poll_interval_seconds

            await asyncio.sleep(1)

    async def _drain_commands(self) -> None:
        while True:
            try:
                command = self._commands.get_nowait()
            except queue.Empty:
                return
            await self._handle_command(command)

    async def _handle_command(self, command: str) -> None:
        try:
            normalized = command.strip().upper()
            if normalized in {"WAKE", "ON"}:
                await self._ps.wake(self._config.ps5.host or "", self._config.ps5.device_id)
            elif normalized in {"STANDBY", "OFF"}:
                await self._ps.standby(self._config.ps5.host or "", self._config.ps5.device_id)
            else:
                LOG.warning("ignoring unsupported command: %s", command)
                return
            self._publish_json("diagnostic/state", {"last_command": normalized, "ok": True})
        except Exception as exc:
            LOG.exception("command failed: %s", command)
            self._publish_json("diagnostic/state", {"last_command": command, "ok": False, "error": str(exc)})

    async def _status(self) -> DeviceSnapshot:
        if self._config.ps5.device_id:
            snapshot = await self._ps.status_by_device_id(
                self._config.ps5.device_id,
                fallback_host=self._config.ps5.host,
            )
        else:
            snapshot = await self._ps.status(self._config.ps5.host or "")
        if snapshot is None:
            target = self._config.ps5.device_id or self._config.ps5.host
            raise RuntimeError(f"PlayStation not found: {target}")
        return snapshot

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
        self._publish_availability(available)
        self._publish("status/state", snapshot.status)
        self._publish("power/state", _power_state(snapshot.status))
        self._publish_json("attributes/state", asdict(snapshot))

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
    return (f"{prefix}/switch/{node}/power/config",)


def _power_state(status: str) -> str:
    normalized = status.upper()
    if normalized in {"AWAKE", "ON"}:
        return "ON"
    if normalized in {"STANDBY", "STANDBY_MODE", "OFF"}:
        return "OFF"
    return "UNKNOWN"


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_") or "ps5"
