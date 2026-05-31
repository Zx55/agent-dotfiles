from __future__ import annotations

import argparse

from .common import add_host_options, host_options
from ha_host_orchestrator.host import check, watch


def main() -> int:
    parser = argparse.ArgumentParser(description="HA host root watch entrypoint.")
    parser.add_argument("--check-only", action="store_true")
    add_host_options(parser, watch=True)
    args = parser.parse_args()
    options = host_options(args)
    if args.check_only:
        return check(options)
    return watch(options)


if __name__ == "__main__":
    raise SystemExit(main())

