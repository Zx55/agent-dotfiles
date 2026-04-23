from __future__ import annotations

import unittest
from unittest import mock

from zotero_mcp_wrapper.config import Config
from zotero_mcp_wrapper.zotero_runtime import ZoteroLaunchError, ZoteroRuntime


class ZoteroRuntimeTests(unittest.TestCase):
    def _config(self) -> Config:
        return Config(
            child_command=("zotero-mcp", "serve"),
            app_path="/Applications/Zotero.app",
            host="127.0.0.1",
            port=23119,
            startup_timeout_sec=0.5,
            connect_timeout_sec=0.1,
            auto_launch=True,
            stable_polls=1,
        )

    @mock.patch("zotero_mcp_wrapper.zotero_runtime.socket.create_connection")
    def test_is_ready_true_when_socket_connects(self, create_connection: mock.Mock) -> None:
        runtime = ZoteroRuntime(self._config())
        create_connection.return_value.__enter__.return_value = object()
        self.assertTrue(runtime.is_ready())

    @mock.patch("zotero_mcp_wrapper.zotero_runtime.socket.create_connection", side_effect=OSError)
    def test_is_ready_false_when_socket_fails(self, _: mock.Mock) -> None:
        runtime = ZoteroRuntime(self._config())
        self.assertFalse(runtime.is_ready())

    @mock.patch("zotero_mcp_wrapper.zotero_runtime.subprocess.run")
    def test_launch_raises_when_all_commands_fail(self, run: mock.Mock) -> None:
        run.return_value.returncode = 1
        runtime = ZoteroRuntime(self._config())
        with self.assertRaises(ZoteroLaunchError):
            runtime.launch()


if __name__ == "__main__":
    unittest.main()
