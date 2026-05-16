#!/usr/bin/env python3
"""Render final poster PDF and PNG exports."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def find_soffice() -> str | None:
    for name in ["soffice", "libreoffice"]:
        found = shutil.which(name)
        if found:
            return found
    candidates = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/Applications/OpenOffice.app/Contents/MacOS/soffice",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def pptx_to_pdf(pptx_path: Path, pdf_path: Path) -> None:
    soffice = find_soffice()
    if not soffice:
        raise SystemExit("Missing renderer: install LibreOffice or provide --pdf from another renderer")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    out_dir = pdf_path.parent
    subprocess.run(
        [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(out_dir),
            str(pptx_path),
        ],
        check=True,
    )
    converted = out_dir / f"{pptx_path.stem}.pdf"
    if converted != pdf_path:
        converted.replace(pdf_path)


def render_pdf_to_png(pdf_path: Path, png_path: Path, dpi: int) -> None:
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("Missing dependency: install PyMuPDF to render final PNG") from exc

    doc = fitz.open(str(pdf_path))
    if len(doc) == 0:
        raise SystemExit("PDF has no pages")
    matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = doc[0].get_pixmap(matrix=matrix, alpha=False)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(png_path))
    print(f"Wrote PNG: {png_path}")
    print(f"Pixel size: {pix.width} x {pix.height}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render poster PDF and PNG exports")
    parser.add_argument("poster_spec")
    parser.add_argument("--pptx", help="PPTX path. Defaults to spec exports.pptx")
    parser.add_argument("--pdf", help="PDF path. Defaults to spec exports.pdf")
    parser.add_argument("--png", help="PNG path. Defaults to spec exports.png")
    parser.add_argument("--dpi", type=int, help="PNG render DPI. Defaults to spec canvas.dpi")
    parser.add_argument("--skip-pdf", action="store_true", help="Use existing PDF and only render PNG")
    args = parser.parse_args()

    spec_path = Path(args.poster_spec).expanduser().resolve()
    spec_dir = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    pptx_path = Path(args.pptx or spec.get("exports", {}).get("pptx", "exports/poster.pptx"))
    pdf_path = Path(args.pdf or spec.get("exports", {}).get("pdf", "exports/poster.pdf"))
    png_path = Path(args.png or spec.get("exports", {}).get("png", "exports/poster.png"))
    if not pptx_path.is_absolute():
        pptx_path = spec_dir / pptx_path
    if not pdf_path.is_absolute():
        pdf_path = spec_dir / pdf_path
    if not png_path.is_absolute():
        png_path = spec_dir / png_path

    dpi = args.dpi or int(spec.get("canvas", {}).get("dpi", 300))

    if not args.skip_pdf:
        if not pptx_path.exists():
            raise SystemExit(f"Missing PPTX: {pptx_path}")
        pptx_to_pdf(pptx_path, pdf_path)
        print(f"Wrote PDF: {pdf_path}")
    elif not pdf_path.exists():
        raise SystemExit(f"Missing PDF for --skip-pdf: {pdf_path}")

    render_pdf_to_png(pdf_path, png_path, dpi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
