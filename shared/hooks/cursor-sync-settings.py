#!/usr/bin/env python3
"""Sync a portable Cursor settings snapshot from the local app config."""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any


def default_settings_path() -> Path:
    return Path("~/Library/Application Support/Cursor/User/settings.json").expanduser()


def path_patterns() -> list[str]:
    user = getpass.getuser()
    home = str(Path.home())
    return [
        home,
        f"/Users/{user}",
        f"/User/{user}",
        "/Users/$USER",
        "/User/$USER",
        "/Users/${USER}",
        "/User/${USER}",
    ]


def normalize_string(value: str) -> str:
    boundary = r'(?=/|["\']|\s|,|\]|\}|$)'
    normalized = value
    for prefix in dict.fromkeys(path_patterns()):
        normalized = re.sub(re.escape(prefix) + boundary, "~", normalized)
    return normalized


def normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        return normalize_string(value)
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    return value


def normalize_text(text: str) -> str:
    settings = json.loads(text)
    normalized = normalize_value(settings)
    return json.dumps(normalized, indent=2, ensure_ascii=False) + "\n"


def read_optional_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def write_atomic(path: Path, content: str) -> None:
    write_path = resolve_write_path(path)
    write_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=write_path.parent,
        delete=False,
    ) as handle:
        temp_name = handle.name
        handle.write(content)

    os.replace(temp_name, write_path)


def resolve_write_path(path: Path) -> Path:
    if path.is_symlink():
        return path.resolve(strict=False)
    return path


def emit_hook_output() -> None:
    print("{}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync a portable Cursor settings snapshot from local app config."
    )
    parser.add_argument(
        "--settings",
        type=Path,
        default=default_settings_path(),
        help="Local runtime Cursor settings.json path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Portable settings snapshot path.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when the snapshot would be changed.",
    )
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Cursor hook-compatible JSON on stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = args.settings.expanduser()
    output = args.output.expanduser()

    try:
        original = settings.read_text(encoding="utf-8")
        normalized = normalize_text(original)
    except FileNotFoundError:
        if args.hook_output:
            emit_hook_output()
            return 0
        print(f"settings not found: {settings}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        if args.hook_output:
            emit_hook_output()
            return 0
        print(f"settings are not valid JSON: {settings}: {exc}", file=sys.stderr)
        return 1

    previous_output = read_optional_text(output)
    changed = normalized != previous_output

    if args.check:
        if args.hook_output:
            emit_hook_output()
        elif changed:
            print(f"portable Cursor settings are out of sync: {output}", file=sys.stderr)
        return 1 if changed else 0

    if changed:
        write_atomic(output, normalized)

    if args.hook_output:
        emit_hook_output()
    elif changed:
        print(f"synced portable Cursor settings: {output}")
    else:
        print(f"portable Cursor settings already current: {output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
