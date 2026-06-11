from __future__ import annotations

import argparse
import os
from pathlib import Path

from .common import add_haos_options
from ha_host_orchestrator.haos import watch


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value == "1"


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def main() -> int:
    parser = argparse.ArgumentParser(description="HAOS user watch entrypoint.")
    parser.add_argument("--vm-name", default="HAOS-17.3")
    parser.add_argument("--host-alias", default="haos")
    parser.add_argument("--haos-interface", default="default")
    parser.add_argument("--guest-device", default="enp0s1")
    parser.add_argument("--apply-gateway", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--apply-bridge", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--apply-vm-restart", action=argparse.BooleanOptionalAction, default=env_bool("HA_WATCH_APPLY_VM_RESTART", True))
    parser.add_argument("--allow-utm-app-restart", action=argparse.BooleanOptionalAction, default=env_bool("HA_WATCH_ALLOW_UTM_APP_RESTART", False))
    parser.add_argument("--restart-after-failures", type=int, default=env_int("HA_WATCH_RESTART_AFTER_FAILURES", 3))
    parser.add_argument("--restart-cooldown-seconds", type=int, default=env_int("HA_WATCH_RESTART_COOLDOWN_SECONDS", 1800))
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
        apply_vm_restart=args.apply_vm_restart,
        allow_utm_app_restart=args.allow_utm_app_restart,
        restart_after_failures=args.restart_after_failures,
        restart_cooldown_seconds=args.restart_cooldown_seconds,
        utm_config_path=args.utm_config_path,
        state_path=args.state_path,
        wait_seconds=args.wait_seconds,
        sleep_seconds=args.sleep_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
