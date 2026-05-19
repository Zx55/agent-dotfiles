#!/usr/bin/env python3
"""Synthesize fixed TTS audio through an OpenAI-compatible chat-audio API."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-tts"
DEFAULT_FORMAT = "wav"
DEFAULT_VOICE = "mimo_default"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate fixed text-to-speech audio from text or a .txt file."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Path to a UTF-8 text file.")
    source.add_argument("--text", help="Raw text to synthesize.")
    parser.add_argument("--output", type=Path, required=True, help="Output audio path.")
    parser.add_argument(
        "--script-output",
        type=Path,
        help=(
            "Optional path for the final narration text actually sent to TTS. "
            "Defaults to the output audio path with a .txt suffix."
        ),
    )
    parser.add_argument(
        "--style",
        default="",
        help="Optional style, tone, pacing, or delivery instructions.",
    )
    parser.add_argument(
        "--voice",
        help=(
            "Optional provider voice name or identifier. "
            f"Default when omitted: {DEFAULT_VOICE}."
        ),
    )
    parser.add_argument(
        "--format",
        default=DEFAULT_FORMAT,
        help=f"Output audio format requested from the provider. Default: {DEFAULT_FORMAT}.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional manifest JSON path. Defaults to output path with .json suffix.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print a sanitized request summary without calling the API.",
    )
    return parser.parse_args()



def normalize_base_url(base_url: str) -> str:
    """Normalize known MiMo hosts to their OpenAI-compatible /v1 endpoint."""
    normalized = base_url.rstrip("/")
    if normalized in {
        "https://token-plan-cn.xiaomimimo.com",
        "https://api.xiaomimimo.com",
    }:
        return f"{normalized}/v1"
    return normalized


def require_env() -> tuple[str, str, str]:
    api_key = os.environ.get("TTS_GEN_API_KEY")
    if not api_key:
        raise SystemExit("Missing required environment variable: TTS_GEN_API_KEY")

    base_url = normalize_base_url(os.environ.get("TTS_GEN_BASE_URL") or DEFAULT_BASE_URL)
    model = os.environ.get("TTS_GEN_MODEL") or DEFAULT_MODEL
    return api_key, base_url, model


def read_text(args: argparse.Namespace) -> str:
    if args.input is not None:
        text = args.input.read_text(encoding="utf-8")
    else:
        text = args.text or ""

    text = text.strip()
    if not text:
        raise SystemExit("Input text is empty.")
    return text


def build_request(
    *,
    model: str,
    text: str,
    style: str,
    audio_format: str,
    voice: str | None,
) -> dict[str, Any]:
    messages: list[dict[str, str]] = []
    if style.strip():
        messages.append({"role": "user", "content": style.strip()})
    messages.append({"role": "assistant", "content": text})

    audio: dict[str, Any] = {"format": audio_format}
    if voice:
        audio["voice"] = voice

    return {
        "model": model,
        "messages": messages,
        "audio": audio,
    }


def sanitized_summary(
    *,
    base_url: str,
    request: dict[str, Any],
    text: str,
    output: Path,
    manifest: Path,
    script_output: Path,
) -> dict[str, Any]:
    summary = {
        "base_url": base_url,
        "model": request["model"],
        "audio": request["audio"],
        "message_roles": [message["role"] for message in request["messages"]],
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text_chars": len(text),
        "output": str(output),
        "manifest": str(manifest),
        "script_output": str(script_output),
    }
    return summary


def write_manifest(
    *,
    manifest_path: Path,
    base_url: str,
    request: dict[str, Any],
    text: str,
    output_path: Path,
    output_bytes: int | None,
    dry_run: bool,
    script_output: Path,
) -> None:
    manifest = sanitized_summary(
        base_url=base_url,
        request=request,
        text=text,
        output=output_path,
        manifest=manifest_path,
        script_output=script_output,
    )
    manifest["dry_run"] = dry_run
    manifest["output_bytes"] = output_bytes
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def synthesize(api_key: str, base_url: str, request: dict[str, Any]) -> bytes:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit(
            "Missing Python package: openai. Install it with `python3 -m pip install openai`."
        ) from exc

    client = OpenAI(api_key=api_key, base_url=base_url)
    completion = client.chat.completions.create(**request)
    message = completion.choices[0].message
    audio = getattr(message, "audio", None)
    if audio is None:
        raise SystemExit("Provider response did not include message.audio.")

    data = getattr(audio, "data", None)
    if data is None and isinstance(audio, dict):
        data = audio.get("data")
    if not data:
        raise SystemExit("Provider response did not include message.audio.data.")

    return base64.b64decode(data)


def main() -> None:
    args = parse_args()
    api_key, base_url, model = require_env()
    text = read_text(args)
    output_path = args.output
    script_output_path = args.script_output or output_path.with_suffix(".txt")
    manifest_path = args.manifest or output_path.with_suffix(".json")
    script_output_path.parent.mkdir(parents=True, exist_ok=True)
    script_output_path.write_text(text + "\n", encoding="utf-8")
    request = build_request(
        model=model,
        text=text,
        style=args.style,
        audio_format=args.format,
        voice=args.voice or DEFAULT_VOICE,
    )

    if args.dry_run:
        summary = sanitized_summary(
            base_url=base_url,
            request=request,
            text=text,
            output=output_path,
            manifest=manifest_path,
            script_output=script_output_path,
        )
        print(json.dumps(summary, indent=2))
        write_manifest(
            manifest_path=manifest_path,
            base_url=base_url,
            request=request,
            text=text,
            output_path=output_path,
            output_bytes=None,
            dry_run=True,
            script_output=script_output_path,
        )
        return

    audio_bytes = synthesize(api_key=api_key, base_url=base_url, request=request)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio_bytes)
    write_manifest(
        manifest_path=manifest_path,
        base_url=base_url,
        request=request,
        text=text,
        output_path=output_path,
        output_bytes=len(audio_bytes),
        dry_run=False,
        script_output=script_output_path,
    )
    print(f"Wrote {output_path} ({len(audio_bytes)} bytes)")
    print(f"Wrote {script_output_path}")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
