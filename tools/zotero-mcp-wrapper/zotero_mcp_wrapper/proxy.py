"""Transparent stdio proxy for zotero-mcp."""

from __future__ import annotations

import sys
import threading
from typing import BinaryIO

from zotero_mcp_wrapper.child_process import ChildProcess
from zotero_mcp_wrapper.config import Config
from zotero_mcp_wrapper.framing import FrameError, encode_json_frame, read_frame
from zotero_mcp_wrapper.local_file_plugin import (
    LocalFilePluginError,
    call_add_from_file_plugin,
    is_add_from_file_tool_call,
)
from zotero_mcp_wrapper.types import JsonRpcRequest
from zotero_mcp_wrapper.zotero_runtime import ZoteroLaunchError, ZoteroRuntime

SKIP_METHODS = {"initialize", "ping"}


def _relay_stream(source: BinaryIO, destination: BinaryIO) -> None:
    while True:
        chunk = source.read1(65536) if hasattr(source, "read1") else source.read(65536)
        if not chunk:
            break
        destination.write(chunk)
        destination.flush()


def _extract_request(payload: object) -> JsonRpcRequest | None:
    if not isinstance(payload, dict):
        return None
    method = payload.get("method")
    if not isinstance(method, str):
        return None
    if "id" not in payload:
        return None
    return JsonRpcRequest(request_id=payload.get("id"), method=method)


def _request_needs_zotero(request: JsonRpcRequest) -> bool:
    return request.method not in SKIP_METHODS


class Proxy:
    """Run the request-aware stdio proxy."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._child = ChildProcess(config)
        self._zotero = ZoteroRuntime(config)

    def run(self) -> int:
        """Start the child process and proxy stdio traffic."""
        self._child.start()

        stdout_thread = threading.Thread(
            target=_relay_stream,
            args=(self._child.stdout, sys.stdout.buffer),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_relay_stream,
            args=(self._child.stderr, sys.stderr.buffer),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

        try:
            return self._proxy_client_requests()
        finally:
            self._child.terminate()

    def _proxy_client_requests(self) -> int:
        while True:
            try:
                frame = read_frame(sys.stdin.buffer)
            except EOFError:
                try:
                    self._child.stdin.close()
                except OSError:
                    pass
                return self._child.wait()
            except FrameError as error:
                print(f"Invalid MCP frame from client: {error}", file=sys.stderr)
                return 1

            payload = frame.parse_json()
            request = _extract_request(payload)

            if request is not None and _request_needs_zotero(request):
                try:
                    self._zotero.ensure_ready()
                except ZoteroLaunchError as error:
                    self._send_request_error(request, str(error))
                    continue

            if request is not None and is_add_from_file_tool_call(payload) and self._config.add_local_file_token:
                self._handle_local_add_from_file(request, payload)
                continue

            self._child.stdin.write(frame.raw)
            self._child.stdin.flush()

    def _send_request_error(self, request: JsonRpcRequest, message: str) -> None:
        payload = {
            "jsonrpc": "2.0",
            "id": request.request_id,
            "error": {
                "code": -32001,
                "message": message,
            },
        }
        sys.stdout.buffer.write(encode_json_frame(payload))
        sys.stdout.buffer.flush()

    def _handle_local_add_from_file(self, request: JsonRpcRequest, payload: object) -> None:
        assert isinstance(payload, dict)
        params = payload.get("params")
        arguments = params.get("arguments") if isinstance(params, dict) else None
        if not isinstance(arguments, dict):
            self._send_tool_result(request, "zotero_add_from_file arguments must be an object", is_error=True)
            return

        try:
            result = call_add_from_file_plugin(self._config, arguments)
        except LocalFilePluginError as error:
            self._send_tool_result(request, str(error), is_error=True)
            return

        self._send_tool_result(request, result.text, is_error=False)

    def _send_tool_result(self, request: JsonRpcRequest, text: str, *, is_error: bool) -> None:
        payload = {
            "jsonrpc": "2.0",
            "id": request.request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    }
                ],
            },
        }
        if is_error:
            payload["result"]["isError"] = True
        sys.stdout.buffer.write(encode_json_frame(payload))
        sys.stdout.buffer.flush()
