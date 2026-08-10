#!/usr/bin/env python3
"""Estimate section timing from MLX Whisper JSON using marker phrases."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Token:
    text: str
    start: float
    end: float


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tokens_from_words(data: dict[str, Any]) -> list[Token]:
    tokens: list[Token] = []
    for segment in data.get("segments", []):
        for word in segment.get("words", []) or []:
            raw = word.get("word") or word.get("text") or ""
            start = word.get("start")
            end = word.get("end")
            if raw and start is not None and end is not None:
                for part in normalize(raw).split():
                    tokens.append(Token(part, float(start), float(end)))
    return tokens


def tokens_from_segments(data: dict[str, Any]) -> list[Token]:
    tokens: list[Token] = []
    for segment in data.get("segments", []):
        text = normalize(segment.get("text") or "")
        words = text.split()
        if not words:
            continue
        start = float(segment["start"])
        end = float(segment["end"])
        span = max(end - start, 0.001)
        for index, word in enumerate(words):
            word_start = start + span * index / len(words)
            word_end = start + span * (index + 1) / len(words)
            tokens.append(Token(word, word_start, word_end))
    return tokens


def find_marker(tokens: list[Token], marker: str) -> float:
    marker_words = normalize(marker).split()
    if not marker_words:
        raise SystemExit("Marker is empty after normalization.")
    for index in range(0, len(tokens) - len(marker_words) + 1):
        if [token.text for token in tokens[index : index + len(marker_words)]] == marker_words:
            return tokens[index].start
    raise SystemExit(f"Marker not found: {marker}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", type=Path, required=True, help="MLX Whisper JSON path."
    )
    parser.add_argument("--start", required=True, help="Start marker phrase.")
    parser.add_argument("--end", help="Optional end marker phrase.")
    args = parser.parse_args()

    data = load_json(args.json)
    tokens = tokens_from_words(data)
    source = "words"
    if not tokens:
        tokens = tokens_from_segments(data)
        source = "segments"
    if not tokens:
        raise SystemExit("No timed words or segments found in MLX Whisper JSON.")

    start = find_marker(tokens, args.start)
    result: dict[str, Any] = {"source": source, "start": round(start, 3)}
    if args.end:
        end = find_marker(tokens, args.end)
        result["end"] = round(end, 3)
        result["duration"] = round(end - start, 3)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
