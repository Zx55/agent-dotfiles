#!/usr/bin/env python3
"""Generate a URL QR code and optionally verify it with zbarimg."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

try:
    import segno
except ImportError as exc:  # pragma: no cover - exercised by missing envs
    raise SystemExit(
        "Missing dependency: segno. Install with: python3 -m pip install segno Pillow"
    ) from exc

try:
    from PIL import Image, ImageColor
except ImportError as exc:  # pragma: no cover - exercised by missing envs
    raise SystemExit(
        "Missing dependency: Pillow. Install with: python3 -m pip install segno Pillow"
    ) from exc


Format = Literal["png", "svg"]


def normalize_url(raw_url: str) -> str:
    url = raw_url.strip()
    if not url:
        raise ValueError("URL is empty")
    if "://" not in url:
        url = f"https://{url}"

    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http:// and https:// URLs are supported")
    if not parsed.netloc:
        raise ValueError("URL must include a host")
    if any(ch.isspace() for ch in url):
        raise ValueError("URL must not contain whitespace")
    return url


def infer_format(output_path: Path | None, requested_format: str | None) -> Format:
    if requested_format:
        return requested_format  # type: ignore[return-value]
    if output_path and output_path.suffix.lower() == ".svg":
        return "svg"
    return "png"


def default_output_path(url: str, output_format: Format) -> Path:
    parsed = urlsplit(url)
    host = parsed.netloc.replace(":", "-")
    safe_host = "".join(ch if ch.isalnum() or ch in ".-" else "-" for ch in host)
    return Path(f"{safe_host or 'url'}-qr.{output_format}")


def render_png(qr: segno.QRCode, output_path: Path, scale: int, border: int, dark: str, light: str) -> None:
    matrix = list(qr.matrix_iter(scale=scale, border=border))
    if not matrix:
        raise ValueError("QR matrix is empty")

    width = len(matrix[0])
    height = len(matrix)
    dark_rgba = ImageColor.getcolor(dark, "RGBA")
    light_rgba = ImageColor.getcolor(light, "RGBA")
    image = Image.new("RGBA", (width, height), light_rgba)
    pixels = image.load()

    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            if value:
                pixels[x, y] = dark_rgba

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def render_svg(qr: segno.QRCode, output_path: Path, scale: int, border: int, dark: str, light: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qr.save(
        str(output_path),
        kind="svg",
        scale=scale,
        border=border,
        dark=dark,
        light=light,
    )


def decode_with_zbar(image_path: Path) -> str:
    zbarimg = shutil.which("zbarimg")
    if not zbarimg:
        raise FileNotFoundError("zbarimg not found. Install with: brew install zbar")

    result = subprocess.run(
        [zbarimg, "--quiet", "--raw", str(image_path)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise RuntimeError(f"zbarimg failed: {detail}")

    decoded = result.stdout.rstrip("\n")
    if not decoded:
        raise RuntimeError("zbarimg decoded an empty value")
    return decoded


def validate_qr(
    qr: segno.QRCode,
    encoded_url: str,
    output_path: Path,
    output_format: Format,
    scale: int,
    border: int,
    dark: str,
    light: str,
) -> str:
    if output_format == "png":
        image_path = output_path
        temp_path = None
    else:
        temp_file = tempfile.NamedTemporaryFile(prefix="url-qr-code-", suffix=".png", delete=False)
        temp_path = Path(temp_file.name)
        temp_file.close()
        render_png(qr, temp_path, scale, border, dark, light)
        image_path = temp_path

    try:
        decoded = decode_with_zbar(image_path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    if decoded != encoded_url:
        raise RuntimeError(
            "QR validation failed: decoded value does not match normalized URL\n"
            f"expected: {encoded_url}\n"
            f"decoded:  {decoded}"
        )
    return decoded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local URL QR code.")
    parser.add_argument("url", help="URL to encode. Missing scheme defaults to https://")
    parser.add_argument("--out", type=Path, help="Output file path. Defaults to <host>-qr.png")
    parser.add_argument("--format", choices=["png", "svg"], help="Output format. Defaults to PNG unless --out ends in .svg")
    parser.add_argument("--scale", type=int, default=12, help="Module size in pixels or SVG units. Default: 12")
    parser.add_argument("--border", type=int, default=4, help="Quiet-zone border in modules. Default: 4")
    parser.add_argument("--error", choices=["L", "M", "Q", "H"], default="M", help="Error correction level. Default: M")
    parser.add_argument("--dark", default="#000000", help="Dark module color. Default: #000000")
    parser.add_argument("--light", default="#ffffff", help="Light module color. Default: #ffffff")
    parser.add_argument("--no-validate", action="store_true", help="Skip zbarimg validation")
    parser.add_argument("--strict-validate", action="store_true", help="Fail if validation cannot be performed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        normalized_url = normalize_url(args.url)
        output_format = infer_format(args.out, args.format)
        output_path = args.out or default_output_path(normalized_url, output_format)

        qr = segno.make(normalized_url, error=args.error, micro=False)
        if output_format == "png":
            render_png(qr, output_path, args.scale, args.border, args.dark, args.light)
        else:
            render_svg(qr, output_path, args.scale, args.border, args.dark, args.light)

        validation_status = "skipped"
        if not args.no_validate:
            try:
                validate_qr(
                    qr,
                    normalized_url,
                    output_path,
                    output_format,
                    args.scale,
                    args.border,
                    args.dark,
                    args.light,
                )
                validation_status = "passed"
            except FileNotFoundError as exc:
                if args.strict_validate:
                    raise
                validation_status = f"skipped ({exc})"

        print(f"normalized_url={normalized_url}")
        print(f"output={output_path}")
        print(f"format={output_format}")
        print(f"validation={validation_status}")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
