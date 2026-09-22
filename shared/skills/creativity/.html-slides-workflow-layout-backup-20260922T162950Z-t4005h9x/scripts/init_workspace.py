#!/usr/bin/env python3
"""Copy the skill's reusable resources into a new, empty workspace."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil


def initialize(destination: Path) -> None:
    skill_dir: Path = Path(__file__).resolve().parent.parent
    templates: Path = skill_dir / "templates"
    scripts: Path = skill_dir / "scripts"
    required: list[str] = [
        "export-pdf.mjs", "export-pptx.mjs", "verify_pptx.py", "lib/common.mjs",
    ]
    for name in required:
        if not (scripts / name).is_file():
            raise ValueError(f"Incomplete skill resources: {name}")
    if not (templates / "slides/template.html").is_file():
        raise ValueError("Missing blank slide template")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError(f"Refusing to overwrite a nonempty workspace: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(templates, destination, dirs_exist_ok=True)
    for name in required:
        target: Path = destination / "scripts" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(scripts / name, target)
    for folder in ("assets/common", "notes", "exports"):
        (destination / folder).mkdir(parents=True, exist_ok=True)
    print(f"Initialized {destination}")
    print("No content slides or notes were invented. Start from slides/template.html.")
    print("See the skill's references/export.md for dependency setup and export commands.")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="New or empty workspace directory")
    args: argparse.Namespace = parser.parse_args()
    try:
        initialize(args.workspace.expanduser().resolve())
    except (OSError, ValueError) as error:
        parser.exit(1, f"Initialization failed: {error}\n")


if __name__ == "__main__":
    main()
