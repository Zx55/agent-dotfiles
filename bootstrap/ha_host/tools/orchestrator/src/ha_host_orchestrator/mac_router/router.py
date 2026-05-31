from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Sequence


def tool_dir() -> Path:
    return Path(__file__).resolve().parent


def router_script_path() -> Path:
    return tool_dir() / "mac-router.sh"


def router_args(
    command: str,
    targets: Sequence[str],
    *,
    lan_interface: str,
    mac_lan_ip: str,
    dns: str,
    egress_interface: str,
    replace_targets: bool,
    yes: bool,
) -> list[str]:
    args = [str(router_script_path()), command]
    if command == "apply" and replace_targets:
        args.append("--replace-targets")
    for target in targets:
        args.extend(["--target-ip", target])
    args.extend(["--lan-interface", lan_interface])
    args.extend(["--mac-lan-ip", mac_lan_ip])
    args.extend(["--dns", dns])
    if egress_interface:
        args.extend(["--egress-interface", egress_interface])
    if yes:
        args.append("--yes")
    return args


def run_router(args: list[str], *, sudo: bool) -> int:
    command = ["sudo", *args] if sudo and os.geteuid() != 0 else args
    print("+ " + " ".join(command), flush=True)
    proc = subprocess.run(command, check=False)
    return proc.returncode
