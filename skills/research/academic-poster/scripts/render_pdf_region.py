#!/usr/bin/env python3
"""Render a cropped PDF master to a PNG derivative."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a PDF region to PNG")
    parser.add_argument("input_pdf")
    parser.add_argument("output_png")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--page", type=int, default=1, help="1-based page number")
    args = parser.parse_args()

    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("Missing dependency: install PyMuPDF to render PDF regions") from exc

    input_pdf = Path(args.input_pdf).expanduser().resolve()
    output_png = Path(args.output_png).expanduser().resolve()
    output_png.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(input_pdf))
    page_index = args.page - 1
    if page_index < 0 or page_index >= len(doc):
        raise SystemExit(f"Page out of range: {args.page}")

    zoom = args.dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    page = doc[page_index]
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    pix.save(str(output_png))

    print(f"Wrote PNG: {output_png}")
    print(f"Pixel size: {pix.width} x {pix.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
