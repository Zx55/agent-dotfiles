#!/usr/bin/env python3
"""Audit Codex tool output for leaked sensitive environment variable values."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any


SENSITIVE_NAME_RE = re.compile(
    r"^(?:[A-Za-z_][A-Za-z0-9_]*_(?:API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY|ACCESS_KEY|AUTH|CREDENTIALS)"
    r"|API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)$"
)
MIN_SECRET_LENGTH = 8
PLACEHOLDER_VALUES = {
    "changeme",
    "change_me",
    "example",
    "placeholder",
    "redacted",
    "secret",
    "test",
    "token",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Codex tool output for sensitive env value leaks."
    )
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Codex hook-compatible JSON on stdout.",
    )
    return parser.parse_args()


def read_hook_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def is_sensitive_name(name: str) -> bool:
    return bool(SENSITIVE_NAME_RE.match(name))


def is_secret_value(value: str) -> bool:
    stripped = value.strip()
    if len(stripped) < MIN_SECRET_LENGTH:
        return False
    if stripped.lower() in PLACEHOLDER_VALUES:
        return False
    return True


def candidate_secrets() -> dict[str, str]:
    result: dict[str, str] = {}
    for name, value in os.environ.items():
        if is_sensitive_name(name) and is_secret_value(value):
            result[name] = value
    return result


def command_from_input(hook_input: dict[str, Any]) -> str:
    tool_input = hook_input.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
    return ""


def text_fragments(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, bytes):
        return [value.decode("utf-8", errors="replace")]
    if isinstance(value, dict):
        fragments: list[str] = []
        for item in value.values():
            fragments.extend(text_fragments(item))
        return fragments
    if isinstance(value, list):
        fragments = []
        for item in value:
            fragments.extend(text_fragments(item))
        return fragments
    return [str(value)]


def output_from_input(hook_input: dict[str, Any]) -> str:
    return "\n".join(text_fragments(hook_input.get("tool_response")))


def command_summary(command: str) -> str:
    normalized = " ".join(command.split())
    if len(normalized) <= 120:
        return normalized
    return normalized[:117] + "..."


def audit_output(output: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for name, value in candidate_secrets().items():
        count = output.count(value)
        if count:
            findings.append(
                {
                    "name": name,
                    "count": count,
                    "value_length": len(value),
                }
            )
    return findings


def secret_values() -> list[str]:
    return sorted(candidate_secrets().values(), key=len, reverse=True)


def redact_text(text: str, values: list[str]) -> str:
    redacted = text
    for value in values:
        redacted = redacted.replace(value, "****** (replaced by secret guard)")
    return redacted


def redact_value(value: Any, values: list[str]) -> Any:
    if isinstance(value, str):
        return redact_text(value, values)
    if isinstance(value, bytes):
        return redact_text(value.decode("utf-8", errors="replace"), values)
    if isinstance(value, dict):
        return {key: redact_value(item, values) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_value(item, values) for item in value]
    return value


def format_redacted_response(response: Any, values: list[str]) -> str:
    redacted = redact_value(response, values)
    if isinstance(redacted, str):
        return redacted
    return json.dumps(redacted, ensure_ascii=False, indent=2)


def emit_diagnostics(command: str, findings: list[dict[str, Any]]) -> None:
    if not findings:
        return

    names = ", ".join(str(item["name"]) for item in findings)
    total = sum(int(item["count"]) for item in findings)
    print(
        "codex-secret-guard-tool-use-after: possible secret value leak detected; "
        f"matched_variables={names}; total_matches={total}; "
        f"command={command_summary(command)!r}",
        file=sys.stderr,
    )


def replacement_payload(
    command: str,
    response: Any,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    names = ", ".join(str(item["name"]) for item in findings)
    total = sum(int(item["count"]) for item in findings)
    redacted_response = format_redacted_response(response, secret_values())
    reason = (
        "Codex Secret Guard replaced sensitive environment values in Bash output. "
        f"matched_variables={names}; total_matches={total}; "
        f"command={command_summary(command)!r}.\n\n"
        f"{redacted_response}"
    )
    return {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": reason,
        },
    }


def main() -> int:
    args = parse_args()
    hook_input = read_hook_input()
    command = command_from_input(hook_input)
    tool_response = hook_input.get("tool_response")
    output = output_from_input(hook_input)
    findings = audit_output(output)

    emit_diagnostics(command, findings)
    if findings:
        payload = replacement_payload(command, tool_response, findings)
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
