from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from .mac_router.common import CommandResult, die, run_command


@dataclass(frozen=True)
class LanEndpoint:
    interface: str
    ip: str
    hardware_port: str
    kind: str


@dataclass(frozen=True)
class HostNetwork:
    lan: LanEndpoint
    egress_interface: str
    route_target: str


def is_valid_lan_ip(value: str) -> bool:
    if not value:
        return False
    try:
        ip_addr = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        return False
    return not (ip_addr.is_loopback or ip_addr.is_link_local or ip_addr.is_unspecified)


def interface_ipv4(interface: str) -> str:
    result = run_command(["ipconfig", "getifaddr", interface], timeout=10)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    result = run_command(["ifconfig", interface], timeout=10)
    if result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0] == "inet":
            return parts[1]
    return ""


def hardware_ports() -> list[tuple[str, str]]:
    result = run_command(["networksetup", "-listallhardwareports"], timeout=10)
    if result.returncode != 0:
        die(result.stderr.strip() or "networksetup -listallhardwareports failed")
    ports: list[tuple[str, str]] = []
    current_port = ""
    for line in result.stdout.splitlines():
        if line.startswith("Hardware Port: "):
            current_port = line.removeprefix("Hardware Port: ").strip()
        elif line.startswith("Device: "):
            device = line.removeprefix("Device: ").strip()
            if device:
                ports.append((device, current_port))
    return ports


def is_wifi_port(hardware_port: str) -> bool:
    lowered = hardware_port.lower()
    return "wi-fi" in lowered or "wifi" in lowered or "airport" in lowered


def is_ignored_wired_port(interface: str, hardware_port: str) -> bool:
    if interface.startswith(("lo", "bridge", "awdl", "llw", "utun", "vmenet", "gif", "stf", "ap")):
        return True
    lowered = hardware_port.lower()
    return "bridge" in lowered


def select_lan_endpoint() -> LanEndpoint:
    candidates = hardware_ports()
    for kind in ("wired", "wifi"):
        for interface, hardware_port in candidates:
            ip_addr = interface_ipv4(interface)
            if not is_valid_lan_ip(ip_addr):
                continue
            if kind == "wired":
                if is_wifi_port(hardware_port) or is_ignored_wired_port(interface, hardware_port):
                    continue
            elif not is_wifi_port(hardware_port):
                continue
            return LanEndpoint(interface=interface, ip=ip_addr, hardware_port=hardware_port, kind=kind)
    die("no usable LAN IP found on macOS hardware ports")


def route_interface(target: str) -> str:
    result = run_command(["route", "-n", "get", target], timeout=10)
    if result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        if "interface:" in line:
            return line.split("interface:", 1)[1].strip()
    return ""


def wait_for_egress(target: str, *, require_utun: bool, wait_seconds: int, sleep_seconds: int) -> str:
    import time

    deadline = time.monotonic() + wait_seconds
    while True:
        interface = route_interface(target)
        if interface and (not require_utun or interface.startswith("utun")):
            return interface
        if time.monotonic() >= deadline:
            expected = "utun*" if require_utun else "any route"
            die(f"route to {target} is {interface or 'unavailable'}, expected {expected}")
        time.sleep(sleep_seconds)


def check_network(
    *,
    route_target: str,
    require_utun: bool,
    wait_seconds: int,
    sleep_seconds: int,
) -> HostNetwork:
    lan = select_lan_endpoint()
    egress = wait_for_egress(
        route_target,
        require_utun=require_utun,
        wait_seconds=wait_seconds,
        sleep_seconds=sleep_seconds,
    )
    return HostNetwork(lan=lan, egress_interface=egress, route_target=route_target)


def host_check_result(network: HostNetwork) -> CommandResult:
    stdout = (
        f"lan_interface={network.lan.interface}\n"
        f"lan_ip={network.lan.ip}\n"
        f"lan_hardware_port={network.lan.hardware_port}\n"
        f"lan_kind={network.lan.kind}\n"
        f"egress_interface={network.egress_interface}\n"
        f"route_target={network.route_target}\n"
    )
    return CommandResult(0, stdout, "")
