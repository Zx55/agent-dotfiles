#!/usr/bin/env python3
"""Ask before running shell commands that reference sensitive env names."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


SENSITIVE_NAME_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"("
    r"(?:[A-Za-z_][A-Za-z0-9_]*_(?:API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY|ACCESS_KEY|AUTH|CREDENTIALS))"
    r"|(?:API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)"
    r")"
    r"(?![A-Za-z0-9_])"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask before shell commands reference sensitive env names."
    )
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Cursor hook-compatible JSON on stdout.",
    )
    return parser.parse_args()


def read_hook_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def sensitive_names(command: str) -> list[str]:
    names = [match.group(1) for match in SENSITIVE_NAME_RE.finditer(command)]
    return sorted(dict.fromkeys(names))


def shell_command(hook_input: dict[str, Any]) -> str:
    command = hook_input.get("command")
    if isinstance(command, str):
        return command

    tool_input = hook_input.get("tool_input")
    if isinstance(tool_input, dict):
        tool_command = tool_input.get("command")
        if isinstance(tool_command, str):
            return tool_command

    return ""


def hook_event_name(hook_input: dict[str, Any]) -> str:
    event_name = hook_input.get("hook_event_name")
    if isinstance(event_name, str):
        return event_name
    if hook_input.get("tool_name") == "Shell":
        return "preToolUse"
    return ""


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def allow_payload(event_name: str) -> dict[str, str]:
    if event_name == "preToolUse":
        return {"permission": "allow"}
    return {"permission": "allow"}


def ask_payload(names: list[str]) -> dict[str, str]:
    joined = ", ".join(names)
    return {
        "permission": "ask",
        "user_message": (
            "This shell command references sensitive environment variable names: "
            f"{joined}. Approve only if the agent explained why it needs them "
            "and the command will not print or expose their values."
        ),
        "agent_message": (
            "Your shell command references sensitive environment variable names: "
            f"{joined}. Explain why you need to use them. Using variables is "
            "allowed for checks such as whether they are set, or for direct API "
            "calls, but you must not print their values or expose them into the "
            "conversation context."
        ),
    }


def main() -> int:
    parse_args()
    hook_input = read_hook_input()
    command = shell_command(hook_input)
    event_name = hook_event_name(hook_input)
    names = sensitive_names(command)

    if names:
        emit(ask_payload(names))
    else:
        emit(allow_payload(event_name))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
