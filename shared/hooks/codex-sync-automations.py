#!/usr/bin/env python3
"""Sync portable Codex App automation snapshots from local runtime files."""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def default_runtime_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "automations"
    return Path("~/.codex/automations").expanduser()


def default_output_dir() -> Path:
    return (
        Path.home()
        / "Documents"
        / "codex-workspace"
        / "agent-dotfiles"
        / "agents"
        / "codex"
        / "automations"
    )


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
    boundary = r'(?=/|["\']|\s|,|\]|\}|\)|$)'
    normalized = text
    for prefix in dict.fromkeys(path_patterns()):
        normalized = re.sub(re.escape(prefix) + boundary, "~", normalized)
    return normalized


def parse_automation_id(text: str) -> str | None:
    match = re.search(r'^id\s*=\s*"([^"]+)"\s*$', text, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        temp_name = handle.name
        handle.write(content)

    os.replace(temp_name, path)


def read_optional_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def remove_snapshot(target: Path) -> None:
    if not target.exists():
        return

    snapshot_dir = target.parent
    target.unlink()
    try:
        snapshot_dir.rmdir()
    except OSError:
        pass


def known_automation_ids(output_dir: Path) -> list[str]:
    if not output_dir.exists():
        return []
    return sorted(
        child.name
        for child in output_dir.iterdir()
        if child.is_dir() and (child / "automation.toml").is_file()
    )


def runtime_automation_ids(runtime_dir: Path) -> list[str]:
    if not runtime_dir.exists():
        return []
    return sorted(
        child.name
        for child in runtime_dir.iterdir()
        if child.is_dir() and (child / "automation.toml").is_file()
    )


def sync_automation(
    automation_id: str,
    runtime_dir: Path,
    output_dir: Path,
    *,
    check: bool,
) -> tuple[bool, str | None]:
    source = runtime_dir / automation_id / "automation.toml"
    target = output_dir / automation_id / "automation.toml"
    text = read_optional_text(source)
    if text is None:
        if not target.exists():
            return False, None
        if not check:
            remove_snapshot(target)
        return True, None

    actual_id = parse_automation_id(text)
    if actual_id != automation_id:
        return (
            False,
            f"skipping {source}: id is {actual_id!r}, expected {automation_id!r}",
        )

    normalized = normalize_text(text)
    previous = read_optional_text(target)
    changed = normalized != previous

    if changed and not check:
        write_atomic(target, normalized)

    return changed, None


def managed_automation_ids(runtime_dir: Path, output_dir: Path) -> list[str]:
    return sorted(
        set(runtime_automation_ids(runtime_dir)) | set(known_automation_ids(output_dir))
    )


def sync_automations(
    runtime_dir: Path,
    output_dir: Path,
    *,
    check: bool,
) -> tuple[int, list[str]]:
    ids = managed_automation_ids(runtime_dir, output_dir)
    changed_count = 0
    warnings: list[str] = []

    for automation_id in ids:
        changed, warning = sync_automation(
            automation_id,
            runtime_dir,
            output_dir,
            check=check,
        )
        if warning:
            warnings.append(warning)
            continue
        if changed:
            changed_count += 1

    return changed_count, warnings


def emit_hook_output(changed_count: int, warnings: list[str]) -> None:
    if warnings:
        message = f"Skipped {len(warnings)} Codex automation snapshot(s)"
    elif changed_count:
        message = f"Synced {changed_count} portable Codex automation snapshot(s)"
    else:
        message = ""

    payload = {
        "continue": True,
        "suppressOutput": True,
        "systemMessage": message,
    }
    print(json.dumps(payload, separators=(",", ":")))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sync portable Codex App automation snapshots from local runtime "
            "automation.toml files."
        )
    )
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=default_runtime_dir(),
        help="Local Codex automation runtime directory. Defaults to CODEX_HOME/automations or ~/.codex/automations.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir(),
        help="Portable automation snapshot directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when automation snapshots would be created, changed, removed, or skipped.",
    )
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Codex hook-compatible JSON on stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime_dir = args.runtime_dir.expanduser()
    output_dir = args.output_dir.expanduser()

    changed_count, warnings = sync_automations(
        runtime_dir,
        output_dir,
        check=args.check,
    )

    if args.hook_output:
        emit_hook_output(changed_count, warnings)
    else:
        for warning in warnings:
            print(warning, file=sys.stderr)
        if changed_count:
            verb = "would sync" if args.check else "synced"
            print(f"{verb} {changed_count} portable Codex automation snapshot(s)")
        else:
            print("portable Codex automation snapshots already current")

    if args.check and (changed_count or warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
