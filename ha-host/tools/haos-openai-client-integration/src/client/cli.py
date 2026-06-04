from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from .client import HaosOpenAIClient
from .config import ApiMode, OpenAIClientConfig


def main() -> None:
    parser = argparse.ArgumentParser(prog="haos-openai-client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prompt_parser = subparsers.add_parser("prompt", help="Generate text or JSON data.")
    prompt_parser.add_argument("--api-key")
    prompt_parser.add_argument("--base-url")
    prompt_parser.add_argument("--model", default=None)
    prompt_parser.add_argument(
        "--api-mode",
        choices=("chat_completions", "responses"),
        default="chat_completions",
    )
    prompt_parser.add_argument("--timeout-seconds", type=float, default=30.0)
    prompt_parser.add_argument("--temperature", type=float)
    prompt_parser.add_argument("--max-tokens", type=int)
    prompt_parser.add_argument("--system-prompt")
    prompt_parser.add_argument("--json-schema", type=Path)
    prompt_parser.add_argument("--schema-name", default="haos_response")
    prompt_parser.add_argument("--prompt", required=True)

    args = parser.parse_args()
    if args.command == "prompt":
        asyncio.run(_run_prompt(args))


async def _run_prompt(args: argparse.Namespace) -> None:
    schema: dict[str, Any] | None = None
    if args.json_schema is not None:
        schema = json.loads(args.json_schema.read_text(encoding="utf-8"))

    config = OpenAIClientConfig.from_env(
        api_key=args.api_key,
        model=args.model,
        base_url=args.base_url,
        api_mode=_api_mode(args.api_mode),
        timeout_seconds=args.timeout_seconds,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    client = HaosOpenAIClient(config)
    result = await client.generate(
        args.prompt,
        system_prompt=args.system_prompt,
        json_schema=schema,
        schema_name=args.schema_name,
    )
    if result.structured:
        print(json.dumps(result.data, ensure_ascii=False, indent=2))
    else:
        print(result.content)


def _api_mode(value: str) -> ApiMode:
    if value in ("chat_completions", "responses"):
        return value
    raise ValueError(f"Unsupported api_mode: {value}")
