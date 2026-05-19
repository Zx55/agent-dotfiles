#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REQUIRED_FILES = ["MEMORY.md", "memory_summary.md", "raw_memories.md"]
EXPECTED_DIRS = ["rollout_summaries"]
MAINTENANCE_SUBDIRS = ["reports", "plans", "backups", "state", "tmp", "locks"]

SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    "api_key_assignment": re.compile(
        r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[^'\"\s]{12,}"
    ),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
}

PATH_PATTERNS = {
    "absolute_home_path": re.compile(r"/Users/[A-Za-z0-9._-]+/[^\s)`'\"<>]+"),
    "tmp_path": re.compile(r"(/tmp|/private/var/folders)/[^\s)`'\"<>]+"),
    "secret_file_reference": re.compile(r"(?i)(^|[/\s])(\.secret|secret\.local)(\s|$|[/])"),
}


@dataclass
class Finding:
    severity: str
    category: str
    path: str
    detail: str
    line: int | None = None


def expand(path: str) -> Path:
    return Path(path).expanduser().resolve()


def ensure_maintenance_dirs(root: Path) -> None:
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except PermissionError:
        pass
    for name in MAINTENANCE_SUBDIRS:
        (root / name).mkdir(parents=True, exist_ok=True)


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_text_files(root: Path) -> Iterable[Path]:
    candidates = [root / name for name in REQUIRED_FILES]
    rollout_dir = root / "rollout_summaries"
    if rollout_dir.is_dir():
        candidates.extend(sorted(rollout_dir.glob("*.md"))[:200])
        candidates.extend(sorted(rollout_dir.glob("*.jsonl"))[:200])
    for path in candidates:
        if path.is_file():
            yield path


def scan_text_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return [
            Finding(
                severity="error",
                category="read_error",
                path=rel(path, root),
                detail=str(exc),
            )
        ]

    for index, line in enumerate(lines, start=1):
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                findings.append(
                    Finding(
                        severity="high",
                        category=f"secret_like:{name}",
                        path=rel(path, root),
                        line=index,
                        detail="matched sensitive-value pattern; value intentionally omitted",
                    )
                )
        for name, pattern in PATH_PATTERNS.items():
            if pattern.search(line):
                findings.append(
                    Finding(
                        severity="medium",
                        category=f"path:{name}",
                        path=rel(path, root),
                        line=index,
                        detail="matched path portability or secret-file reference pattern",
                    )
                )
    return findings


def duplicate_headings(path: Path, root: Path) -> list[Finding]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = [line.strip() for line in text.splitlines() if line.startswith("#")]
    counts = Counter(headings)
    findings: list[Finding] = []
    for heading, count in counts.items():
        if count > 1:
            findings.append(
                Finding(
                    severity="medium",
                    category="duplicate_heading",
                    path=rel(path, root),
                    detail=f"{heading!r} appears {count} times",
                )
            )
    return findings


def paragraph_fingerprints(path: Path, root: Path) -> list[Finding]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) >= 160]
    normalized = [" ".join(p.lower().split()) for p in paragraphs]
    counts = Counter(normalized)
    duplicate_count = sum(count - 1 for count in counts.values() if count > 1)
    if duplicate_count == 0:
        return []
    return [
        Finding(
            severity="medium",
            category="duplicate_paragraph",
            path=rel(path, root),
            detail=f"{duplicate_count} repeated long paragraph(s) detected",
        )
    ]


def collect_stats(root: Path) -> dict[str, object]:
    files: dict[str, object] = {}
    for path in sorted(root.rglob("*")) if root.exists() else []:
        if ".git" in path.parts:
            continue
        if path.is_file():
            stat = path.stat()
            files[rel(path, root)] = {
                "bytes": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "sha256": sha256_file(path),
            }
    return {
        "file_count": len(files),
        "files": files,
    }


def inspect(memory_root: Path, maintenance_root: Path) -> dict[str, object]:
    findings: list[Finding] = []

    if not memory_root.exists():
        findings.append(
            Finding(
                severity="error",
                category="layout",
                path=str(memory_root),
                detail="memory root does not exist",
            )
        )
        return {"findings": [asdict(item) for item in findings], "stats": {}}

    for name in REQUIRED_FILES:
        path = memory_root / name
        if path.is_file():
            size = path.stat().st_size
            if name == "memory_summary.md" and size > 80_000:
                findings.append(
                    Finding(
                        severity="medium",
                        category="size",
                        path=name,
                        detail=f"memory_summary.md is large ({size} bytes)",
                    )
                )
            elif name == "MEMORY.md" and size > 300_000:
                findings.append(
                    Finding(
                        severity="medium",
                        category="size",
                        path=name,
                        detail=f"MEMORY.md is large ({size} bytes)",
                    )
                )
        else:
            findings.append(
                Finding(
                    severity="error",
                    category="layout",
                    path=name,
                    detail="required memory file missing",
                )
            )

    for name in EXPECTED_DIRS:
        if not (memory_root / name).is_dir():
            findings.append(
                Finding(
                    severity="warning",
                    category="layout",
                    path=name,
                    detail="expected memory directory missing",
                )
            )

    if not (memory_root / ".git").is_dir():
        findings.append(
            Finding(
                severity="warning",
                category="layout",
                path=".git",
                detail="memory baseline .git directory missing",
            )
        )

    for path in iter_text_files(memory_root):
        findings.extend(scan_text_file(path, memory_root))

    findings.extend(duplicate_headings(memory_root / "MEMORY.md", memory_root))
    findings.extend(paragraph_fingerprints(memory_root / "MEMORY.md", memory_root))
    findings.extend(paragraph_fingerprints(memory_root / "memory_summary.md", memory_root))

    stats = collect_stats(memory_root)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "memory_root": str(memory_root),
        "maintenance_root": str(maintenance_root),
        "findings": [asdict(item) for item in findings],
        "stats": stats,
    }


def write_report(result: dict[str, object], maintenance_root: Path) -> tuple[Path, Path]:
    ensure_maintenance_dirs(maintenance_root)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = maintenance_root / "reports" / f"memory-audit-{timestamp}.json"
    md_path = maintenance_root / "reports" / f"memory-audit-{timestamp}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    findings = result.get("findings", [])
    lines = [
        "# Codex Memory Audit",
        "",
        f"- Generated at: `{result.get('generated_at')}`",
        f"- Memory root: `{result.get('memory_root')}`",
        f"- Maintenance root: `{result.get('maintenance_root')}`",
        f"- Finding count: `{len(findings)}`",
        "",
        "## Findings",
        "",
    ]
    if findings:
        for item in findings:
            line = item.get("line")
            location = item.get("path")
            if line is not None:
                location = f"{location}:{line}"
            lines.append(
                f"- **{item.get('severity')}** `{item.get('category')}` `{location}` - {item.get('detail')}"
            )
    else:
        lines.append("- No findings.")
    lines.extend(["", "## Notes", "", "Sensitive matched values are intentionally omitted."])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Codex memory files without modifying them.")
    parser.add_argument("--memory-root", default="~/.codex/memories")
    parser.add_argument("--maintenance-root", default="~/.codex-memory-maintenance")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    memory_root = expand(args.memory_root)
    maintenance_root = expand(args.maintenance_root)
    result = inspect(memory_root, maintenance_root)
    if args.no_write_report:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    md_path, json_path = write_report(result, maintenance_root)
    print(json.dumps({"report": str(md_path), "json": str(json_path), "findings": len(result["findings"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
