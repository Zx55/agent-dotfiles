#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


DEFAULT_FILES = ["MEMORY.md", "memory_summary.md"]


def expand(path: str) -> Path:
    return Path(path).expanduser().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Back up editable Codex memory files before maintenance.")
    parser.add_argument("--memory-root", default="~/.codex/memories")
    parser.add_argument("--maintenance-root", default="~/.codex-memory-maintenance")
    parser.add_argument("--include-raw", action="store_true", help="Also back up raw_memories.md.")
    args = parser.parse_args()

    memory_root = expand(args.memory_root)
    maintenance_root = expand(args.maintenance_root)
    backup_root = maintenance_root / "backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_dir = backup_root / datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=False)

    files = list(DEFAULT_FILES)
    if args.include_raw:
        files.append("raw_memories.md")

    copied: list[str] = []
    missing: list[str] = []
    for name in files:
        source = memory_root / name
        if source.is_file():
            target = backup_dir / name
            shutil.copy2(source, target)
            copied.append(name)
        else:
            missing.append(name)

    manifest = {"backup_dir": str(backup_dir), "copied": copied, "missing": missing}
    (backup_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
