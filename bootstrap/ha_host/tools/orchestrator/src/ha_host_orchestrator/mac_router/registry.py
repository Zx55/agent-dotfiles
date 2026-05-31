from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def default_registry_path() -> Path:
    override = os.environ.get("MAC_ROUTER_REGISTRY")
    if override:
        return Path(override).expanduser()
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        return Path("/Users") / sudo_user / ".router" / "device.json"
    return Path.home() / ".router" / "device.json"


def empty_registry() -> dict[str, Any]:
    return {
        "version": 1,
        "defaults": {
            "lan_interface": "",
            "dns": "1.1.1.1",
        },
        "devices": {},
    }


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_registry()
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    data.setdefault("version", 1)
    data.setdefault("defaults", {})
    data.setdefault("devices", {})
    data["defaults"].setdefault("lan_interface", "")
    data["defaults"].setdefault("dns", "1.1.1.1")
    return data


def save_registry(path: Path, registry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(registry, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
