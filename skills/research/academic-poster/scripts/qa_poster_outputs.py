#!/usr/bin/env python3
"""Run basic QA checks for academic poster outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def image_size(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Missing dependency: install Pillow to inspect PNG dimensions") from exc
    with Image.open(path) as image:
        return image.size


def check_file(path: Path, label: str, issues: list[str]) -> None:
    if not path.exists():
        issues.append(f"Missing {label}: {path}")
        return
    if path.stat().st_size == 0:
        issues.append(f"Empty {label}: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="QA poster PPTX/PDF/PNG outputs")
    parser.add_argument("poster_spec")
    parser.add_argument("--tolerance-px", type=int, default=8)
    args = parser.parse_args()

    spec_path = Path(args.poster_spec).expanduser().resolve()
    spec_dir = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    exports = spec.get("exports", {})

    pptx = spec_dir / exports.get("pptx", "exports/poster.pptx")
    pdf = spec_dir / exports.get("pdf", "exports/poster.pdf")
    png = spec_dir / exports.get("png", "exports/poster.png")

    issues: list[str] = []
    warnings: list[str] = []
    check_file(pptx, "PPTX", issues)
    check_file(pdf, "PDF", issues)
    check_file(png, "PNG", issues)

    canvas = spec.get("canvas", {})
    width_in = float(canvas.get("width_in", 0))
    height_in = float(canvas.get("height_in", 0))
    dpi = int(canvas.get("dpi", 300))
    expected = (round(width_in * dpi), round(height_in * dpi))

    if png.exists() and width_in and height_in:
        actual = image_size(png)
        dx = abs(actual[0] - expected[0])
        dy = abs(actual[1] - expected[1])
        if dx > args.tolerance_px or dy > args.tolerance_px:
            issues.append(f"PNG size {actual[0]} x {actual[1]} does not match expected {expected[0]} x {expected[1]}")
        else:
            print(f"PNG size OK: {actual[0]} x {actual[1]}")

    for region in spec.get("regions", []):
        rendered = region.get("rendered_png")
        if not rendered:
            continue
        region_path = spec_dir / rendered
        check_file(region_path, f"region PNG {region.get('id', rendered)}", issues)
        if region_path.exists():
            actual = image_size(region_path)
            required_w = None
            required_h = None
            for element in spec.get("elements", []):
                if element.get("type") == "image" and element.get("path") == rendered:
                    required_w = round(float(element.get("w", 0)) * dpi)
                    required_h = round(float(element.get("h", 0)) * dpi)
                    break
            if required_w and required_h and (actual[0] < required_w or actual[1] < required_h):
                warnings.append(
                    f"Region {region.get('id', rendered)} is {actual[0]} x {actual[1]} px, below placed size target {required_w} x {required_h} px"
                )

    if issues:
        print("Issues:")
        for issue in issues:
            print(f"- {issue}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if issues:
        return 1
    print("Basic poster QA passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
