from __future__ import annotations

import unittest

from zotero_mcp_wrapper.proxy import _extract_request, _request_needs_zotero
from zotero_mcp_wrapper.types import JsonRpcRequest


class RequestClassifierTests(unittest.TestCase):
    def test_extract_request_ignores_notifications(self) -> None:
        payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        self.assertIsNone(_extract_request(payload))

    def test_extract_request_returns_request(self) -> None:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call"}
        request = _extract_request(payload)
        self.assertEqual(request, JsonRpcRequest(request_id=1, method="tools/call"))

    def test_initialize_does_not_require_zotero(self) -> None:
        request = JsonRpcRequest(request_id=1, method="initialize")
        self.assertFalse(_request_needs_zotero(request))

    def test_tools_call_requires_zotero(self) -> None:
        request = JsonRpcRequest(request_id=1, method="tools/call")
        self.assertTrue(_request_needs_zotero(request))


if __name__ == "__main__":
    unittest.main()
