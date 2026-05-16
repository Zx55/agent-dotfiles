#!/usr/bin/env python3
"""Initialize an academic poster workspace."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


STAGES = [
    "initialized",
    "inputs_registered",
    "planned",
    "drafts_generated",
    "draft_selected",
    "regions_extracted",
    "pptx_built",
    "exports_rendered",
    "qa_passed",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_template(skill_dir: Path, orientation: str) -> dict:
    template_name = "portrait-basic.json" if orientation == "portrait" else "landscape-basic.json"
    template_path = skill_dir / "assets" / "templates" / template_name
    with template_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize an academic poster workspace")
    parser.add_argument("workspace", help="Workspace directory to create or reuse")
    parser.add_argument("--title", default="Academic Poster", help="Poster title")
    parser.add_argument("--orientation", choices=["landscape", "portrait"], default="landscape")
    parser.add_argument("--width-in", type=float, help="Canvas width in inches")
    parser.add_argument("--height-in", type=float, help="Canvas height in inches")
    parser.add_argument("--dpi", type=int, default=300, help="Target print DPI")
    parser.add_argument("--template", help="Optional poster-spec template JSON")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    skill_dir = Path(__file__).resolve().parents[1]
    workspace.mkdir(parents=True, exist_ok=True)

    for child in ["inputs", "planning", "drafts", "assets", "regions", "exports", "qa"]:
        (workspace / child).mkdir(exist_ok=True)

    if args.template:
        template_path = Path(args.template).expanduser().resolve()
        with template_path.open("r", encoding="utf-8") as f:
            spec = json.load(f)
    else:
        spec = load_template(skill_dir, args.orientation)

    spec.setdefault("version", 1)
    spec.setdefault("canvas", {})
    if args.width_in:
        spec["canvas"]["width_in"] = args.width_in
    if args.height_in:
        spec["canvas"]["height_in"] = args.height_in
    spec["canvas"]["dpi"] = args.dpi
    spec["canvas"]["orientation"] = args.orientation
    spec.setdefault("title", args.title)
    spec.setdefault("assets", [])
    spec.setdefault("regions", [])
    spec.setdefault("elements", [])
    spec["exports"] = {
        "pptx": "exports/poster.pptx",
        "pdf": "exports/poster.pdf",
        "png": "exports/poster.png",
    }

    spec_path = workspace / "poster-spec.json"
    if not spec_path.exists():
        spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "version": 1,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "workspace": str(workspace),
        "poster_spec": "poster-spec.json",
        "title": args.title,
        "stages": {
            stage: {
                "status": "pending",
                "updated_at": None,
                "artifacts": [],
                "notes": "",
            }
            for stage in STAGES
        },
    }
    manifest["stages"]["initialized"] = {
        "status": "done",
        "updated_at": now_iso(),
        "artifacts": ["poster-spec.json"],
        "notes": "Workspace initialized with poster-spec.json and standard folders.",
    }

    manifest_path = workspace / "manifest.json"
    if manifest_path.exists():
        backup_path = workspace / f"manifest.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        shutil.copy2(manifest_path, backup_path)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Initialized poster workspace: {workspace}")
    print(f"Wrote: {manifest_path}")
    print(f"Wrote: {spec_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
