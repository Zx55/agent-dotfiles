"""Child process management for the wrapped zotero-mcp server."""

from __future__ import annotations

import subprocess
from typing import BinaryIO

from zotero_mcp_wrapper.config import Config


class ChildProcess:
    """Own the wrapped zotero-mcp child process."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._process: subprocess.Popen[bytes] | None = None

    def start(self) -> None:
        """Start the child process."""
        if self._process is not None:
            return

        self._process = subprocess.Popen(
            self._config.child_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @property
    def stdin(self) -> BinaryIO:
        assert self._process is not None and self._process.stdin is not None
        return self._process.stdin

    @property
    def stdout(self) -> BinaryIO:
        assert self._process is not None and self._process.stdout is not None
        return self._process.stdout

    @property
    def stderr(self) -> BinaryIO:
        assert self._process is not None and self._process.stderr is not None
        return self._process.stderr

    @property
    def returncode(self) -> int | None:
        if self._process is None:
            return None
        return self._process.poll()

    def terminate(self) -> None:
        """Terminate the child process."""
        if self._process is None:
            return
        if self._process.poll() is None:
            self._process.terminate()

    def wait(self) -> int:
        """Wait for the child process to exit."""
        assert self._process is not None
        return self._process.wait()

