"""Small internal types for the wrapper."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JsonRpcRequest:
    """A minimal JSON-RPC request view."""

    request_id: str | int | None
    method: str

