"""Runtime checks for Zotero Desktop local API availability."""

from __future__ import annotations

import socket
import subprocess
import time

from zotero_mcp_wrapper.config import Config


class ZoteroLaunchError(RuntimeError):
    """Raised when Zotero could not be made ready."""


class ZoteroRuntime:
    """Manage request-time readiness checks for Zotero Desktop."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def is_ready(self) -> bool:
        """Return whether the local Zotero API is reachable."""
        try:
            with socket.create_connection(
                (self._config.host, self._config.port),
                timeout=self._config.connect_timeout_sec,
            ):
                return True
        except OSError:
            return False

    def ensure_ready(self) -> None:
        """Ensure Zotero local API is available."""
        if self.is_ready():
            return

        if not self._config.auto_launch:
            raise ZoteroLaunchError("Zotero local API is unavailable and auto-launch is disabled.")

        self.launch()
        self.wait_until_ready()

    def launch(self) -> None:
        """Attempt to launch Zotero Desktop on macOS."""
        commands = []
        if self._config.app_path:
            commands.append(["open", "-gj", self._config.app_path])
        commands.append(["osascript", "-e", 'tell application "Zotero" to launch'])
        commands.append(["open", "-ga", "Zotero"])

        for command in commands:
            result = subprocess.run(command, capture_output=True, check=False)
            if result.returncode == 0:
                return

        raise ZoteroLaunchError("Unable to launch Zotero Desktop automatically.")

    def wait_until_ready(self) -> None:
        """Wait until Zotero local API becomes reachable."""
        deadline = time.monotonic() + self._config.startup_timeout_sec
        stable_hits = 0

        while time.monotonic() < deadline:
            if self.is_ready():
                stable_hits += 1
                if stable_hits >= self._config.stable_polls:
                    return
            else:
                stable_hits = 0
            time.sleep(0.25)

        raise ZoteroLaunchError(
            f"Zotero local API did not become ready at "
            f"{self._config.host}:{self._config.port} within "
            f"{self._config.startup_timeout_sec:.1f}s."
        )

