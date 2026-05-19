#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import inspect_memories


REQUIRED_FILES = ["MEMORY.md", "memory_summary.md", "raw_memories.md"]


def expand(path: str) -> Path:
    return Path(path).expanduser().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Codex memory structure after maintenance.")
    parser.add_argument("--memory-root", default="~/.codex/memories")
    parser.add_argument("--maintenance-root", default="~/.codex-memory-maintenance")
    parser.add_argument("--allow-existing-sensitive-findings", action="store_true")
    args = parser.parse_args()

    memory_root = expand(args.memory_root)
    maintenance_root = expand(args.maintenance_root)
    errors: list[str] = []
    warnings: list[str] = []

    if not memory_root.exists():
        errors.append(f"memory root missing: {memory_root}")
    else:
        for name in REQUIRED_FILES:
            path = memory_root / name
            if not path.is_file():
                errors.append(f"required file missing: {name}")
            elif not path.read_text(encoding="utf-8", errors="replace").strip():
                warnings.append(f"file is empty: {name}")

        if not (memory_root / "rollout_summaries").is_dir():
            warnings.append("rollout_summaries directory missing")
        if not (memory_root / ".git").is_dir():
            warnings.append(".git baseline directory missing")

    if not maintenance_root.is_dir():
        errors.append(f"maintenance root missing: {maintenance_root}")

    result = inspect_memories.inspect(memory_root, maintenance_root)
    sensitive_findings = [
        item for item in result.get("findings", [])
        if str(item.get("category", "")).startswith("secret_like:")
    ]
    if sensitive_findings and not args.allow_existing_sensitive_findings:
        errors.append(f"{len(sensitive_findings)} sensitive-pattern finding(s) present")

    output = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "finding_count": len(result.get("findings", [])),
        "sensitive_finding_count": len(sensitive_findings),
    }
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
