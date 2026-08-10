#!/usr/bin/env python3
"""Generate validated MLX Whisper timestamps for fixed narration audio."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="mlx-community/whisper-tiny")
    parser.add_argument("--language", default="en")
    parser.add_argument(
        "--timing",
        choices=("segment", "word"),
        default="word",
        help="Generate segment timestamps or attention-derived word timestamps.",
    )
    return parser.parse_args()


def mlx_whisper_command() -> str:
    global_tool = Path.home() / ".local" / "bin" / "mlx_whisper"
    if global_tool.is_file():
        return str(global_tool)
    direct = shutil.which("mlx_whisper")
    if direct:
        return direct
    raise SystemExit(
        "Missing MLX Whisper. Install the global tool with "
        "`uv tool install mlx-whisper`."
    )


def validate_result(data: dict[str, Any], *, require_words: bool) -> tuple[int, int]:
    segments = data.get("segments") or []
    if not segments:
        raise SystemExit("MLX Whisper produced no transcript segments.")
    for index, segment in enumerate(segments):
        segment.setdefault("id", index)
        if "start" not in segment or "end" not in segment:
            raise SystemExit(f"Segment {index} has no start/end timestamp.")
    words = [
        word
        for segment in segments
        for word in (segment.get("words") or [])
        if word.get("word")
        and word.get("start") is not None
        and word.get("end") is not None
    ]
    if require_words and not words:
        raise SystemExit("Word timing was requested but MLX Whisper produced no words.")
    return len(segments), len(words)


def main() -> None:
    args = parse_args()
    audio_path = args.audio.expanduser().resolve()
    if not audio_path.is_file():
        raise SystemExit(f"Audio is missing: {audio_path}")

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    word_timestamps = args.timing == "word"
    with tempfile.TemporaryDirectory(
        prefix=".mlx-whisper-", dir=output_dir
    ) as temporary:
        temporary_dir = Path(temporary)
        command = [
            mlx_whisper_command(),
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
            str(word_timestamps),
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
        segment_count, word_count = validate_result(
            data, require_words=word_timestamps
        )
        data["_tts_align"] = {
            "source_audio": str(audio_path),
            "backend": "mlx-whisper",
            "model": args.model,
            "timing": args.timing,
        }
        result_path = output_dir / f"{audio_path.stem}.json"
        generated_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        generated_path.replace(result_path)

    print(
        json.dumps(
            {
                "transcript": str(result_path),
                "segments": segment_count,
                "timed_words": word_count,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
