from __future__ import annotations

import io
import unittest

from zotero_mcp_wrapper.framing import FrameError, encode_json_frame, read_frame


class FramingTests(unittest.TestCase):
    def test_read_frame_round_trip(self) -> None:
        raw = encode_json_frame({"jsonrpc": "2.0", "id": 1, "method": "ping"})
        frame = read_frame(io.BytesIO(raw))
        self.assertEqual(frame.raw, raw)
        self.assertEqual(frame.parse_json(), {"jsonrpc": "2.0", "id": 1, "method": "ping"})

    def test_read_frame_requires_newline_terminated_message(self) -> None:
        with self.assertRaises(FrameError):
            read_frame(io.BytesIO(b'{"jsonrpc":"2.0"}'))

    def test_read_frame_rejects_empty_line(self) -> None:
        with self.assertRaises(FrameError):
            read_frame(io.BytesIO(b"\n"))


if __name__ == "__main__":
    unittest.main()
