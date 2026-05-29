from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import AppConfig, BridgeConfig, MqttConfig, Ps5Config
from .mqtt_bridge import MqttBridge, clear_discovery
from .playstation import DeviceSnapshot, PlayStationClient
from .webui import WEB_PORT, run_web


LOG = logging.getLogger(__name__)

OPTIONS_PATH = Path("/data/options.json")
STATE_PATH = Path("/config/ps5-ha-bridge/state.json")
CREDENTIAL_DIR = Path("/config/ps5-ha-bridge/credentials")


class AddonRuntime:
    def __init__(self, options: dict[str, Any]) -> None:
        self.options = options
        self.client = PlayStationClient(CREDENTIAL_DIR)
        self.state: dict[str, Any] = _load_state(STATE_PATH)
        self.discovered_devices: list[DeviceSnapshot] = []
        self.snapshot: DeviceSnapshot | None = None
        self.pairing_mode = False
        self.pairing_in_progress = False
        self.message: str | None = None
        self.error: str | None = None
        self._mqtt_task: asyncio.Task[None] | None = None
        self._refresh_task: asyncio.Task[None] | None = None
        self._device_refresh_task: asyncio.Task[None] | None = None
        self._pair_lock = asyncio.Lock()

    async def initialize(self) -> None:
        if self.state.get("pairing_mode") is True:
            LOG.info("PS5 bridge is in persisted pairing mode. Open the add-on Web UI to pair.")
            self.request_device_refresh()
            self.pairing_mode = True
            self.message = "Pairing mode enabled. Generate a new PS5 Link Device PIN and submit it below."
            return

        self.snapshot = await self._load_paired_snapshot()
        if self.snapshot is not None:
            self.request_snapshot_refresh()
            await self.start_mqtt()
            return

        self.request_device_refresh()
        LOG.info("PS5 is not paired yet. Open the add-on Web UI to pair.")
        self.pairing_mode = True

    async def refresh_devices(self) -> None:
        self.discovered_devices = await self.client.discover(timeout=8.0)
        ps5_count = len([device for device in self.discovered_devices if device.device_type.upper() == "PS5"])
        LOG.info("Discovered %s PS5 device(s).", ps5_count)

    async def refresh_snapshot(self) -> None:
        if self.snapshot is None or self.pairing_in_progress:
            return
        await self.refresh_devices()
        discovered = self._select_discovered(
            device_id=self.snapshot.device_id,
            host=self.snapshot.ip,
        )
        if discovered is None:
            LOG.debug("Paired PS5 %s was not found during UI refresh.", self.snapshot.device_id)
            return
        if discovered != self.snapshot:
            LOG.info("Refreshed paired PS5 %s status=%s at %s", discovered.name, discovered.status, discovered.ip)
            self.snapshot = discovered
            self.state = _save_state(STATE_PATH, discovered)

    def request_snapshot_refresh(self) -> None:
        if self.snapshot is None or self.pairing_in_progress:
            return
        if self._refresh_task and not self._refresh_task.done():
            return
        self._refresh_task = asyncio.create_task(self.refresh_snapshot())
        self._refresh_task.add_done_callback(self._refresh_done)

    async def start_mqtt(self) -> None:
        if self.snapshot is None:
            return
        if self._mqtt_task and not self._mqtt_task.done():
            return
        config = _build_config(self.options, self.snapshot)
        LOG.info("Starting MQTT bridge for %s (%s) at %s", self.snapshot.name, self.snapshot.device_id, self.snapshot.ip)
        self._mqtt_task = asyncio.create_task(MqttBridge(config).run())
        self._mqtt_task.add_done_callback(self._mqtt_done)

    async def restart_mqtt(self) -> None:
        await self.stop_mqtt()
        await self.start_mqtt()

    async def stop_mqtt(self, *, clear_widget: bool = False) -> None:
        snapshot = self.snapshot
        if self._mqtt_task and not self._mqtt_task.done():
            self._mqtt_task.cancel()
            try:
                await self._mqtt_task
            except asyncio.CancelledError:
                pass
        self._mqtt_task = None
        if clear_widget and snapshot is not None:
            LOG.info("Clearing PS5 MQTT discovery while waiting for re-pair.")
            await asyncio.to_thread(clear_discovery, _build_config(self.options, snapshot))

    async def enter_pairing_mode(self) -> None:
        await self.stop_mqtt(clear_widget=True)
        self.snapshot = None
        self.state = _save_pairing_mode(STATE_PATH, self.state, True)
        self.pairing_mode = True
        self.message = "Pairing mode enabled. Generate a new PS5 Link Device PIN and submit it below."
        self.error = None
        self.request_device_refresh()

    def request_device_refresh(self) -> None:
        if self._device_refresh_task and not self._device_refresh_task.done():
            return
        self._device_refresh_task = asyncio.create_task(self.refresh_devices())
        self._device_refresh_task.add_done_callback(self._refresh_done)

    async def pair(self, host: str, npsso: str, pin: str) -> None:
        if self._pair_lock.locked():
            raise RuntimeError("Pairing is already in progress.")
        async with self._pair_lock:
            self.pairing_in_progress = True
            self.message = "Pairing in progress. Keep this page open."
            self.error = None
            try:
                if not _optional_str(host):
                    raise RuntimeError("Select a discovered PS5 before pairing.")
                LOG.info("Pairing with PS5 at %s. NPSSO is used once and is not saved.", host)
                snapshot = await self.client.pair(host, pin, npsso, timeout=30.0)
                self.snapshot = snapshot
                self.state = _save_state(STATE_PATH, snapshot, pairing_mode=False)
                self.pairing_mode = False
                self.message = f"Paired {snapshot.name} at {snapshot.ip}."
                LOG.info("Pairing succeeded for %s (%s).", snapshot.name, snapshot.device_id)
                await self.restart_mqtt()
            finally:
                self.pairing_in_progress = False

    async def _load_paired_snapshot(self) -> DeviceSnapshot | None:
        host = _optional_str(self.state.get("host"))
        device_id = _optional_str(self.state.get("device_id"))

        discovered = self._discover_target(host, device_id)
        if discovered is not None:
            host = discovered.ip
            device_id = discovered.device_id
            LOG.info("Found PS5 %s (%s) at %s, status=%s", discovered.name, discovered.device_id, discovered.ip, discovered.status)
            if self.client.has_credential(discovered.device_id):
                self.state = _save_state(STATE_PATH, discovered, pairing_mode=False)
                return discovered

        if device_id and self.client.has_credential(device_id) and host:
            LOG.info("Using saved paired PS5 %s at %s. It may be in rest mode.", device_id, host)
            snapshot = DeviceSnapshot(
                ip=host,
                name=_optional_str(self.state.get("name")) or "PS5",
                device_id=device_id,
                device_type=_optional_str(self.state.get("device_type")) or "PS5",
                status=_optional_str(self.state.get("status")) or "standby",
                running_app_name=None,
                running_app_titleid=None,
            )
            self.state = _save_state(STATE_PATH, snapshot, pairing_mode=False)
            return snapshot
        return None

    def _discover_target(self, host: str | None, device_id: str | None) -> DeviceSnapshot | None:
        discovered = self._select_discovered(device_id=device_id, host=host)
        if discovered is not None:
            return discovered
        ps5_devices = [device for device in self.discovered_devices if device.device_type.upper() == "PS5"]
        if not ps5_devices:
            LOG.info("No PS5 discovered.")
            return None
        return ps5_devices[0]

    def _select_discovered(self, *, device_id: str | None, host: str | None) -> DeviceSnapshot | None:
        ps5_devices = [device for device in self.discovered_devices if device.device_type.upper() == "PS5"]
        if device_id:
            expected = device_id.casefold()
            for device in ps5_devices:
                if device.device_id.casefold() == expected:
                    return device
        if host:
            for device in ps5_devices:
                if device.ip == host:
                    return device
        return None

    def _mqtt_done(self, task: asyncio.Task[None]) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            LOG.exception("MQTT bridge stopped unexpectedly.", exc_info=exc)
            self.error = f"MQTT bridge stopped: {exc}"

    def _refresh_done(self, task: asyncio.Task[None]) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            LOG.debug("Background PS5 status refresh failed: %s", exc)


