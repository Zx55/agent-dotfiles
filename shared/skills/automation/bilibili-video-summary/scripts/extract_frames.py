#!/usr/bin/env python3
"""Extract deduplicated screenshots requested from timestamped transcript sections."""

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
    resolve_artifact_path,
    save_manifest,
    utc_now,
)


PTS_PATTERN = re.compile(r"pts_time:([0-9]+(?:\.[0-9]+)?)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--requests",
        type=Path,
        required=True,
        help="JSON containing a `requests` list with timestamps and reasons.",
    )
    parser.add_argument(
        "--scene-window",
        type=float,
        default=1.5,
        help="Use the nearest scene cut within this many seconds. Set 0 to disable.",
    )
    parser.add_argument("--scene-threshold", type=float, default=0.35)
    parser.add_argument(
        "--scene-offset",
        type=float,
        default=0.15,
        help="Move slightly after a detected scene cut. Default: 0.15.",
    )
    parser.add_argument("--max-frames", type=int, default=30)
    parser.add_argument(
        "--duplicate-distance",
        type=int,
        default=6,
        help="Maximum 256-bit average-hash distance treated as a duplicate.",
    )
    args = parser.parse_args()
    if args.scene_window < 0:
        parser.error("--scene-window cannot be negative.")
    if not 0 < args.scene_threshold < 1:
        parser.error("--scene-threshold must be between 0 and 1.")
    if args.max_frames <= 0:
        parser.error("--max-frames must be positive.")
    if args.duplicate_distance < 0:
        parser.error("--duplicate-distance cannot be negative.")
    return args


def load_requests(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    requests = data.get("requests") if isinstance(data, dict) else data
    if not isinstance(requests, list) or not requests:
        raise SystemExit("Frame request JSON must contain a non-empty `requests` list.")

    normalized: list[dict[str, Any]] = []
    for index, request in enumerate(requests):
        if not isinstance(request, dict) or "timestamp" not in request:
            raise SystemExit(f"Frame request {index} is missing `timestamp`.")
        timestamp = float(request["timestamp"])
        if timestamp < 0:
            raise SystemExit(f"Frame request {index} has a negative timestamp.")
        normalized.append(
            {
                "timestamp": timestamp,
                "segment_id": request.get("segment_id"),
                "reason": str(request.get("reason") or "").strip(),
            }
        )
    return normalized


def media_duration(ffprobe: str, path: Path) -> float:
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return float(completed.stdout.strip())


def detect_scene_times(
    ffmpeg: str,
    video_path: Path,
    *,
    threshold: float,
) -> list[float]:
    filter_expression = f"select='gt(scene,{threshold})',showinfo"
    completed = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-i",
            str(video_path),
            "-vf",
            filter_expression,
            "-fps_mode",
            "vfr",
            "-f",
            "null",
            "-",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return [float(match) for match in PTS_PATTERN.findall(completed.stderr)]


def choose_timestamp(
    requested: float,
    scene_times: list[float],
    *,
    window: float,
    offset: float,
    duration: float,
) -> tuple[float, bool]:
    nearby = [timestamp for timestamp in scene_times if abs(timestamp - requested) <= window]
    if nearby:
        selected = min(nearby, key=lambda timestamp: abs(timestamp - requested)) + offset
        return min(max(selected, 0.0), max(duration - 0.01, 0.0)), True
    return min(requested, max(duration - 0.01, 0.0)), False


def extract_frame(ffmpeg: str, video_path: Path, timestamp: float, output: Path) -> None:
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-ss",
            f"{timestamp:.3f}",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-y",
            str(output),
        ],
        check=True,
    )
    if not output.is_file() or output.stat().st_size == 0:
        raise SystemExit(f"FFmpeg did not produce a frame: {output}")


def average_hash(ffmpeg: str, image_path: Path) -> int:
    completed = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(image_path),
            "-vf",
            "scale=16:16,format=gray",
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-",
        ],
        check=True,
        capture_output=True,
    )
    pixels = completed.stdout
    if len(pixels) != 256:
        raise SystemExit(f"Could not calculate an image hash for {image_path}.")
    mean = sum(pixels) / len(pixels)
    result = 0
    for value in pixels:
        result = (result << 1) | int(value >= mean)
    return result


def is_duplicate(candidate: int, existing: list[int], max_distance: int) -> bool:
    return any((candidate ^ value).bit_count() <= max_distance for value in existing)


def main() -> None:
    args = parse_args()
    run_dir = ensure_run_dir(args.run_dir, create=False)
    manifest = load_manifest(run_dir)
    video_path = resolve_artifact_path(run_dir, manifest, "video")
    if not video_path.is_file():
        raise SystemExit(f"Downloaded video is missing: {video_path}")

    requests_path = args.requests.expanduser().resolve()
    requests = load_requests(requests_path)
    if len(requests) > args.max_frames:
        raise SystemExit(
            f"Requested {len(requests)} frames, exceeding --max-frames {args.max_frames}."
        )

    ffmpeg = require_command("ffmpeg")
    ffprobe = require_command("ffprobe")
    duration = media_duration(ffprobe, video_path)
    scene_times = (
        detect_scene_times(
            ffmpeg,
            video_path,
            threshold=args.scene_threshold,
        )
        if args.scene_window > 0
        else []
    )

    frames_dir = run_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    hashes: list[int] = []
    frame_records: list[dict[str, Any]] = []
    duplicates = 0

    for request in requests:
        requested = float(request["timestamp"])
        if requested >= duration:
            raise SystemExit(
                f"Requested timestamp {requested:.3f}s exceeds video duration {duration:.3f}s."
            )
        actual, adjusted = choose_timestamp(
            requested,
            scene_times,
            window=args.scene_window,
            offset=args.scene_offset,
            duration=duration,
        )
        frame_number = len(frame_records) + 1
        output = frames_dir / f"frame-{frame_number:03d}-{actual:010.3f}.jpg"
        extract_frame(ffmpeg, video_path, actual, output)
        image_hash = average_hash(ffmpeg, output)
        if is_duplicate(image_hash, hashes, args.duplicate_distance):
            output.unlink()
            duplicates += 1
            continue

        hashes.append(image_hash)
        frame_records.append(
            {
                "id": f"frame-{frame_number:03d}",
                "path": str(output.relative_to(run_dir)),
                "requested_time": round(requested, 3),
                "actual_time": round(actual, 3),
                "scene_adjusted": adjusted,
                "segment_id": request["segment_id"],
                "reason": request["reason"],
            }
        )

    if not frame_records:
        raise SystemExit("All requested frames were duplicates; no screenshots were retained.")

    frames_manifest_path = frames_dir / "frames.json"
    frames_manifest = {
        "source_video": str(video_path.relative_to(run_dir)),
        "requests_source": str(requests_path),
        "scene_threshold": args.scene_threshold,
        "scene_window": args.scene_window,
        "frames": frame_records,
        "duplicates_skipped": duplicates,
    }
    frames_manifest_path.write_text(
        json.dumps(frames_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    record_artifact(
        manifest,
        run_dir=run_dir,
        name="frames_manifest",
        path=frames_manifest_path,
        kind="frames",
        ephemeral=False,
        details={"frames": len(frame_records), "duplicates_skipped": duplicates},
    )
    manifest.setdefault("stages", {})["frames"] = {
        "status": "complete",
        "completed_at": utc_now(),
        "frames": len(frame_records),
        "duplicates_skipped": duplicates,
    }
    save_manifest(run_dir, manifest)
    print(
        json.dumps(
            {
                "frames_manifest": str(frames_manifest_path),
                "frames": len(frame_records),
                "duplicates_skipped": duplicates,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
