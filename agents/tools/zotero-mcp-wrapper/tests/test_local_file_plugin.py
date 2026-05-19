from __future__ import annotations

import tempfile
import unittest
import os
from pathlib import Path

from zotero_mcp_wrapper.local_file_plugin import (
    LocalFilePluginError,
    build_plugin_request,
    is_add_from_file_tool_call,
)


class LocalFilePluginTests(unittest.TestCase):
    def test_detects_add_from_file_tool_call(self) -> None:
        self.assertTrue(
            is_add_from_file_tool_call(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "zotero_add_from_file", "arguments": {}},
                }
            )
        )

    def test_build_plugin_request_maps_mcp_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "paper.pdf"
            file_path.write_bytes(b"%PDF-1.7\n")

            request = build_plugin_request(
                {
                    "file_path": str(file_path),
                    "title": "Paper Title",
                    "item_type": "preprint",
                    "collections": ["ABC12345"],
                    "tags": ["survey", "multimodal"],
                }
            )

        self.assertEqual(request["filePath"], os.path.realpath(file_path))
        self.assertEqual(request["collectionKeys"], ["ABC12345"])
        self.assertEqual(request["attachmentTitle"], "paper.pdf")
        self.assertEqual(
            request["item"],
            {
                "itemType": "preprint",
                "title": "Paper Title",
                "tags": [{"tag": "survey"}, {"tag": "multimodal"}],
            },
        )

    def test_build_plugin_request_rejects_relative_path(self) -> None:
        with self.assertRaises(LocalFilePluginError):
            build_plugin_request({"file_path": "paper.pdf"})


if __name__ == "__main__":
    unittest.main()
