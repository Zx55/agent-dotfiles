"""MCP stdio line-based message helpers."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from typing import BinaryIO


class FrameError(Exception):
    """Raised when an MCP stdio message is malformed."""


@dataclass(frozen=True)
class Frame:
    """A single MCP stdio JSON line message."""

    raw: bytes
    body: bytes

    def parse_json(self) -> dict | list | None:
        """Parse the frame body as JSON when possible."""
        try:
            return json.loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

def read_frame(stream: BinaryIO) -> Frame:
    """Read a single newline-delimited JSON message from *stream*."""
    line = stream.readline()
    if line == b"":
        raise EOFError
    if not line.endswith(b"\n"):
        raise FrameError("Incomplete JSON line message")

    body = line.rstrip(b"\r\n")
    if not body:
        raise FrameError("Empty JSON line message")

    return Frame(raw=line, body=body)


def write_frame(stream: BinaryIO, body: bytes) -> None:
    """Write a newline-delimited JSON message with *body* to *stream*."""
    stream.write(body + b"\n")
    stream.flush()


def encode_json_frame(message: dict) -> bytes:
    """Encode a JSON message into a newline-delimited JSON message."""
    buffer = io.BytesIO()
    write_frame(buffer, json.dumps(message).encode("utf-8"))
    return buffer.getvalue()
