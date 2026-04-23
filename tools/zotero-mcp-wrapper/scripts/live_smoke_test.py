#!/usr/bin/env python3
"""Minimal live smoke test for the packaged zotero-mcp-wrapper binary."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BINARY = ROOT / "dist" / "zotero-mcp-wrapper"


def _write_message(stream, payload: dict) -> None:
    stream.write(json.dumps(payload).encode("utf-8") + b"\n")
    stream.flush()


def _read_message(stream) -> dict:
    line = stream.readline()
    if not line:
        raise RuntimeError("Wrapper exited before returning a response.")
    return json.loads(line.decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default=str(DEFAULT_BINARY))
    parser.add_argument("--query", default="SceneWeaver")
    args = parser.parse_args()

    env = os.environ.copy()
    env.setdefault("ZOTERO_MCP_BIN", "/Users/chenzeren/.local/bin/zotero-mcp")
    env.setdefault("ZOTERO_MCP_ARGS", "serve")
    env.setdefault("ZOTERO_LOCAL", "true")
    env.setdefault("ZOTERO_EMBEDDING_MODEL", "default")

    process = subprocess.Popen(
        [args.binary],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    try:
        assert process.stdin is not None
        assert process.stdout is not None

        _write_message(
            process.stdin,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "smoke-test", "version": "0.1.0"},
                },
            },
        )
        initialize = _read_message(process.stdout)
        print(json.dumps({"initialize": initialize}, ensure_ascii=False, indent=2))

        _write_message(
            process.stdin,
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
        )

        _write_message(
            process.stdin,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "zotero_search_items",
                    "arguments": {"query": args.query},
                },
            },
        )
        result = _read_message(process.stdout)
        print(json.dumps({"tools_call": result}, ensure_ascii=False, indent=2))
        return 0
    finally:
        if process.stdin is not None and not process.stdin.closed:
            process.stdin.close()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
        if process.stderr is not None:
            stderr = process.stderr.read().decode("utf-8", errors="replace").strip()
            if stderr:
                print(stderr, file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
