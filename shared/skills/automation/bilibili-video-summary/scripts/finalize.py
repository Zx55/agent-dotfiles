#!/usr/bin/env python3
"""Validate durable outputs and optionally delete only downloaded raw media."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _run import (
    ensure_run_dir,
    load_manifest,
    record_artifact,
    resolve_artifact_path,
    save_manifest,
    utc_now,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--summary",
        type=Path,
        help="Summary Markdown path. Defaults to RUN_DIR/summary.md.",
    )
    parser.add_argument(
        "--delete-media",
        action="store_true",
        help="Delete ready ephemeral media after all validation passes.",
    )
    return parser.parse_args()


def load_nonempty_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"Missing or empty {label}: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{label} must contain a JSON object: {path}")
    return data


def validate_transcript(
    run_dir: Path,
    manifest: dict[str, Any],
) -> tuple[Path, int]:
    path = resolve_artifact_path(run_dir, manifest, "transcript_json")
    data = load_nonempty_json(path, "transcript")
    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        raise SystemExit("Transcript has no segments.")

    previous_end = -1.0
    for index, segment in enumerate(segments):
        start = float(segment["start"])
        end = float(segment["end"])
        if start < 0 or end <= start:
            raise SystemExit(f"Transcript segment {index} has invalid timestamps.")
        if start < previous_end - 0.5:
            raise SystemExit(f"Transcript segment {index} is out of order.")
        if not str(segment.get("text") or "").strip():
            raise SystemExit(f"Transcript segment {index} has empty text.")
        previous_end = end
    return path, len(segments)


def validate_frames(run_dir: Path, manifest: dict[str, Any]) -> int:
    artifact = manifest.get("artifacts", {}).get("frames_manifest")
    if not artifact or artifact.get("status") != "ready":
        return 0

    path = resolve_artifact_path(run_dir, manifest, "frames_manifest")
    data = load_nonempty_json(path, "frames manifest")
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        raise SystemExit("Frames manifest has no retained frames.")
    for frame in frames:
        relative = Path(frame["path"])
        if relative.is_absolute():
            raise SystemExit(f"Frame path must be relative: {relative}")
        image_path = (run_dir / relative).resolve()
        try:
            image_path.relative_to(run_dir)
        except ValueError as exc:
            raise SystemExit(f"Frame path escapes the run directory: {relative}") from exc
        if not image_path.is_file() or image_path.stat().st_size == 0:
            raise SystemExit(f"Missing or empty frame: {image_path}")
    return len(frames)


def delete_ephemeral_media(run_dir: Path, manifest: dict[str, Any]) -> list[str]:
    deleted: list[str] = []
    for name, artifact in manifest.get("artifacts", {}).items():
        if not artifact.get("ephemeral") or artifact.get("status") != "ready":
            continue
        relative = Path(artifact["path"])
        if relative.is_absolute() or not relative.parts or relative.parts[0] != "raw":
            raise SystemExit(
                f"Refusing to delete ephemeral artifact outside raw/: {relative}"
            )
        path = resolve_artifact_path(run_dir, manifest, name)
        if path.is_symlink():
            raise SystemExit(f"Refusing to delete symlinked media: {path}")
        if path.is_file():
            path.unlink()
        elif path.exists():
            raise SystemExit(f"Refusing to recursively delete media path: {path}")
        artifact["status"] = "deleted"
        artifact["deleted_at"] = utc_now()
        deleted.append(name)

    raw_dir = run_dir / "raw"
    if raw_dir.is_dir() and not any(raw_dir.iterdir()):
        raw_dir.rmdir()
    return deleted


def main() -> None:
    args = parse_args()
    run_dir = ensure_run_dir(args.run_dir, create=False)
    manifest = load_manifest(run_dir)

    metadata_path = resolve_artifact_path(run_dir, manifest, "metadata")
    load_nonempty_json(metadata_path, "metadata")
    transcript_path, segment_count = validate_transcript(run_dir, manifest)
    frame_count = validate_frames(run_dir, manifest)

    summary_path = (args.summary or (run_dir / "summary.md")).expanduser().resolve()
    try:
        summary_path.relative_to(run_dir)
    except ValueError as exc:
        raise SystemExit("Summary must be stored inside the run directory.") from exc
    if not summary_path.is_file() or not summary_path.read_text(encoding="utf-8").strip():
        raise SystemExit(f"Missing or empty summary: {summary_path}")

    record_artifact(
        manifest,
        run_dir=run_dir,
        name="summary",
        path=summary_path,
        kind="summary",
        ephemeral=False,
    )
    manifest.setdefault("stages", {})["validation"] = {
        "status": "complete",
        "completed_at": utc_now(),
        "transcript": str(transcript_path.relative_to(run_dir)),
        "segments": segment_count,
        "frames": frame_count,
    }

    deleted = delete_ephemeral_media(run_dir, manifest) if args.delete_media else []
    manifest["stages"]["finalization"] = {
        "status": "complete",
        "completed_at": utc_now(),
        "media_deleted": deleted,
    }
    save_manifest(run_dir, manifest)
    print(
        json.dumps(
            {
                "validated": True,
                "segments": segment_count,
                "frames": frame_count,
                "media_deleted": deleted,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
