"""Minimal stdio MCP child used for end-to-end wrapper tests."""

from __future__ import annotations

import json
import sys
from typing import BinaryIO


def read_frame(stream: BinaryIO) -> bytes:
    """Read a single newline-delimited JSON body from *stream*."""
    line = stream.readline()
    if line == b"":
        raise EOFError
    return line.rstrip(b"\r\n")


def write_message(message: dict) -> None:
    body = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(body + b"\n")
    sys.stdout.buffer.flush()


def main() -> int:
    """Run a tiny request/response MCP server."""
    while True:
        try:
            body = read_frame(sys.stdin.buffer)
        except EOFError:
            return 0

        payload = json.loads(body.decode("utf-8"))
        request_id = payload.get("id")
        method = payload.get("method")

        if request_id is None:
            continue

        if method == "initialize":
            write_message(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "serverInfo": {"name": "echo-mcp-server", "version": "0.1.0"},
                    },
                }
            )
            continue

        write_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "echoMethod": method,
                    "echoParams": payload.get("params"),
                },
            }
        )


if __name__ == "__main__":
    raise SystemExit(main())
