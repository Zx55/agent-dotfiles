#!/usr/bin/env python3
"""Deny Cursor reads of local secret files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


SECRET_FILENAMES = {
    ".secret",
    "secret.local",
}
SECRET_SUFFIXES = (
    ".env",
    ".local",
    ".secret",
)
SECRET_NAME_PREFIXES = (
    ".env.",
    ".local.",
    ".secret.",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deny reads of local secret files.")
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Cursor hook-compatible JSON on stdout.",
    )
    return parser.parse_args()


def read_hook_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def file_path_from_input(hook_input: dict[str, Any]) -> Path | None:
    raw_path = hook_input.get("file_path")
    if not isinstance(raw_path, str) or not raw_path:
        return None
    return Path(raw_path).expanduser()


def is_secret_file(path: Path) -> bool:
    name = path.name
    if name in SECRET_FILENAMES:
        return True
    if name.startswith(SECRET_NAME_PREFIXES):
        return True
    if name.endswith(SECRET_SUFFIXES):
        return True

    parts = set(path.parts)
    return "dotfiles" in parts and "secrets" in parts


def deny_payload(path: Path) -> dict[str, str]:
    return {
        "permission": "deny",
        "user_message": (
            "Secret file read blocked by Cursor Secret Guard: "
            f"{path}. Use a non-secret fixture or ask the user for a redacted value."
        ),
    }


def main() -> int:
    parse_args()
    hook_input = read_hook_input()
    path = file_path_from_input(hook_input)

    if path is not None and is_secret_file(path):
        print(json.dumps(deny_payload(path), ensure_ascii=False))
    else:
        print('{"permission":"allow"}')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
