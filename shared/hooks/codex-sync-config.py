#!/usr/bin/env python3
"""Sync a portable Codex config snapshot from the local runtime config."""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def default_config_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "config.toml"
    return Path("~/.codex/config.toml").expanduser()


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


def normalize_text(text: str) -> str:
    boundary = r'(?=/|["\']|\s|,|\]|\}|$)'
    output: list[str] = []
    skipping_local_state = False

    for line in text.splitlines(keepends=True):
        if is_single_table_header(line):
            skipping_local_state = is_local_state_header(line)
            if skipping_local_state:
                continue

        if skipping_local_state:
            continue

        normalized = line
        for prefix in dict.fromkeys(path_patterns()):
            normalized = re.sub(re.escape(prefix) + boundary, "~", normalized)
        normalized = strip_trailing_whitespace(normalized)
        output.append(normalized)

    return drop_duplicate_project_tables(drop_duplicate_tables("".join(output)))


def is_single_table_header(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("[") and not stripped.startswith("[[") and stripped.endswith("]")


def is_hooks_state_header(line: str) -> bool:
    stripped = line.strip()
    return stripped == "[hooks.state]" or stripped.startswith("[hooks.state.")


def is_local_state_header(line: str) -> bool:
    return is_hooks_state_header(line)


def strip_trailing_whitespace(line: str) -> str:
    newline = "\n" if line.endswith("\n") else ""
    body = line[:-1] if newline else line
    return body.rstrip(" \t") + newline


def drop_duplicate_tables(text: str) -> str:
    lines = text.splitlines(keepends=True)
    seen_headers: set[str] = set()
    output: list[str] = []
    skipping_duplicate = False

    for line in lines:
        if is_single_table_header(line):
            header = line.strip()
            if header in seen_headers:
                skipping_duplicate = True
                continue
            seen_headers.add(header)
            skipping_duplicate = False

        if not skipping_duplicate:
            output.append(line)

    return "".join(output)


def drop_duplicate_project_tables(text: str) -> str:
    inline_projects = collect_inline_projects(text)
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    skipping_duplicate = False

    for line in lines:
        project_name = parse_project_subtable_header(line)
        if project_name is not None:
            skipping_duplicate = project_name in inline_projects
            if skipping_duplicate:
                continue

        elif is_single_table_header(line):
            skipping_duplicate = False

        if not skipping_duplicate:
            output.append(line)

    return "".join(output)


def collect_inline_projects(text: str) -> set[str]:
    projects: set[str] = set()
    in_projects = False

    for line in text.splitlines():
        stripped = line.strip()
        if is_single_table_header(line):
            in_projects = stripped == "[projects]"
            continue

        if not in_projects:
            continue

        match = re.match(r'"([^"]+)"\s*=', stripped)
        if match:
            projects.add(match.group(1))

    return projects


def parse_project_subtable_header(line: str) -> str | None:
    match = re.fullmatch(r'\[projects\."(.+)"\]\s*', line.strip())
    if not match:
        return None
    return match.group(1)


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


def emit_hook_output(changed: bool, config: Path) -> None:
    payload = {
        "continue": True,
        "suppressOutput": True,
        "systemMessage": (
            f"Synced portable Codex config snapshot to {config}"
            if changed
            else ""
        ),
    }
    print(json.dumps(payload, separators=(",", ":")))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync a portable Codex config snapshot from local runtime config."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path(),
        help="Local runtime Codex config.toml path. Defaults to CODEX_HOME/config.toml or ~/.codex/config.toml.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Portable config snapshot path. Defaults to --config.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when the config would be changed.",
    )
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Codex hook-compatible JSON on stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = args.config.expanduser()
    output = (args.output or args.config).expanduser()

    try:
        original = config.read_text(encoding="utf-8")
    except FileNotFoundError:
        if args.hook_output:
            emit_hook_output(False, config)
            return 0
        print(f"config not found: {config}", file=sys.stderr)
        return 1

    normalized = normalize_text(original)
    previous_output = read_optional_text(output)
    changed = normalized != previous_output

    if args.check:
        if args.hook_output:
            emit_hook_output(False, config)
        elif changed:
            print(f"portable Codex config is out of sync: {output}", file=sys.stderr)
        return 1 if changed else 0

    if changed:
        write_atomic(output, normalized)

    if args.hook_output:
        emit_hook_output(changed, output)
    elif changed:
        print(f"synced portable Codex config: {output}")
    else:
        print(f"portable Codex config already current: {output}")

    return 0


def read_optional_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
