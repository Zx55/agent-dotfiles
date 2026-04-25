#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a PDF page or normalized page crop to a PNG asset."
    )
    parser.add_argument("--pdf", required=True, help="Path to the source PDF.")
    parser.add_argument(
        "--page",
        required=True,
        type=int,
        help="1-indexed PDF page number to render.",
    )
    parser.add_argument("--out", required=True, help="Output PNG path.")
    parser.add_argument(
        "--crop",
        nargs=4,
        type=float,
        metavar=("X", "Y", "WIDTH", "HEIGHT"),
        help="Optional normalized crop rectangle, each value in [0, 1].",
    )
    parser.add_argument(
        "--zoom",
        type=float,
        default=2.0,
        help="Render zoom factor. Defaults to 2.0.",
    )
    return parser.parse_args()


def validate_crop(crop: list[float] | None) -> None:
    if crop is None:
        return
    x, y, width, height = crop
    if width <= 0 or height <= 0:
        raise ValueError("Crop width and height must be positive.")
    if x < 0 or y < 0 or x + width > 1 or y + height > 1:
        raise ValueError("Crop rectangle must fit within normalized page bounds.")


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()

    if not pdf_path.exists():
        print(f"Missing PDF: {pdf_path}", file=sys.stderr)
        return 1

    try:
        import fitz
    except ImportError:
        print(
            "PyMuPDF is required for render_pdf_asset.py. Install it with `python -m pip install pymupdf`.",
            file=sys.stderr,
        )
        return 1

    try:
        validate_crop(args.crop)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    doc = fitz.open(pdf_path)
    try:
        if args.page < 1 or args.page > len(doc):
            print(f"Page must be between 1 and {len(doc)}.", file=sys.stderr)
            return 1

        page = doc[args.page - 1]
        clip = None
        if args.crop is not None:
            x, y, width, height = args.crop
            rect = page.rect
            clip = fitz.Rect(
                rect.x0 + x * rect.width,
                rect.y0 + y * rect.height,
                rect.x0 + (x + width) * rect.width,
                rect.y0 + (y + height) * rect.height,
            )

        matrix = fitz.Matrix(args.zoom, args.zoom)
        pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(out_path)
    finally:
        doc.close()

    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
