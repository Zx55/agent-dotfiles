"""macOS AirPlay mDNS adapters for MiAir.

The adapter intentionally changes runtime behavior only. It does not modify the
upstream MiAir checkout.
"""

from __future__ import annotations

import logging
import ipaddress
import subprocess
import time
import traceback
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

log = logging.getLogger("miair")


@dataclass(frozen=True)
class RaopRegistration:
    """RAOP registration data used for macOS native dns-sd."""

    service_name: str
    device_name: str
    device_id: str
    rtsp_port: int


def is_ipv4_address(value: str) -> bool:
    """Return whether value is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        return False
    return True


def build_dns_sd_command(registration: RaopRegistration) -> list[str]:
    """Build a macOS dns-sd command for an AirPlay 1 RAOP service."""
    return [
        "/usr/bin/dns-sd",
        "-R",
        registration.service_name,
        "_raop._tcp",
        "local",
        str(registration.rtsp_port),
        "ch=2",
        "cn=0,1,2,3",
        "et=0,1",
        "sv=false",
        "da=true",
        "sr=44100",
        "ss=16",
        "vn=65537",
        "tp=UDP",
        "vs=105.1",
        "am=AirPort4,107",
        "sf=0x4",
        "ft=0x8DC4200",
        "md=0,1,2",
        "pw=false",
        f"fn={registration.device_name}",
    ]


def preferred_ip(hostname: str, fallback: Callable[[], str]) -> str:
    """Prefer configured IPv4 hostname, falling back to MiAir's original logic."""
    if is_ipv4_address(hostname):
        return hostname
    return fallback()


def _terminate_process(proc: subprocess.Popen[Any]) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()


def _native_dns_sd_loop(
    mdns: Any,
    command: Sequence[str],
    popen: Callable[..., subprocess.Popen[Any]] = subprocess.Popen,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Run dns-sd while the MiAir mDNS object is active.

    If dns-sd exits unexpectedly while MiAir is still running, restart it after a
    short delay. This matters because diagnostic commands may accidentally kill
    dns-sd processes.
    """
    while mdns._running:
        proc = popen(
            list(command),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        mdns._miair_native_dns_sd = proc
        while mdns._running and proc.poll() is None:
            sleep(1)
        if mdns._running:
            log.warning("macOS dns-sd RAOP registration exited unexpectedly; restarting")
            sleep(2)


def install_macos_mdns_adapter() -> None:
    """Install runtime monkeypatches for MiAir AirPlay mDNS on macOS."""
    from miair.airplay.mdns import AirPlayMDNS

    if getattr(AirPlayMDNS, "_miair_macos_wrapper_installed", False):
        return

    original_get_ip = AirPlayMDNS._get_ip
    original_stop = AirPlayMDNS.stop

    def get_ip_preferring_configured_hostname(self: Any) -> str:
        return preferred_ip(self.hostname, lambda: original_get_ip(self))

    def run_mdns_with_native_dns_sd(self: Any) -> None:
        try:
            ip = self._get_ip()
            device_id_clean = self.device_id.replace(":", "")
            registration = RaopRegistration(
                service_name=f"{device_id_clean}@{self.device_name}",
                device_name=self.device_name,
                device_id=self.device_id,
                rtsp_port=self.rtsp_port,
            )
            command = build_dns_sd_command(registration)
            log.info("AirPlay mDNS 启动中，IP: %s:%s", ip, self.rtsp_port)
            log.info(
                "macOS dns-sd RAOP 服务已注册: %s._raop._tcp.local.",
                registration.service_name,
            )
            log.info("AirPlay 音频接收器 mDNS 广播已启动")
            log.info("  设备名称: %s", registration.device_name)
            log.info("  设备 ID: %s", registration.device_id)
            log.info("  RTSP 端口: %s", registration.rtsp_port)
            _native_dns_sd_loop(self, command)
        except Exception as exc:
            log.error("启动 macOS dns-sd RAOP 服务失败: %s", exc)
            log.error(traceback.format_exc())

    def stop_with_native_dns_sd(self: Any) -> None:
        proc = getattr(self, "_miair_native_dns_sd", None)
        if proc is not None:
            _terminate_process(proc)
        original_stop(self)

    AirPlayMDNS._get_ip = get_ip_preferring_configured_hostname
    AirPlayMDNS._run_mdns = run_mdns_with_native_dns_sd
    AirPlayMDNS.stop = stop_with_native_dns_sd
    AirPlayMDNS._miair_macos_wrapper_installed = True
