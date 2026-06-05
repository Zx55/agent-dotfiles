#!/usr/bin/env python3
"""Audit shell output for leaked sensitive environment variable values."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
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
        description="Audit shell output for sensitive env value leaks."
    )
    parser.add_argument(
        "--hook-output",
        action="store_true",
        help="Emit Cursor hook-compatible JSON on stdout.",
    )
    parser.add_argument(
        "--mac-notify",
        action="store_true",
        help="Show a macOS notification when a possible leak is detected.",
    )
    parser.add_argument(
        "--test-notify",
        action="store_true",
        help="Send a benign macOS test notification and exit.",
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


def command_summary(command: str) -> str:
    normalized = " ".join(command.split())
    if len(normalized) <= 120:
        return normalized
    return normalized[:117] + "..."


def value_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def command_from_input(hook_input: dict[str, Any]) -> str:
    command = hook_input.get("command")
    if isinstance(command, str):
        return command

    tool_input = hook_input.get("tool_input")
    if isinstance(tool_input, dict):
        tool_command = tool_input.get("command")
        if isinstance(tool_command, str):
            return tool_command

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


def parse_json_text(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def output_from_input(hook_input: dict[str, Any]) -> str:
    fragments: list[str] = []

    output = hook_input.get("output")
    if isinstance(output, str):
        fragments.append(output)

    tool_output = hook_input.get("tool_output")
    if isinstance(tool_output, str):
        fragments.extend(text_fragments(parse_json_text(tool_output)))
    elif tool_output is not None:
        fragments.extend(text_fragments(tool_output))

    error_message = hook_input.get("error_message")
    if isinstance(error_message, str):
        fragments.append(error_message)

    return "\n".join(fragment for fragment in fragments if fragment)


def audit_output(command: str, output: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for name, value in candidate_secrets().items():
        count = output.count(value)
        if count:
            findings.append(
                {
                    "name": name,
                    "count": count,
                    "value_length": len(value),
                    "value_sha256_prefix": value_hash(value),
                }
            )
    return findings


def emit_diagnostics(command: str, findings: list[dict[str, Any]]) -> None:
    if not findings:
        return

    names = ", ".join(str(item["name"]) for item in findings)
    total = sum(int(item["count"]) for item in findings)
    print(
        "cursor-secret-guard-tool-use-after: possible secret value leak detected; "
        f"matched_variables={names}; total_matches={total}; "
        f"command={command_summary(command)!r}",
        file=sys.stderr,
    )


def send_mac_notification(title: str, subtitle: str, message: str) -> None:
    try:
        subprocess.run(
            [
                "/usr/bin/osascript",
                "-e",
                (
                    "display notification "
                    f"{json.dumps(message)} "
                    f"with title {json.dumps(title)} "
                    f"subtitle {json.dumps(subtitle)}"
                ),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(
            f"cursor-secret-guard-tool-use-after: mac notification failed: {exc}",
            file=sys.stderr,
        )


def mac_notify(findings: list[dict[str, Any]]) -> None:
    if not findings:
        return

    names = ", ".join(str(item["name"]) for item in findings)
    total = sum(int(item["count"]) for item in findings)
    send_mac_notification(
        "Cursor Secret Guard",
        "Possible sensitive output detected",
        f"Matched {total} occurrence(s): {names}",
    )


def test_notify() -> None:
    send_mac_notification(
        "Cursor Secret Guard",
        "Notification test",
        "macOS notification delivery is working.",
    )


def main() -> int:
    args = parse_args()
    if args.test_notify:
        test_notify()
        print("{}")
        return 0

    hook_input = read_hook_input()
    command = command_from_input(hook_input)
    output = output_from_input(hook_input)
    findings = audit_output(command, output)

    emit_diagnostics(command, findings)
    if args.mac_notify:
        mac_notify(findings)
    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
