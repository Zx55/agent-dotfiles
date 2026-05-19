"""Command-line entrypoint for mcp-launcher."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


_ENV_REF_RE = re.compile(r"\$(?:\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|(?P<plain>[A-Za-z_][A-Za-z0-9_]*))")


class LauncherError(RuntimeError):
    """Raised when launcher input cannot be resolved safely."""


@dataclass(frozen=True)
class LaunchPlan:
    """Resolved command and environment ready for exec."""

    command: str
    argv: tuple[str, ...]
    env: dict[str, str]


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="mcp-launcher",
        description="Launch an MCP server with portable path and environment expansion.",
    )
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Set an environment variable after expanding ~ and $VAR references.",
    )
    parser.add_argument(
        "--env-file",
        action="append",
        default=[],
        metavar="PATH",
        help="Load simple KEY=VALUE or export KEY=VALUE entries before --env expansion.",
    )
    parser.add_argument(
        "--allow-missing-env",
        action="store_true",
        help="Expand missing $VAR references to an empty string instead of failing.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to exec. Prefix with -- when the command has launcher-like flags.",
    )
    parsed = parser.parse_args(argv)
    if parsed.command and parsed.command[0] == "--":
        parsed.command = parsed.command[1:]
    if not parsed.command:
        parser.error("missing command after --")
    return parsed


def expand_value(value: str, env: Mapping[str, str], *, allow_missing_env: bool) -> str:
    """Expand ~ and shell-style variable references using a controlled env map."""
    expanded = expand_home(value, env)

    def replace_var(match: re.Match[str]) -> str:
        name = match.group("braced") or match.group("plain")
        if name in env:
            return env[name]
        if allow_missing_env:
            return ""
        raise LauncherError(f"environment variable ${name} is not set")

    return _ENV_REF_RE.sub(replace_var, expanded)


def expand_home(value: str, env: Mapping[str, str]) -> str:
    """Expand the current user's home with the target env, not the launcher env."""
    home = env.get("HOME")
    if home and value == "~":
        return home
    if home and value.startswith("~/"):
        return f"{home}{value[1:]}"
    return os.path.expanduser(value)


def parse_env_assignment(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise LauncherError(f"--env must be KEY=VALUE, got: {raw}")
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
        raise LauncherError(f"invalid environment variable name: {key!r}")
    return key, value


def parse_env_file(path: str, env: Mapping[str, str], *, allow_missing_env: bool) -> dict[str, str]:
    resolved_path = Path(expand_value(path, env, allow_missing_env=allow_missing_env))
    values: dict[str, str] = {}
    try:
        lines = resolved_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise LauncherError(f"failed to read env file {resolved_path}: {exc}") from exc

    merged_env = dict(env)
    for line in lines:
        parsed = parse_env_file_line(line)
        if parsed is None:
            continue
        key, raw_value = parsed
        value = expand_value(raw_value, {**merged_env, **values}, allow_missing_env=allow_missing_env)
        values[key] = value
    return values


def parse_env_file_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()
    if "=" not in stripped:
        raise LauncherError(f"env-file line is not KEY=VALUE: {line!r}")
    key, raw_value = stripped.split("=", 1)
    key = key.strip()
    if not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
        raise LauncherError(f"invalid environment variable name in env file: {key!r}")
    return key, parse_env_file_value(raw_value.strip())


def parse_env_file_value(raw_value: str) -> str:
    if not raw_value:
        return ""
    if raw_value[0] in {"'", '"'}:
        try:
            parts = shlex.split(raw_value, comments=False, posix=True)
        except ValueError as exc:
            raise LauncherError(f"invalid quoted env-file value: {raw_value!r}") from exc
        if len(parts) != 1:
            raise LauncherError(f"env-file value must be a single token: {raw_value!r}")
        return parts[0]
    return raw_value


def build_launch_plan(parsed: argparse.Namespace, base_env: Mapping[str, str] | None = None) -> LaunchPlan:
    env = dict(os.environ if base_env is None else base_env)
    allow_missing = bool(parsed.allow_missing_env)

    for env_file in parsed.env_file:
        env.update(parse_env_file(env_file, env, allow_missing_env=allow_missing))

    for assignment in parsed.env:
        key, raw_value = parse_env_assignment(assignment)
        env[key] = expand_value(raw_value, env, allow_missing_env=allow_missing)

    argv = tuple(expand_value(part, env, allow_missing_env=allow_missing) for part in parsed.command)
    if not argv:
        raise LauncherError("missing command")
    return LaunchPlan(command=argv[0], argv=argv, env=env)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        parsed = parse_args(sys.argv[1:] if argv is None else argv)
        plan = build_launch_plan(parsed)
    except LauncherError as exc:
        print(f"mcp-launcher: {exc}", file=sys.stderr)
        return 2

    os.execvpe(plan.command, plan.argv, plan.env)
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
