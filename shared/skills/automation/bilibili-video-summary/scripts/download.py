#!/usr/bin/env python3
"""Download Bilibili metadata and optional audio/video into an owned run directory."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from _run import (
    ensure_run_dir,
    load_manifest,
    record_artifact,
    require_command,
    save_manifest,
    utc_now,
    yt_dlp_command,
)


SECTION_PATTERN = re.compile(r"^\d+(?:\.\d+)?-\d+(?:\.\d+)?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="One Bilibili video URL.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--audio", action="store_true", help="Download an M4A audio file.")
    parser.add_argument(
        "--video",
        action="store_true",
        help="Download a playable MP4 with audio.",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=720,
        help="Maximum video height. Default: 720.",
    )
    parser.add_argument(
        "--section",
        help="Optional test range in seconds, formatted START-END, for example 0-90.",
    )
    parser.add_argument(
        "--cookies-from-browser",
        help="Optional yt-dlp browser name for videos that require login.",
    )
    args = parser.parse_args()
    if not args.audio and not args.video:
        parser.error("Select at least one of --audio or --video.")
    if args.max_height <= 0:
        parser.error("--max-height must be positive.")
    if args.section and not SECTION_PATTERN.fullmatch(args.section):
        parser.error("--section must use numeric START-END seconds.")
    return args


def run_checked(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=capture,
    )


def common_download_args(args: argparse.Namespace) -> list[str]:
    result = ["--no-playlist", "--no-overwrites"]
    if args.section:
        result.extend(["--download-sections", f"*{args.section}"])
    if args.cookies_from_browser:
        result.extend(["--cookies-from-browser", args.cookies_from_browser])
    return result


def inspect_source(args: argparse.Namespace) -> dict[str, Any]:
    command = (
        yt_dlp_command()
        + ["--no-playlist", "--no-warnings", "--dump-single-json"]
    )
    if args.cookies_from_browser:
        command.extend(["--cookies-from-browser", args.cookies_from_browser])
    command.append(args.url)
    completed = run_checked(command, capture=True)
    raw = json.loads(completed.stdout)
    return {
        "id": raw.get("id"),
        "title": raw.get("title"),
        "uploader": raw.get("uploader"),
        "uploader_id": raw.get("uploader_id"),
        "duration": raw.get("duration"),
        "webpage_url": raw.get("webpage_url") or args.url,
        "timestamp": raw.get("timestamp"),
        "availability": raw.get("availability"),
        "extractor": raw.get("extractor"),
    }


def probe_media(path: Path) -> dict[str, Any]:
    ffprobe = require_command("ffprobe")
    completed = run_checked(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,format_name",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    data = json.loads(completed.stdout)["format"]
    return {
        "duration": round(float(data["duration"]), 3),
        "bytes": int(data["size"]),
        "format": data.get("format_name"),
    }


def locate_output(raw_dir: Path, stem: str) -> Path:
    candidates = sorted(
        path
        for path in raw_dir.glob(f"{stem}.*")
        if path.is_file() and not path.name.endswith((".part", ".ytdl"))
    )
    if len(candidates) != 1:
        raise SystemExit(
            f"Expected one {stem} output in {raw_dir}, found {len(candidates)}."
        )
    return candidates[0]


def download_audio(args: argparse.Namespace, raw_dir: Path) -> Path:
    command = yt_dlp_command() + common_download_args(args)
    command.extend(
        [
            "-f",
            "bestaudio",
            "-x",
            "--audio-format",
            "m4a",
            "-o",
            str(raw_dir / "audio.%(ext)s"),
            args.url,
        ]
    )
    run_checked(command)
    return locate_output(raw_dir, "audio")


def download_video(args: argparse.Namespace, raw_dir: Path) -> Path:
    format_selector = (
        f"bestvideo[height<={args.max_height}]+bestaudio/"
        f"best[height<={args.max_height}]"
    )
    command = yt_dlp_command() + common_download_args(args)
    command.extend(
        [
            "-f",
            format_selector,
            "--merge-output-format",
            "mp4",
            "-o",
            str(raw_dir / "video.%(ext)s"),
            args.url,
        ]
    )
    run_checked(command)
    return locate_output(raw_dir, "video")


def main() -> None:
    args = parse_args()
    run_dir = ensure_run_dir(args.run_dir, create=True)
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(run_dir)
    source = inspect_source(args)
    metadata_path = run_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(source, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest["source"] = source
    record_artifact(
        manifest,
        run_dir=run_dir,
        name="metadata",
        path=metadata_path,
        kind="metadata",
        ephemeral=False,
    )

    if args.audio:
        audio_path = download_audio(args, raw_dir)
        record_artifact(
            manifest,
            run_dir=run_dir,
            name="audio",
            path=audio_path,
            kind="audio",
            ephemeral=True,
            details=probe_media(audio_path),
        )

    if args.video:
        video_path = download_video(args, raw_dir)
        record_artifact(
            manifest,
            run_dir=run_dir,
            name="video",
            path=video_path,
            kind="video",
            ephemeral=True,
            details=probe_media(video_path),
        )

    manifest.setdefault("stages", {})["download"] = {
        "status": "complete",
        "completed_at": utc_now(),
        "section": args.section,
    }
    save_manifest(run_dir, manifest)
    print(json.dumps({"run_dir": str(run_dir), "source": source}, ensure_ascii=False))


if __name__ == "__main__":
    main()
