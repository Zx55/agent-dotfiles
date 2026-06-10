#!/usr/bin/env python3
"""Keep globally visible Lark skills limited to the approved allowlist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys


ALLOWED_LARK_SKILLS = {
    "lark-base",
    "lark-calendar",
    "lark-contact",
    "lark-doc",
    "lark-drive",
    "lark-im",
    "lark-openapi-explorer",
    "lark-shared",
    "lark-sheets",
    "lark-slides",
    "lark-task",
    "lark-vc",
    "lark-whiteboard",
    "lark-wiki",
    "lark-workflow-meeting-summary",
    "lark-workflow-standup-report",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move unapproved Lark skills out of ~/.agents/skills."
    )
    parser.add_argument(
        "--skills-dir",
        default="~/.agents/skills",
        help="Directory containing globally installed agent skills.",
    )
    parser.add_argument(
        "--disabled-dir",
        default="~/.agents/skills-disabled/lark-cli-unused",
        help="Directory where unapproved Lark skills are moved.",
    )
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Cursor hook-compatible JSON on stdout.",
    )
    return parser.parse_args()


def remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)


def prune_lark_skills(skills_dir: Path, disabled_dir: Path) -> list[str]:
    if not skills_dir.exists():
        return []

    disabled_dir.mkdir(parents=True, exist_ok=True)
    moved: list[str] = []

    for skill_path in sorted(skills_dir.iterdir(), key=lambda path: path.name):
        name = skill_path.name
        if not name.startswith("lark-") or name in ALLOWED_LARK_SKILLS:
            continue

        target = disabled_dir / name
        if target.exists() or target.is_symlink():
            remove_existing(target)
        shutil.move(str(skill_path), str(target))
        moved.append(name)

    return moved


def emit_hook_output() -> None:
    print("{}")


def main() -> int:
    args = parse_args()
    skills_dir = Path(args.skills_dir).expanduser()
    disabled_dir = Path(args.disabled_dir).expanduser()

    try:
        moved = prune_lark_skills(skills_dir, disabled_dir)
    except OSError as exc:
        if args.hook_output:
            emit_hook_output()
        print(f"failed to prune Lark skills: {exc}", file=sys.stderr)
        return 1

    if args.hook_output:
        emit_hook_output()
    elif moved:
        print(json.dumps({"moved": moved}, ensure_ascii=False))
    else:
        print("Lark skills already match allowlist.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
