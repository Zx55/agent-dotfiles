from __future__ import annotations

import json
import os
import socket
import socketserver
import subprocess
import sys
import threading
import unittest
from pathlib import Path

from zotero_mcp_wrapper.framing import read_frame, write_frame


ROOT = Path(__file__).resolve().parent.parent
STUB_CHILD = ROOT / "tests" / "stubs" / "echo_mcp_server.py"


class _ReadyTcpHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        try:
            self.request.recv(16)
        except OSError:
            pass


class _ReadyServer:
    def __init__(self) -> None:
        self._server = socketserver.TCPServer(("127.0.0.1", 0), _ReadyTcpHandler)
        self.host, self.port = self._server.server_address
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self) -> "_ReadyServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=1)


class ProxyE2ETests(unittest.TestCase):
    def _start_wrapper(self, **env_overrides: str) -> subprocess.Popen[bytes]:
        env = os.environ.copy()
        env.update(
            {
                "ZOTERO_MCP_BIN": sys.executable,
                "ZOTERO_MCP_ARGS": str(STUB_CHILD),
                "ZOTERO_CONNECT_TIMEOUT_SEC": "0.05",
                "ZOTERO_STARTUP_TIMEOUT_SEC": "0.2",
                "ZOTERO_READY_STABLE_POLLS": "1",
                "ZOTERO_AUTO_LAUNCH": "false",
            }
        )
        env.update(env_overrides)
        return subprocess.Popen(
            [sys.executable, "-m", "zotero_mcp_wrapper.cli"],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    def _request(self, process: subprocess.Popen[bytes], payload: dict) -> dict:
        assert process.stdin is not None
        assert process.stdout is not None
        write_frame(process.stdin, json.dumps(payload).encode("utf-8"))
        frame = read_frame(process.stdout)
        parsed = frame.parse_json()
        assert isinstance(parsed, dict)
        return parsed

    def _stop_wrapper(self, process: subprocess.Popen[bytes]) -> None:
        if process.stdin is not None and not process.stdin.closed:
            process.stdin.close()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
        if process.stdout is not None and not process.stdout.closed:
            process.stdout.close()
        if process.stderr is not None and not process.stderr.closed:
            process.stderr.close()

    def test_tools_call_passes_through_when_zotero_ready(self) -> None:
        with _ReadyServer() as ready_server:
            process = self._start_wrapper(
                ZOTERO_LOCAL_HOST=ready_server.host,
                ZOTERO_LOCAL_PORT=str(ready_server.port),
            )
            try:
                response = self._request(
                    process,
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {"name": "search", "arguments": {"query": "SceneWeaver"}},
                    },
                )
                self.assertEqual(response["id"], 1)
                self.assertEqual(response["result"]["echoMethod"], "tools/call")
                self.assertEqual(
                    response["result"]["echoParams"],
                    {"name": "search", "arguments": {"query": "SceneWeaver"}},
                )
            finally:
                self._stop_wrapper(process)

    def test_tools_call_returns_wrapper_error_when_zotero_not_ready(self) -> None:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            host, port = probe.getsockname()

        process = self._start_wrapper(
            ZOTERO_LOCAL_HOST=host,
            ZOTERO_LOCAL_PORT=str(port),
        )
        try:
            response = self._request(
                process,
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": "search", "arguments": {"query": "Missing"}},
                },
            )
            self.assertEqual(response["id"], 2)
            self.assertIn("error", response)
            self.assertEqual(response["error"]["code"], -32001)
            self.assertIn("auto-launch is disabled", response["error"]["message"])
        finally:
            self._stop_wrapper(process)


if __name__ == "__main__":
    unittest.main()
