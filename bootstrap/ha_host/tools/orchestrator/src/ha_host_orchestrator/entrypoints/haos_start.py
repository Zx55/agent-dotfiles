from __future__ import annotations

import argparse

from .common import add_haos_options
from ha_host_orchestrator.haos import startup


def main() -> int:
    parser = argparse.ArgumentParser(description="HAOS user startup entrypoint.")
    parser.add_argument("--vm-name", default="HAOS-17.3")
    add_haos_options(parser)
    args = parser.parse_args()
    return startup(
        args.vm_name,
        state_path=args.state_path,
        wait_seconds=args.wait_seconds,
        sleep_seconds=args.sleep_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())