def main() -> None:
    options = _load_options(OPTIONS_PATH)
    _configure_logging(str(options.get("log_level") or "info"))
    asyncio.run(_run(options))


async def _run(options: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_DIR.mkdir(parents=True, exist_ok=True)

    runtime = AddonRuntime(options)
    await runtime.initialize()
    LOG.info("PS5 HA Bridge Web UI listening on port %s.", WEB_PORT)
    await run_web(runtime)


def _build_config(options: dict[str, Any], snapshot: DeviceSnapshot) -> AppConfig:
    mqtt_options = _mapping(options.get("mqtt"))
    bridge_options = _mapping(options.get("bridge"))
    service_mqtt = _load_mqtt_service_config()
    username = _optional_str(mqtt_options.get("username")) or _optional_str(service_mqtt.get("username"))
    password = _optional_str(mqtt_options.get("password")) or _optional_str(service_mqtt.get("password"))

    return AppConfig(
        ps5=Ps5Config(
            host=snapshot.ip,
            device_id=snapshot.device_id,
            name=snapshot.name or "PS5",
        ),
        mqtt=MqttConfig(
            host=str(mqtt_options.get("host") or service_mqtt.get("host") or "core-mosquitto"),
            port=int(mqtt_options.get("port") or service_mqtt.get("port") or 1883),
            username=username,
            password=password,
            discovery_prefix=str(mqtt_options.get("discovery_prefix") or "homeassistant"),
            base_topic=str(mqtt_options.get("base_topic") or "ps5-ha-bridge/ps5"),
            client_id=str(mqtt_options.get("client_id") or "ps5-ha-bridge"),
        ),
        bridge=BridgeConfig(
            poll_interval_seconds=int(bridge_options.get("poll_interval_seconds") or 30),
            availability_failures=int(bridge_options.get("availability_failures") or 3),
            command_transition_timeout_seconds=int(
                bridge_options.get("command_transition_timeout_seconds") or 60
            ),
            command_transition_poll_seconds=int(
                bridge_options.get("command_transition_poll_seconds") or 1
            ),
            actual_state_confirmations=int(bridge_options.get("actual_state_confirmations") or 3),
            discovery_name=str(bridge_options.get("discovery_name") or "PS5"),
            credential_storage_dir=CREDENTIAL_DIR,
            state_path=STATE_PATH,
        ),
    )


def _load_mqtt_service_config() -> dict[str, Any]:
    token = os.environ.get("SUPERVISOR_TOKEN")
    if not token:
        LOG.debug("SUPERVISOR_TOKEN is not set. MQTT service credentials are unavailable.")
        return {}
    request = Request(
        "http://supervisor/services/mqtt",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        LOG.warning("Could not read Supervisor MQTT service config: %s", exc)
        return {}
    data = payload.get("data")
    if not isinstance(data, dict):
        LOG.warning("Supervisor MQTT service response did not contain a data object.")
        return {}
    LOG.debug("Loaded MQTT service config from Supervisor.")
    return data


def _load_options(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"options root must be a mapping: {path}")
    return data


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        LOG.warning("Ignoring invalid state file: %s", path)
        return {}
    if not isinstance(data, dict):
        LOG.warning("Ignoring non-object state file: %s", path)
        return {}
    return data


def _save_state(path: Path, snapshot: DeviceSnapshot, *, pairing_mode: bool | None = None) -> dict[str, Any]:
    data = {
        "host": snapshot.ip,
        "device_id": snapshot.device_id,
        "name": snapshot.name,
        "device_type": snapshot.device_type,
        "status": snapshot.status,
    }
    if pairing_mode is not None:
        data["pairing_mode"] = pairing_mode
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    LOG.debug("Saved PS5 state: %s", json.dumps(asdict(snapshot), sort_keys=True))
    return data


def _save_pairing_mode(path: Path, state: dict[str, Any], pairing_mode: bool) -> dict[str, Any]:
    data = dict(state)
    data["pairing_mode"] = pairing_mode
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def _configure_logging(level: str) -> None:
    normalized = level.upper()
    numeric_level = getattr(logging, normalized, logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


if __name__ == "__main__":
    main()
