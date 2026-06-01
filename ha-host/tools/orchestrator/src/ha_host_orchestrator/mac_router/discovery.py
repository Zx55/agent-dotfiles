from __future__ import annotations

import ipaddress
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Sequence

from .common import dedupe, die, is_ipv4, normalize_loose_mac, normalize_mac, run_command, validate_ipv4


ARP_RE = re.compile(
    r"\((?P<ip>[0-9.]+)\) at (?P<mac>[0-9a-fA-F]{1,2}(?::[0-9a-fA-F]{1,2}){5})(?: .*?)? on (?P<interface>\S+)"
)


def parse_arp_table() -> list[dict[str, str]]:
    result = run_command(["arp", "-an"], timeout=10)
    if result.returncode != 0:
        die(result.stderr.strip() or "arp -an failed")
    entries: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        match = ARP_RE.search(line)
        if not match:
            continue
        entries.append(
            {
                "ip": match.group("ip"),
                "mac": normalize_loose_mac(match.group("mac")),
                "interface": match.group("interface"),
            }
        )
    return entries


def find_ip_by_mac(mac: str, interface: str | None = None) -> str:
    ips = find_ips_by_mac(mac, interface=interface)
    return ips[0] if ips else ""


def find_ips_by_mac(mac: str, interface: str | None = None) -> list[str]:
    mac = normalize_mac(mac)
    ips: list[str] = []
    for entry in parse_arp_table():
        if entry["mac"] != mac:
            continue
        if interface and entry["interface"] != interface:
            continue
        ips.append(entry["ip"])
    return ips


def ping_ip(ip_addr: str, timeout_ms: int) -> None:
    run_command(["ping", "-c", "1", "-W", str(timeout_ms), ip_addr], timeout=3)


def sweep_subnet(subnet: str, timeout_ms: int, workers: int) -> None:
    network = ipaddress.ip_network(subnet, strict=False)
    hosts = [str(host) for host in network.hosts()]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(ping_ip, host, timeout_ms) for host in hosts]
        for future in as_completed(futures):
            future.result()


def infer_subnet(interface: str) -> str:
    result = run_command(["ipconfig", "getifaddr", interface], timeout=10)
    if result.returncode != 0 or not result.stdout.strip():
        die(f"could not infer subnet because {interface} has no IPv4 address")
    ip_addr = ipaddress.IPv4Address(result.stdout.strip())
    return str(ipaddress.IPv4Network(f"{ip_addr}/24", strict=False))


def resolve_device_ip(
    device: dict[str, Any],
    *,
    interface: str,
    scan: bool,
    subnet: str,
    timeout_ms: int,
    workers: int,
) -> str:
    host = str(device.get("host", "")).strip()
    last_ip = str(device.get("last_ip", "")).strip()
    if host:
        run_command(["ping", "-c", "1", "-W", str(timeout_ms), host], timeout=3)

    ip_addrs = find_ips_by_mac(device["mac"], interface=interface)
    if last_ip and last_ip in ip_addrs:
        return last_ip
    if ip_addrs:
        return ip_addrs[0]

    if scan:
        sweep_subnet(subnet, timeout_ms=timeout_ms, workers=workers)
        ip_addrs = find_ips_by_mac(device["mac"], interface=interface)
        if last_ip and last_ip in ip_addrs:
            return last_ip
        if ip_addrs:
            return ip_addrs[0]

    return last_ip


def resolve_targets(
    registry: dict[str, Any],
    names_or_ips: Sequence[str],
    *,
    interface: str,
    scan: bool,
    subnet: str,
    timeout_ms: int,
    workers: int,
) -> list[str]:
    devices = registry["devices"]
    targets: list[str] = []
    for value in names_or_ips:
        if is_ipv4(value):
            targets.append(value)
            continue
        if value not in devices:
            die(f"unknown device: {value}")
        ip_addr = resolve_device_ip(
            devices[value],
            interface=interface,
            scan=scan,
            subnet=subnet,
            timeout_ms=timeout_ms,
            workers=workers,
        )
        if not ip_addr:
            die(f"could not resolve IP for {value}; rerun with --scan or set --ip when registering")
        validate_ipv4(value, ip_addr)
        devices[value]["last_ip"] = ip_addr
        targets.append(ip_addr)
    return dedupe(targets)
