from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import os

import yaml


DEFAULT_CONFIG_PATH = Path("~/.config/ps5-ha-bridge/config.yaml").expanduser()
DEFAULT_CREDENTIAL_DIR = Path("~/.config/ps5-ha-bridge/credentials").expanduser()


@dataclass(frozen=True)
class Ps5Config:
    host: str | None = None
    device_id: str | None = None
    name: str = "PS5"


@dataclass(frozen=True)
class MqttConfig:
    host: str = "localhost"
    port: int = 1883
    username: str | None = None
    password: str | None = None
    discovery_prefix: str = "homeassistant"
    base_topic: str = "ps5-ha-bridge/ps5"
    client_id: str = "ps5-ha-bridge"


@dataclass(frozen=True)
class BridgeConfig:
    poll_interval_seconds: int = 30
    availability_failures: int = 3
    command_transition_timeout_seconds: int = 60
    command_transition_poll_seconds: int = 1
    actual_state_confirmations: int = 3
    discovery_name: str = "PS5"
    credential_storage_dir: Path = DEFAULT_CREDENTIAL_DIR
    state_path: Path | None = None


@dataclass(frozen=True)
class AppConfig:
    ps5: Ps5Config = field(default_factory=Ps5Config)
    mqtt: MqttConfig = field(default_factory=MqttConfig)
    bridge: BridgeConfig = field(default_factory=BridgeConfig)


def load_config(path: Path | None) -> AppConfig:
    if path is None:
        path = DEFAULT_CONFIG_PATH
    path = path.expanduser()
    if not path.exists():
        return AppConfig()

    raw = _load_mapping(path)
    return AppConfig(
        ps5=Ps5Config(
            host=_optional_str(raw.get("ps5", {}).get("host")),
            device_id=_optional_str(raw.get("ps5", {}).get("device_id")),
            name=str(raw.get("ps5", {}).get("name", "PS5")),
        ),
        mqtt=MqttConfig(
            host=str(raw.get("mqtt", {}).get("host", "localhost")),
            port=int(raw.get("mqtt", {}).get("port", 1883)),
            username=_resolve_secret(raw.get("mqtt", {}).get("username")),
            password=_resolve_secret(raw.get("mqtt", {}).get("password")),
            discovery_prefix=str(raw.get("mqtt", {}).get("discovery_prefix", "homeassistant")),
            base_topic=str(raw.get("mqtt", {}).get("base_topic", "ps5-ha-bridge/ps5")),
            client_id=str(raw.get("mqtt", {}).get("client_id", "ps5-ha-bridge")),
        ),
        bridge=BridgeConfig(
            poll_interval_seconds=int(raw.get("bridge", {}).get("poll_interval_seconds", 30)),
            availability_failures=int(raw.get("bridge", {}).get("availability_failures", 3)),
            command_transition_timeout_seconds=int(
                raw.get("bridge", {}).get("command_transition_timeout_seconds", 60)
            ),
            command_transition_poll_seconds=int(
                raw.get("bridge", {}).get("command_transition_poll_seconds", 1)
            ),
            actual_state_confirmations=int(raw.get("bridge", {}).get("actual_state_confirmations", 3)),
            discovery_name=str(raw.get("bridge", {}).get("discovery_name", "PS5")),
            credential_storage_dir=Path(
                str(raw.get("bridge", {}).get("credential_storage_dir", DEFAULT_CREDENTIAL_DIR))
            ).expanduser(),
            state_path=(
                Path(str(raw.get("bridge", {}).get("state_path"))).expanduser()
                if raw.get("bridge", {}).get("state_path")
                else None
            ),
        ),
    )


def write_example_config(path: Path, *, overwrite: bool = False) -> None:
    path = path.expanduser()
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """ps5:
  host: <ps5-ip>
  # Optional. If omitted, the bridge uses the device id returned by discovery.
  device_id:
  name: PS5

mqtt:
  host: <mqtt-broker-host>
  port: 1883
  # Use env:VAR_NAME to keep secrets out of this file.
  username:
  password:
  discovery_prefix: homeassistant
  base_topic: ps5-ha-bridge/ps5
  client_id: ps5-ha-bridge

bridge:
  poll_interval_seconds: 30
  availability_failures: 3
  command_transition_timeout_seconds: 60
  command_transition_poll_seconds: 1
  actual_state_confirmations: 3
  discovery_name: PS5
  credential_storage_dir: ~/.config/ps5-ha-bridge/credentials
  state_path: ~/.config/ps5-ha-bridge/state.json
""",
        encoding="utf-8",
    )


def _load_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"config root must be a mapping: {path}")
    return data


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _resolve_secret(value: object) -> str | None:
    text = _optional_str(value)
    if text is None:
        return None
    if text.startswith("env:"):
        env_name = text[4:]
        resolved = os.environ.get(env_name)
        if not resolved:
            raise ValueError(f"environment variable is not set: {env_name}")
        return resolved
    return text
