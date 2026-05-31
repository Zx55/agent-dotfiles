from __future__ import annotations

import ipaddress
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence


MAC_RE = re.compile(r"^[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}$")
IPV4_RE = re.compile(r"^([0-9]{1,3}\.){3}[0-9]{1,3}$")


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def run_command(args: Sequence[str], timeout: int = 20) -> CommandResult:
    try:
        proc = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        command = " ".join(args)
        return CommandResult(124, stdout, stderr or f"command timed out after {timeout}s: {command}\n")
    return CommandResult(proc.returncode, proc.stdout, proc.stderr)


def die(message: str) -> None:
    print(f"mac-router.py: error: {message}", file=sys.stderr)
    raise SystemExit(1)


def normalize_mac(value: str) -> str:
    value = value.strip().lower()
    if not MAC_RE.match(value):
        die(f"invalid MAC address: {value}")
    return value


def normalize_loose_mac(value: str) -> str:
    parts = value.strip().lower().split(":")
    if len(parts) != 6:
        die(f"invalid MAC address: {value}")
    normalized: list[str] = []
    for part in parts:
        if not part or len(part) > 2:
            die(f"invalid MAC address: {value}")
        try:
            octet = int(part, 16)
        except ValueError:
            die(f"invalid MAC address: {value}")
        normalized.append(f"{octet:02x}")
    return ":".join(normalized)


def is_ipv4(value: str) -> bool:
    if not IPV4_RE.match(value):
        return False
    try:
        ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        return False
    return True


def validate_ipv4(name: str, value: str) -> str:
    if not is_ipv4(value):
        die(f"{name} must be an IPv4 address: {value}")
    return value


def dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
