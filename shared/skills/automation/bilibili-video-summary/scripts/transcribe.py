#!/usr/bin/env python3
"""Transcribe a run's downloaded audio with MLX Whisper."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from _run import (
    ensure_run_dir,
    load_manifest,
    mlx_whisper_command,
    record_artifact,
    resolve_artifact_path,
    save_manifest,
    utc_now,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--language", default="zh")
    parser.add_argument("--model", default="mlx-community/whisper-small-mlx")
    parser.add_argument(
        "--word-timestamps",
        action="store_true",
        help="Generate attention-derived word timestamps in addition to segments.",
    )
    return parser.parse_args()


def format_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def write_markdown(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# Transcript",
        "",
        f"Language: `{data.get('language', 'unknown')}`",
        "",
    ]
    for segment in data["segments"]:
        start = format_timestamp(float(segment["start"]))
        end = format_timestamp(float(segment["end"]))
        text = str(segment.get("text", "")).strip()
        lines.append(f"- [{start} – {end}] {text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_segments(
    data: dict[str, Any], *, require_words: bool
) -> tuple[list[dict[str, Any]], int]:
    segments = data.get("segments") or []
    if not segments:
        raise SystemExit("MLX Whisper produced no transcript segments.")

    for index, segment in enumerate(segments):
        segment.setdefault("id", index)
        if "start" not in segment or "end" not in segment:
            raise SystemExit(f"Segment {index} has no start/end timestamp.")

    timed_words = [
        word
        for segment in segments
        for word in (segment.get("words") or [])
        if word.get("word")
        and word.get("start") is not None
        and word.get("end") is not None
    ]
    if require_words and not timed_words:
        raise SystemExit(
            "Word timestamps were requested but MLX Whisper produced no timed words."
        )
    return segments, len(timed_words)


def main() -> None:
    args = parse_args()
    run_dir = ensure_run_dir(args.run_dir, create=False)
    manifest = load_manifest(run_dir)
    audio_path = resolve_artifact_path(run_dir, manifest, "audio")
    if not audio_path.is_file():
        raise SystemExit(f"Downloaded audio is missing: {audio_path}")

    output_dir = run_dir / "transcript"
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".mlx-whisper-", dir=output_dir
    ) as temporary:
        temporary_dir = Path(temporary)
        command = mlx_whisper_command() + [
            str(audio_path),
            "--model",
            args.model,
            "--language",
            args.language,
            "--task",
            "transcribe",
            "--temperature",
            "0",
            "--condition-on-previous-text",
            "False",
            "--fp16",
            "True",
            "--word-timestamps",
            str(args.word_timestamps),
            "--output-dir",
            str(temporary_dir),
            "--output-format",
            "json",
            "--verbose",
            "False",
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                f"MLX Whisper transcription failed with exit code {exc.returncode}."
            ) from exc

        generated_path = temporary_dir / f"{audio_path.stem}.json"
        if not generated_path.is_file():
            raise SystemExit(
                f"MLX Whisper did not create its expected JSON: {generated_path}"
            )
        data = json.loads(generated_path.read_text(encoding="utf-8"))
        segments, word_count = validate_segments(
            data, require_words=args.word_timestamps
        )
        data["_bilibili_video_summary"] = {
            "source_audio": str(audio_path.relative_to(run_dir)),
            "backend": "mlx-whisper",
            "model": args.model,
            "timing": "word" if args.word_timestamps else "segment",
        }
        generated_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        transcript_path = output_dir / "transcript.json"
        generated_path.replace(transcript_path)

    markdown_path = output_dir / "transcript.md"
    write_markdown(markdown_path, data)

    record_artifact(
        manifest,
        run_dir=run_dir,
        name="transcript_json",
        path=transcript_path,
        kind="transcript",
        ephemeral=False,
        details={"segments": len(segments), "timed_words": word_count},
    )
    record_artifact(
        manifest,
        run_dir=run_dir,
        name="transcript_markdown",
        path=markdown_path,
        kind="transcript",
        ephemeral=False,
    )
    manifest.setdefault("stages", {})["transcription"] = {
        "status": "complete",
        "completed_at": utc_now(),
        "backend": "mlx-whisper",
        "model": args.model,
        "language": data.get("language") or args.language,
        "timing": "word" if args.word_timestamps else "segment",
    }
    save_manifest(run_dir, manifest)
    print(
        json.dumps(
            {
                "transcript": str(transcript_path),
                "segments": len(segments),
                "timed_words": word_count,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
