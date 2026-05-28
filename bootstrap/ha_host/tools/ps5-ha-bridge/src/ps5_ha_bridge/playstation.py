from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from playdirector import find, scan, standby, wake
from playdirector.credentials import JsonCredentialStorage
from playdirector.discovery import DeviceStatus, DeviceType, DiscoveredDevice
from playdirector.pairing import pair_ps5


@dataclass(frozen=True)
class DeviceSnapshot:
    ip: str
    name: str
    device_id: str
    device_type: str
    status: str
    running_app_name: str | None
    running_app_titleid: str | None


class PlayStationClient:
    def __init__(self, credential_storage_dir: Path) -> None:
        self._credential_storage_dir = credential_storage_dir.expanduser()
        self._credential_storage_dir.mkdir(parents=True, exist_ok=True)
        self._storage = JsonCredentialStorage(self._credential_storage_dir)

    async def discover(self, timeout: float = 5.0) -> list[DeviceSnapshot]:
        devices: list[DeviceSnapshot] = []
        async for device in scan(timeout=timeout):
            devices.append(_snapshot(device))
        return devices

    async def status(self, host: str, timeout: float = 5.0) -> DeviceSnapshot | None:
        device = await find(host, timeout=timeout)
        if device is None:
            return None
        return _snapshot(device)

    async def status_by_device_id(
        self,
        device_id: str,
        *,
        fallback_host: str | None = None,
        timeout: float = 8.0,
    ) -> DeviceSnapshot | None:
        device = await self._find_by_device_id(device_id, timeout=timeout)
        if device is not None:
            return _snapshot(device)
        if fallback_host:
            return await self.status(fallback_host, timeout=5.0)
        return None

    async def pair(self, host: str, pin: str, npsso: str, timeout: float = 30.0) -> DeviceSnapshot:
        device = await self._find_by_host(host, timeout=8.0)
        if device is None:
            raise RuntimeError(f"No device found at {host} - check the IP and network.")
        if device.device_type != DeviceType.PS5:
            raise RuntimeError(f"Unsupported PlayStation device type: {_enum_value(device.device_type)}")
        credential = await pair_ps5(device, pin=pin, npsso=npsso)
        self._storage.save(credential)
        device = await self._find_by_host(host, timeout=5.0)
        if device is None:
            return DeviceSnapshot(
                ip=host,
                name="PS5",
                device_id=str(credential.device_id),
                device_type="PS5",
                status="UNKNOWN",
                running_app_name=None,
                running_app_titleid=None,
            )
        return _snapshot(device)

    async def wake(
        self,
        host: str,
        device_id: str | None = None,
        *,
        wait_seconds: float = 30.0,
    ) -> DeviceSnapshot:
        device = await find(host, timeout=5.0)
        credential = self._require_credential(device_id or (str(device.device_id) if device else None))
        if device is None:
            device = _wake_target(host, credential.device_id)
        await wake(device, credential)

        deadline = asyncio.get_running_loop().time() + wait_seconds
        last_snapshot = _snapshot(device)
        while asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(2)
            refreshed = await find(host, timeout=3.0)
            if refreshed is None:
                continue
            last_snapshot = _snapshot(refreshed)
            if refreshed.status == DeviceStatus.AWAKE:
                return last_snapshot
        return last_snapshot

    async def standby(self, host: str, device_id: str | None = None) -> DeviceSnapshot:
        device = await self._require_device(host, device_id)
        credential = self._require_credential(device_id or str(device.device_id))
        await standby(device, credential)
        return _snapshot(device)

    def has_credential(self, device_id: str) -> bool:
        return self._storage.load(device_id) is not None

    def _require_credential(self, device_id: str | None) -> Any:
        if device_id is None:
            device_ids = self._storage.list_device_ids()
            if len(device_ids) == 1:
                device_id = device_ids[0]
            else:
                raise RuntimeError(
                    "missing credential device id. Set ps5.device_id or pass --device-id."
                )
        credential = self._storage.load(device_id)
        if credential is None:
            raise RuntimeError(
                f"missing credential for device {device_id}. Run `ps5-ha-bridge pair` first."
            )
        return credential

    async def _find_by_device_id(self, device_id: str, *, timeout: float = 8.0) -> Any | None:
        expected = device_id.casefold()
        async for device in scan(timeout=timeout):
            if str(device.device_id).casefold() == expected:
                return device
        return None

    async def _find_by_host(self, host: str, *, timeout: float = 8.0) -> Any | None:
        async for device in scan(timeout=timeout):
            if str(device.ip) == host:
                return device
        device = await find(host, timeout=5.0)
        if device is not None:
            return device
        return None

    async def _require_device(self, host: str, device_id: str | None) -> Any:
        if device_id:
            device = await self._find_by_device_id(device_id, timeout=8.0)
            if device is not None:
                return device
        device = await find(host, timeout=5.0)
        if device is None:
            target = device_id or host
            raise RuntimeError(f"PlayStation not found: {target}")
        return device

def _snapshot(device: Any) -> DeviceSnapshot:
    return DeviceSnapshot(
        ip=str(device.ip),
        name=str(device.name),
        device_id=str(device.device_id),
        device_type=_enum_value(device.device_type),
        status=_enum_value(device.status),
        running_app_name=getattr(device, "running_app_name", None),
        running_app_titleid=getattr(device, "running_app_titleid", None),
    )


def _wake_target(host: str, device_id: str) -> DiscoveredDevice:
    return DiscoveredDevice(
        ip=host,
        port=9302,
        device_id=device_id,
        name="PS5",
        status=DeviceStatus.STANDBY,
        device_type=DeviceType.PS5,
        system_version="",
    )


def _enum_value(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)
