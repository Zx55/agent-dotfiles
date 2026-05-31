from __future__ import annotations

import argparse
from pathlib import Path

from ha_host_orchestrator.host import HostOptions
from ha_host_orchestrator.mac_router.registry import default_registry_path


def add_host_options(parser: argparse.ArgumentParser, *, watch: bool = False) -> None:
    parser.add_argument("--registry", type=Path, default=default_registry_path(), help="Device registry JSON path.")
    parser.add_argument("--route-target", default="1.1.1.1", help="Egress route probe target.")
    parser.add_argument("--no-require-utun", action="store_true", help="Allow any egress route instead of requiring utun*.")
    parser.add_argument("--wait-seconds", type=int, default=60 if watch else 600)
    parser.add_argument("--sleep-seconds", type=int, default=5)
    parser.add_argument("--scan", action="store_true", help="Ping-sweep the selected LAN subnet before reading ARP.")
    parser.add_argument("--subnet", help="Subnet to scan, default inferred as selected interface /24.")
    parser.add_argument("--timeout-ms", type=int, default=1000)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--state-path", type=Path)


def host_options(args: argparse.Namespace) -> HostOptions:
    return HostOptions(
        registry=args.registry,
        route_target=args.route_target,
        require_utun=not args.no_require_utun,
        wait_seconds=args.wait_seconds,
        sleep_seconds=args.sleep_seconds,
        scan=args.scan,
        subnet=args.subnet,
        timeout_ms=args.timeout_ms,
        workers=args.workers,
        state_path=args.state_path,
    )


def add_haos_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--state-path", type=Path)
    parser.add_argument("--wait-seconds", type=int, default=180)
    parser.add_argument("--sleep-seconds", type=int, default=5)

