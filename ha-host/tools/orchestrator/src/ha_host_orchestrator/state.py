from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .network import HostNetwork


@dataclass(frozen=True)
class HostState:
    version: int
    updated_at: float
    lan_interface: str
    lan_ip: str
    lan_hardware_port: str
    lan_kind: str
    egress_interface: str
    route_target: str
    registry_path: str
    target_ips: list[str]


def ha_host_home() -> Path:
    override = os.environ.get("HA_HOST_HOME")
    if override:
        return Path(override).expanduser()
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        return Path("/Users") / sudo_user / ".ha_host"
    return Path.home() / ".ha_host"


def default_state_path() -> Path:
    return ha_host_home() / "state.json"


def host_state_from_network(
    network: HostNetwork,
    *,
    registry_path: Path,
    target_ips: list[str],
) -> HostState:
    return HostState(
        version=1,
        updated_at=time.time(),
        lan_interface=network.lan.interface,
        lan_ip=network.lan.ip,
        lan_hardware_port=network.lan.hardware_port,
        lan_kind=network.lan.kind,
        egress_interface=network.egress_interface,
        route_target=network.route_target,
        registry_path=str(registry_path),
        target_ips=target_ips,
    )


def read_state(path: Path | None = None) -> HostState | None:
    state_path = path or default_state_path()
    if not state_path.exists():
        return None
    with state_path.open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    return HostState(
        version=int(data["version"]),
        updated_at=float(data["updated_at"]),
        lan_interface=str(data["lan_interface"]),
        lan_ip=str(data["lan_ip"]),
        lan_hardware_port=str(data["lan_hardware_port"]),
        lan_kind=str(data["lan_kind"]),
        egress_interface=str(data["egress_interface"]),
        route_target=str(data["route_target"]),
        registry_path=str(data["registry_path"]),
        target_ips=[str(item) for item in data.get("target_ips", [])],
    )


def write_state(state: HostState, path: Path | None = None) -> Path:
    state_path = path or default_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(asdict(state), handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(state_path)
    return state_path


def state_matches_network(state: HostState, network: HostNetwork) -> bool:
    return (
        state.lan_interface == network.lan.interface
        and state.lan_ip == network.lan.ip
        and state.egress_interface == network.egress_interface
        and state.route_target == network.route_target
    )
