#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import shutil
import sys
import unicodedata


@dataclass(frozen=True)
class TemplateSpec:
    source_name: str
    dest_name: str


TEMPLATES = (
    TemplateSpec("search_report.template.md", "search_report.md"),
    TemplateSpec("deep_reading_report.template.md", "deep_reading_report.md"),
    TemplateSpec("final_report.template.md", "final_report.md"),
)


def slugify(value: str) -> str:
    slug = unicodedata.normalize("NFKC", value).strip().lower()
    slug = re.sub(r"[^\w]+", "-", slug, flags=re.UNICODE)
    slug = re.sub(r"_+", "-", slug).strip("-")
    return slug or "topic"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a task-local surveys workspace for the paper-survey skill."
    )
    parser.add_argument("--topic", required=True, help="Survey topic.")
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Base directory where the surveys/ folder should be created. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date suffix for the survey directory. Defaults to today's local date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing materialized templates and final_report.md if the survey directory already exists.",
    )
    return parser.parse_args()


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def survey_root(base_dir: Path, topic: str, date_str: str) -> Path:
    topic_slug = slugify(topic)
    return (base_dir / "surveys" / f"survey-{topic_slug}-{date_str}").resolve()


def write_manifest(path: Path, topic: str, survey_dir: Path) -> None:
    content = "\n".join(
        [
            "# Survey Manifest",
            "",
            f"- Topic: {topic}",
            f"- Created: {datetime.now().isoformat(timespec='seconds')}",
            "- Survey Workspace: .",
            "- Templates: templates/",
            "- Search Reports: search_reports/",
            "- Deep Read Reports: deep_read_reports/",
            "- Assets: assets/",
            "- Final Report: final_report.md",
            "",
            "## Focus Map",
            "",
            "| Phase | Focus | Main Artifact / Gate |",
            "| --- | --- | --- |",
            "| Setup | normalize topic, language, time window, workspace | Workspace initialized |",
            "| Search | broad retrieval and triage by complementary query | search_reports/*.md |",
            "| Merge | dedupe, cluster, and pick core papers | Core papers selected |",
            "| Zotero | dedupe library, import verified PDFs, place collection | Zotero capture completed or explicitly marked unresolved |",
            "| Deep Read | claim-level evidence for core papers | deep_read_reports/*.md |",
            "| Visuals | one visual-anchor decision per core paper | assets/* or explicit none reason |",
            "| Synthesis | comparison, claims, gaps, next steps | final_report.md |",
            "",
            "## Gates",
            "",
            "### Setup",
            "",
            "- [ ] Workspace initialized",
            "",
            "### Search",
            "",
            "- [ ] Search reports written",
            "",
            "### Merge",
            "",
            "- [ ] Core papers selected",
            "",
            "### Zotero",
            "",
            "- [ ] Zotero capture completed or explicitly marked unresolved",
            "",
            "### Deep Read",
            "",
            "- [ ] Deep-reading reports written",
            "- [ ] Visual anchors considered for each core paper",
            "",
            "### Synthesis",
            "",
            "- [ ] Final report links deep-reading reports",
            "- [ ] Final report records Zotero collection path or unresolved status",
            "- [ ] Final report includes evidence gaps and uncertainties",
            "",
            "Use this workspace for all survey artifacts in this run.",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def copy_template(src: Path, dest: Path, force: bool) -> None:
    if dest.exists() and not force:
        return
    shutil.copyfile(src, dest)


def main() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir).expanduser().resolve()
    survey_dir = survey_root(base_dir, args.topic, args.date)
    templates_dir = survey_dir / "templates"
    search_reports_dir = survey_dir / "search_reports"
    deep_read_reports_dir = survey_dir / "deep_read_reports"
    assets_dir = survey_dir / "assets"

    for directory in (templates_dir, search_reports_dir, deep_read_reports_dir, assets_dir):
        directory.mkdir(parents=True, exist_ok=True)

    source_templates_dir = skill_root() / "templates"
    for spec in TEMPLATES:
        src = source_templates_dir / spec.source_name
        if not src.exists():
            print(f"Missing template source: {src}", file=sys.stderr)
            return 1
        copy_template(src, templates_dir / spec.dest_name, args.force)

    final_report_path = survey_dir / "final_report.md"
    copy_template(templates_dir / "final_report.md", final_report_path, args.force)

    write_manifest(survey_dir / "manifest.md", args.topic, survey_dir)

    print(survey_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
