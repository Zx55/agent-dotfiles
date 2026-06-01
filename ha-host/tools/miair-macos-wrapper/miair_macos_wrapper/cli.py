"""CLI entrypoint for miair-macos-wrapper."""

from __future__ import annotations

import os
import sys

from miair_macos_wrapper.mdns import install_macos_mdns_adapter, is_ipv4_address


def configured_hostname(argv: list[str]) -> str:
    """Return the configured --hostname value from MiAir CLI arguments."""
    for index, arg in enumerate(argv):
        if arg == "--hostname" and index + 1 < len(argv):
            return argv[index + 1]
        if arg.startswith("--hostname="):
            return arg.split("=", 1)[1]
    return ""


def export_hostname_env(argv: list[str]) -> None:
    """Expose MiAir's explicit hostname to upstream code paths that read env."""
    hostname = configured_hostname(argv)
    if hostname and is_ipv4_address(hostname):
        os.environ["MIAIR_HOSTNAME"] = hostname


def main() -> int:
    """Install macOS runtime adapters and run MiAir."""
    export_hostname_env(sys.argv[1:])
    install_macos_mdns_adapter()

    from miair.cli import main as miair_main

    result = miair_main()
    return int(result or 0)


if __name__ == "__main__":
    raise SystemExit(main())
