from __future__ import annotations

import argparse
from pathlib import Path

from .common import add_haos_options
from ha_host_orchestrator.haos import watch


def main() -> int:
    parser = argparse.ArgumentParser(description="HAOS user watch entrypoint.")
    parser.add_argument("--vm-name", default="HAOS-17.3")
    parser.add_argument("--host-alias", default="haos")
    parser.add_argument("--haos-interface", default="default")
    parser.add_argument("--guest-device", default="enp0s1")
    parser.add_argument("--apply-gateway", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--apply-bridge", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--force-bridge-restart", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--utm-config-path", type=Path)
    add_haos_options(parser)
    args = parser.parse_args()
    return watch(
        vm_name=args.vm_name,
        host_alias=args.host_alias,
        haos_interface=args.haos_interface,
        guest_device=args.guest_device,
        apply_gateway=args.apply_gateway,
        apply_bridge=args.apply_bridge,
        force_bridge_restart=args.force_bridge_restart,
        utm_config_path=args.utm_config_path,
        state_path=args.state_path,
        wait_seconds=args.wait_seconds,
        sleep_seconds=args.sleep_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
