"""Minimal stdio MCP server for showing local images in Cursor."""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any, BinaryIO


PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "cursor-inline-img-loader"
SERVER_VERSION = "0.1.0"
DEFAULT_MAX_BYTES = 15 * 1024 * 1024

MIME_BY_SUFFIX = {
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

LOAD_IMAGE_TOOL = {
    "name": "load_image",
    "description": (
        "Return a local PNG/JPEG/GIF/WebP file as MCP ImageContent so Cursor can "
        "render it as a tool-result image. Prefer absolute paths."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or cwd-relative local image path.",
            },
            "cwd": {
                "type": "string",
                "description": "Optional base directory used when path is relative.",
            },
            "max_bytes": {
                "type": "integer",
                "minimum": 1,
                "description": "Optional maximum file size. Defaults to 15 MiB.",
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },
}


class ToolError(RuntimeError):
    """Raised when a tool call should return an MCP error result."""


def read_frame(stream: BinaryIO) -> bytes:
    """Read one newline-delimited JSON-RPC frame."""
    line = stream.readline()
    if line == b"":
        raise EOFError
    return line.rstrip(b"\r\n")


def write_message(message: dict[str, Any]) -> None:
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(body + b"\n")
    sys.stdout.buffer.flush()


def text_block(text: str) -> dict[str, str]:
    return {"type": "text", "text": text}


def error_result(message: str) -> dict[str, Any]:
    return {"content": [text_block(message)], "isError": True}


def resolve_image_path(raw_path: str, raw_cwd: str | None) -> Path:
    path = Path(os.path.expandvars(raw_path)).expanduser()
    if path.is_absolute():
        return path.resolve()

    base = Path(os.path.expandvars(raw_cwd)).expanduser() if raw_cwd else Path.cwd()
    return (base / path).resolve()


def load_image(arguments: dict[str, Any]) -> dict[str, Any]:
    raw_path = arguments.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ToolError("path must be a non-empty string.")

    raw_cwd = arguments.get("cwd")
    if raw_cwd is not None and not isinstance(raw_cwd, str):
        raise ToolError("cwd must be a string when provided.")

    raw_max_bytes = arguments.get("max_bytes", DEFAULT_MAX_BYTES)
    if not isinstance(raw_max_bytes, int) or raw_max_bytes <= 0:
        raise ToolError("max_bytes must be a positive integer.")

    image_path = resolve_image_path(raw_path, raw_cwd)
    if not image_path.exists():
        raise ToolError(f"Image file does not exist: {image_path}")
    if not image_path.is_file():
        raise ToolError(f"Image path is not a file: {image_path}")

    mime_type = MIME_BY_SUFFIX.get(image_path.suffix.lower())
    if mime_type is None:
        supported = ", ".join(sorted(MIME_BY_SUFFIX))
        raise ToolError(f"Unsupported image type {image_path.suffix!r}. Supported suffixes: {supported}")

    size = image_path.stat().st_size
    if size > raw_max_bytes:
        raise ToolError(f"Image is too large for inline loading: {size} bytes > {raw_max_bytes} bytes")

    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return {
        "content": [
            text_block(f"Loaded image for Cursor inline preview: {image_path} ({mime_type}, {size} bytes)"),
            {
                "type": "image",
                "data": data,
                "mimeType": mime_type,
                "annotations": {"audience": ["user"], "priority": 0.9},
            },
        ]
    }


def handle_request(payload: dict[str, Any]) -> dict[str, Any] | None:
    request_id = payload.get("id")
    method = payload.get("method")

    if request_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": [LOAD_IMAGE_TOOL]}}

    if method == "tools/call":
        params = payload.get("params")
        if not isinstance(params, dict):
            result = error_result("tools/call params must be an object.")
        elif params.get("name") != "load_image":
            result = error_result(f"Unknown tool: {params.get('name')!r}")
        else:
            arguments = params.get("arguments", {})
            if not isinstance(arguments, dict):
                result = error_result("Tool arguments must be an object.")
            else:
                try:
                    result = load_image(arguments)
                except ToolError as exc:
                    result = error_result(str(exc))
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def serve() -> int:
    while True:
        try:
            frame = read_frame(sys.stdin.buffer)
        except EOFError:
            return 0

        try:
            payload = json.loads(frame.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON-RPC payload must be an object.")
            response = handle_request(payload)
        except Exception as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Invalid request: {exc}"},
            }

        if response is not None:
            write_message(response)


def main() -> int:
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())
