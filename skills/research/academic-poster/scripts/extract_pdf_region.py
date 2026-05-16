#!/usr/bin/env python3
"""Crop a PDF page region to a new one-page PDF master."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("bbox must be left,top,right,bottom")
    left, top, right, bottom = parts
    if right <= left or bottom <= top:
        raise argparse.ArgumentTypeError("bbox must satisfy right > left and bottom > top")
    return left, top, right, bottom


def main() -> int:
    parser = argparse.ArgumentParser(description="Crop a source PDF page to a region PDF")
    parser.add_argument("source_pdf")
    parser.add_argument("output_pdf")
    parser.add_argument("--page", type=int, required=True, help="1-based PDF page number")
    parser.add_argument(
        "--bbox",
        required=True,
        type=parse_bbox,
        help="Region as left,top,right,bottom in PDF points from the top-left page origin",
    )
    args = parser.parse_args()

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise SystemExit("Missing dependency: install pypdf to crop PDF regions") from exc

    source_pdf = Path(args.source_pdf).expanduser().resolve()
    output_pdf = Path(args.output_pdf).expanduser().resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(source_pdf))
    page_index = args.page - 1
    if page_index < 0 or page_index >= len(reader.pages):
        raise SystemExit(f"Page out of range: {args.page}")

    page = reader.pages[page_index]
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    left, top, right, bottom = args.bbox

    if left < 0 or top < 0 or right > page_width or bottom > page_height:
        raise SystemExit(
            f"bbox {args.bbox} exceeds page size {page_width:.2f} x {page_height:.2f} points"
        )

    # pypdf boxes use a bottom-left origin. The skill bbox uses top-left for easier visual markup.
    page.cropbox.lower_left = (left, page_height - bottom)
    page.cropbox.upper_right = (right, page_height - top)
    page.mediabox.lower_left = page.cropbox.lower_left
    page.mediabox.upper_right = page.cropbox.upper_right

    writer = PdfWriter()
    writer.add_page(page)
    with output_pdf.open("wb") as f:
        writer.write(f)

    print(f"Wrote cropped PDF: {output_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
