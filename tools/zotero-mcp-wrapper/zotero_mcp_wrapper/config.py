"""Configuration loading for zotero-mcp-wrapper."""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass


DEFAULT_ZOTERO_MCP_BIN = "/Users/chenzeren/.local/bin/zotero-mcp"
DEFAULT_ZOTERO_MCP_ARGS = "serve"
DEFAULT_ZOTERO_APP_PATH = "/Applications/Zotero.app"
DEFAULT_ZOTERO_HOST = "127.0.0.1"
DEFAULT_ZOTERO_PORT = 23119
DEFAULT_STARTUP_TIMEOUT_SEC = 30.0
DEFAULT_CONNECT_TIMEOUT_SEC = 0.25
DEFAULT_STABLE_POLLS = 2


@dataclass(frozen=True)
class Config:
    """Runtime configuration for the wrapper."""

    child_command: tuple[str, ...]
    app_path: str
    host: str
    port: int
    startup_timeout_sec: float
    connect_timeout_sec: float
    auto_launch: bool
    stable_polls: int


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    return int(raw.strip())


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    return float(raw.strip())


def load_config() -> Config:
    """Load wrapper configuration from environment variables."""
    child_bin = os.getenv("ZOTERO_MCP_BIN", DEFAULT_ZOTERO_MCP_BIN).strip()
    child_args = shlex.split(os.getenv("ZOTERO_MCP_ARGS", DEFAULT_ZOTERO_MCP_ARGS))
    return Config(
        child_command=(child_bin, *child_args),
        app_path=os.getenv("ZOTERO_APP_PATH", DEFAULT_ZOTERO_APP_PATH).strip(),
        host=os.getenv("ZOTERO_LOCAL_HOST", DEFAULT_ZOTERO_HOST).strip(),
        port=_env_int("ZOTERO_LOCAL_PORT", DEFAULT_ZOTERO_PORT),
        startup_timeout_sec=_env_float("ZOTERO_STARTUP_TIMEOUT_SEC", DEFAULT_STARTUP_TIMEOUT_SEC),
        connect_timeout_sec=_env_float("ZOTERO_CONNECT_TIMEOUT_SEC", DEFAULT_CONNECT_TIMEOUT_SEC),
        auto_launch=_env_flag("ZOTERO_AUTO_LAUNCH", True),
        stable_polls=_env_int("ZOTERO_READY_STABLE_POLLS", DEFAULT_STABLE_POLLS),
    )

