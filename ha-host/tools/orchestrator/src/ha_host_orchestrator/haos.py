from __future__ import annotations

import json
import plistlib
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mac_router.common import CommandResult, run_command
from .state import HostState, default_state_path, read_state


@dataclass(frozen=True)
class HaosNetworkStatus:
    reachable: bool
    stdout: str
    stderr: str


@dataclass(frozen=True)
class HaosWatchState:
    version: int
    updated_at: float
    vm_name: str
    host_lan_interface: str
    host_lan_ip: str
    bridge_interface: str
    haos_interface: str
    guest_device: str
    gateway: str


@dataclass(frozen=True)
class HaosRecoveryState:
    version: int
    updated_at: float
    consecutive_failures: int
    last_failure_reason: str
    last_restart_at: float


def haos_watch_state_path(host_state_path: Path | None = None) -> Path:
    base = host_state_path or default_state_path()
    return base.parent / "haos-watch-state.json"


def haos_recovery_state_path(host_state_path: Path | None = None) -> Path:
    base = host_state_path or default_state_path()
    return base.parent / "haos-watch-recovery.json"


def log_timestamp(name: str) -> None:
    print(f"{name}={time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime())}")


def read_haos_watch_state(path: Path) -> HaosWatchState | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            data: dict[str, Any] = json.load(handle)
        return HaosWatchState(
            version=int(data["version"]),
            updated_at=float(data["updated_at"]),
            vm_name=str(data["vm_name"]),
            host_lan_interface=str(data["host_lan_interface"]),
            host_lan_ip=str(data["host_lan_ip"]),
            bridge_interface=str(data["bridge_interface"]),
            haos_interface=str(data["haos_interface"]),
            guest_device=str(data["guest_device"]),
            gateway=str(data["gateway"]),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def read_haos_recovery_state(path: Path) -> HaosRecoveryState | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            data: dict[str, Any] = json.load(handle)
        return HaosRecoveryState(
            version=int(data["version"]),
            updated_at=float(data["updated_at"]),
            consecutive_failures=int(data["consecutive_failures"]),
            last_failure_reason=str(data["last_failure_reason"]),
            last_restart_at=float(data.get("last_restart_at", 0)),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def write_haos_recovery_state(path: Path, state: HaosRecoveryState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(state.__dict__, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(path)


def clear_haos_recovery_state(path: Path) -> None:
    current = read_haos_recovery_state(path)
    if current is None or current.consecutive_failures == 0:
        print("recovery_failures_cleared=0")
        return
    write_haos_recovery_state(
        path,
        HaosRecoveryState(
            version=1,
            updated_at=time.time(),
            consecutive_failures=0,
            last_failure_reason="",
            last_restart_at=current.last_restart_at,
        ),
    )
    print("recovery_failures_cleared=1")


def write_haos_watch_state(
    path: Path,
    *,
    vm_name: str,
    host_state: HostState,
    bridge: str,
    haos_interface: str,
    guest_device: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = HaosWatchState(
        version=1,
        updated_at=time.time(),
        vm_name=vm_name,
        host_lan_interface=host_state.lan_interface,
        host_lan_ip=host_state.lan_ip,
        bridge_interface=bridge,
        haos_interface=haos_interface,
        guest_device=guest_device,
        gateway=host_state.lan_ip,
    )
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(data.__dict__, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(path)


def watch_state_matches(
    cached: HaosWatchState | None,
    *,
    vm_name: str,
    host_state: HostState,
    bridge: str,
    haos_interface: str,
    guest_device: str,
) -> bool:
    return (
        cached is not None
        and cached.vm_name == vm_name
        and cached.host_lan_interface == host_state.lan_interface
        and cached.host_lan_ip == host_state.lan_ip
        and cached.bridge_interface == bridge
        and cached.haos_interface == haos_interface
        and cached.guest_device == guest_device
        and cached.gateway == host_state.lan_ip
    )


def watch_state_matches_host(
    cached: HaosWatchState | None,
    *,
    vm_name: str,
    host_state: HostState,
    haos_interface: str,
    guest_device: str,
) -> bool:
    return (
        cached is not None
        and cached.vm_name == vm_name
        and cached.host_lan_interface == host_state.lan_interface
        and cached.host_lan_ip == host_state.lan_ip
        and cached.bridge_interface == host_state.lan_interface
        and cached.haos_interface == haos_interface
        and cached.guest_device == guest_device
        and cached.gateway == host_state.lan_ip
    )


def print_cache_summary(cached: HaosWatchState | None) -> None:
    print(f"cache_present={1 if cached else 0}")
    if cached is None:
        return
    print(f"cache_updated_at={time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(cached.updated_at))}")
    print(f"cache_age_seconds={max(0, int(time.time() - cached.updated_at))}")
    print(f"cache_vm_name={cached.vm_name}")
    print(f"cache_host_lan_interface={cached.host_lan_interface}")
    print(f"cache_host_lan_ip={cached.host_lan_ip}")
    print(f"cache_bridge_interface={cached.bridge_interface}")
    print(f"cache_gateway={cached.gateway}")
    print(f"cache_haos_interface={cached.haos_interface}")
    print(f"cache_guest_device={cached.guest_device}")


def print_recovery_summary(path: Path, recovery: HaosRecoveryState | None) -> None:
    print(f"haos_recovery_state_path={path}")
    print(f"recovery_present={1 if recovery else 0}")
    if recovery is None:
        print("recovery_consecutive_failures=0")
        return
    print(f"recovery_updated_at={time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(recovery.updated_at))}")
    print(f"recovery_consecutive_failures={recovery.consecutive_failures}")
    print(f"recovery_last_failure_reason={recovery.last_failure_reason}")
    if recovery.last_restart_at > 0:
        print(f"recovery_last_restart_at={time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(recovery.last_restart_at))}")


def utmctl_path() -> str:
    found = shutil.which("utmctl")
    if found:
        return found
    return "/Applications/UTM.app/Contents/MacOS/utmctl"


def list_vms() -> int:
    result = run_command([utmctl_path(), "list"], timeout=20)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    return result.returncode


def vm_is_started(name: str) -> bool:
    result = run_command([utmctl_path(), "list"], timeout=20)
    if result.returncode != 0:
        return False
    pattern = re.compile(r"^\S+\s+started\s+" + re.escape(name) + r"\s*$")
    return any(pattern.match(line) for line in result.stdout.splitlines())


def start_vm(name: str) -> int:
    if vm_is_started(name):
        print(f"{name} already started")
        return 0
    result = run_command([utmctl_path(), "start", name], timeout=30)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    combined = "\n".join([result.stdout, result.stderr])
    if "QEMU error:" in combined or "unsupported ifname" in combined or "虚拟机未运行" in combined:
        return 75
    return result.returncode


def quit_utm_app() -> int:
    result = run_command(["osascript", "-e", 'tell application "UTM" to quit'], timeout=20)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    return result.returncode


def start_vm_after_config_change(name: str, *, allow_utm_app_restart: bool) -> int:
    rc = start_vm(name)
    if rc == 0:
        return 0
    if not allow_utm_app_restart:
        print("utm_restart_app=disabled")
        return rc
    print("utm_restart_app=1")
    quit_utm_app()
    import time

    time.sleep(5)
    return start_vm(name)


def restart_vm_for_recovery(
    name: str,
    *,
    force_restart: bool,
    allow_utm_app_restart: bool,
    wait_seconds: int,
    sleep_seconds: int,
) -> int:
    print(f"recovery_utm_stop_request={name}")
    rc = stop_vm_request(name)
    if rc != 0:
        return rc
    if not wait_for_vm_status(name, "stopped", wait_seconds=wait_seconds, sleep_seconds=sleep_seconds):
        print(f"recovery_utm_stop_request_timeout={name}")
        if not force_restart:
            return 75
        print(f"recovery_utm_stop_force={name}")
        rc = stop_vm_force(name)
        if rc != 0:
            return rc
        if not wait_for_vm_status(name, "stopped", wait_seconds=wait_seconds, sleep_seconds=sleep_seconds):
            print(f"recovery_utm_stop_force_timeout={name}")
            return 75
    print(f"recovery_utm_start={name}")
    return start_vm_after_config_change(name, allow_utm_app_restart=allow_utm_app_restart)


def stop_vm_request(name: str) -> int:
    if not vm_is_started(name):
        print(f"{name} already stopped")
        return 0
    result = run_command([utmctl_path(), "stop", "--request", name], timeout=60)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    return result.returncode


def stop_vm_force(name: str) -> int:
    if not vm_is_started(name):
        print(f"{name} already stopped")
        return 0
    result = run_command([utmctl_path(), "stop", "--force", name], timeout=60)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    return result.returncode


def vm_status(name: str) -> str:
    result = run_command([utmctl_path(), "status", name], timeout=20)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def wait_for_vm_status(name: str, expected: str, *, wait_seconds: int, sleep_seconds: int) -> bool:
    import time

    deadline = time.monotonic() + wait_seconds
    while True:
        if vm_status(name) == expected:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(sleep_seconds)


def default_utm_config_path(vm_name: str) -> Path:
    return Path.home() / "Library" / "Containers" / "com.utmapp.UTM" / "Data" / "Documents" / f"{vm_name}.utm" / "config.plist"


def read_utm_config(path: Path) -> dict:
    with path.open("rb") as handle:
        return plistlib.load(handle)


def write_utm_config(path: Path, data: dict) -> None:
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("wb") as handle:
        plistlib.dump(data, handle)
    tmp_path.replace(path)


def bridge_interface(path: Path) -> str:
    data = read_utm_config(path)
    networks = data.get("Network", [])
    if not networks:
        return ""
    return str(networks[0].get("BridgeInterface", ""))


def set_bridge_interface(path: Path, interface: str) -> None:
    data = read_utm_config(path)
    networks = data.setdefault("Network", [])
    if not networks:
        raise SystemExit(f"UTM config has no Network entry: {path}")
    networks[0]["Mode"] = "Bridged"
    networks[0]["BridgeInterface"] = interface
    write_utm_config(path, data)


def reconcile_bridge(
    *,
    vm_name: str,
    config_path: Path,
    interface: str,
    apply_bridge: bool,
    force_bridge_restart: bool,
    wait_seconds: int,
    sleep_seconds: int,
) -> int:
    current = bridge_interface(config_path)
    print(f"utm_bridge_interface={current or 'unknown'}")
    print(f"host_lan_interface={interface}")
    if current == interface:
        print("utm_bridge_matches=1")
        return 0
    print("utm_bridge_matches=0")
    print(f"utm_bridge_update_required={current or 'unknown'}->{interface}")
    if not apply_bridge:
        print("utm_bridge_apply=disabled")
        return 0
    was_started = vm_is_started(vm_name)
    if was_started:
        print(f"utm_stop_request={vm_name}")
        rc = stop_vm_request(vm_name)
        if rc != 0:
            return rc
        if not wait_for_vm_status(vm_name, "stopped", wait_seconds=wait_seconds, sleep_seconds=sleep_seconds):
            print(f"utm_stop_request_timeout={vm_name}")
            if not force_bridge_restart:
                return 75
            print(f"utm_stop_force={vm_name}")
            rc = stop_vm_force(vm_name)
            if rc != 0:
                return rc
            if not wait_for_vm_status(vm_name, "stopped", wait_seconds=wait_seconds, sleep_seconds=sleep_seconds):
                print(f"utm_stop_force_timeout={vm_name}")
                return 75
    set_bridge_interface(config_path, interface)
    print(f"utm_bridge_applied={interface}")
    if was_started:
        print(f"utm_start={vm_name}")
        return start_vm_after_config_change(vm_name, allow_utm_app_restart=False)
    return 0


def wait_for_state(path: Path | None, *, wait_seconds: int, sleep_seconds: int) -> HostState:
    import time

    state_path = path or default_state_path()
    deadline = time.monotonic() + wait_seconds
    while True:
        state = read_state(state_path)
        if state is not None:
            return state
        if time.monotonic() >= deadline:
            raise SystemExit(f"host state is unavailable: {state_path}")
        time.sleep(sleep_seconds)


def startup(vm_name: str, *, state_path: Path | None, wait_seconds: int, sleep_seconds: int) -> int:
    state = wait_for_state(state_path, wait_seconds=wait_seconds, sleep_seconds=sleep_seconds)
    print(f"host_lan_ip={state.lan_ip}")
    print(f"host_lan_interface={state.lan_interface}")
    return start_vm(vm_name)


def ha_network_info(host_alias: str) -> HaosNetworkStatus:
    result = run_command(["ssh", host_alias, "ha network info"], timeout=20)
    if result.returncode != 0:
        return HaosNetworkStatus(False, result.stdout, result.stderr)
    return HaosNetworkStatus(True, result.stdout, result.stderr)


UTMCTL_ERROR_MARKERS = (
    "Error from event:",
    "OSStatus",
    "QEMU 客户机代理没有运行",
    "guest agent is not running",
)


def output_has_utmctl_error(result: CommandResult) -> bool:
    combined = "\n".join([result.stdout, result.stderr])
    return any(marker in combined for marker in UTMCTL_ERROR_MARKERS)


def utm_exec(vm_name: str, command: list[str], *, timeout: int = 30) -> CommandResult:
    result = run_command([utmctl_path(), "exec", vm_name, "--cmd", *command], timeout=timeout)
    if result.returncode == 0 and output_has_utmctl_error(result):
        return CommandResult(75, result.stdout, result.stderr)
    return result


def guest_ip_route(vm_name: str) -> CommandResult:
    return utm_exec(vm_name, ["ip", "route"], timeout=20)


def default_gateways(output: str) -> list[str]:
    gateways: list[str] = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "default" and parts[1] == "via":
            gateways.append(parts[2])
    return gateways


def route_matches_gateway(output: str, gateway: str) -> bool:
    gateways = default_gateways(output)
    return bool(gateways) and all(item == gateway for item in gateways)


def ssh_reports_gateway(status: HaosNetworkStatus, gateway: str) -> bool:
    return status.reachable and gateway in status.stdout


def update_gateway_via_utm(vm_name: str, *, haos_interface: str, guest_device: str, gateway: str) -> int:
    before = guest_ip_route(vm_name)
    print(f"haos_network_apply=utmctl exec {vm_name} -- ha network update {haos_interface} --ipv4-gateway {gateway}")
    result = utm_exec(vm_name, ["ha", "network", "update", haos_interface, "--ipv4-gateway", gateway], timeout=30)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    if result.returncode != 0:
        return result.returncode
    connection_file = f"/etc/NetworkManager/system-connections/Supervisor {guest_device}.nmconnection"
    script = (
        f"file={connection_file!r}; "
        "if [ -f \"$file\" ]; then "
        f"sed -i -E 's#^address1=([^,]+),.*#address1=\\1,{gateway}#' \"$file\"; "
        "nmcli connection reload >/dev/null 2>&1 || true; "
        "fi"
    )
    persist_result = utm_exec(vm_name, ["/bin/sh", "-c", script], timeout=20)
    if persist_result.stdout:
        print(persist_result.stdout.rstrip())
    if persist_result.stderr:
        print(persist_result.stderr.rstrip())
    if persist_result.returncode != 0:
        return persist_result.returncode
    route_result = utm_exec(vm_name, ["ip", "route", "replace", "default", "via", gateway, "dev", guest_device], timeout=20)
    if route_result.stdout:
        print(route_result.stdout.rstrip())
    if route_result.stderr:
        print(route_result.stderr.rstrip())
    if route_result.returncode != 0:
        return route_result.returncode
    for old_gateway in default_gateways(before.stdout):
        if old_gateway == gateway:
            continue
        delete_result = utm_exec(vm_name, ["ip", "route", "del", "default", "via", old_gateway, "dev", guest_device], timeout=20)
        if delete_result.stdout:
            print(delete_result.stdout.rstrip())
        if delete_result.stderr:
            print(delete_result.stderr.rstrip())
    return 0


def record_recovery_failure(
    *,
    recovery_path: Path,
    vm_name: str,
    reason: str,
    apply_vm_restart: bool,
    allow_utm_app_restart: bool,
    restart_after_failures: int,
    restart_cooldown_seconds: int,
    force_restart: bool,
    wait_seconds: int,
    sleep_seconds: int,
) -> int:
    current = read_haos_recovery_state(recovery_path)
    now = time.time()
    previous_failures = current.consecutive_failures if current else 0
    last_restart_at = current.last_restart_at if current else 0
    consecutive_failures = previous_failures + 1
    print(f"recovery_failure_reason={reason}")
    print(f"recovery_previous_consecutive_failures={previous_failures}")
    print(f"recovery_consecutive_failures={consecutive_failures}")
    print(f"recovery_restart_after_failures={restart_after_failures}")
    print(f"recovery_restart_cooldown_seconds={restart_cooldown_seconds}")
    restart_due = restart_after_failures > 0 and consecutive_failures >= restart_after_failures
    cooldown_remaining = int(max(0, restart_cooldown_seconds - (now - last_restart_at))) if last_restart_at else 0
    write_haos_recovery_state(
        recovery_path,
        HaosRecoveryState(
            version=1,
            updated_at=now,
            consecutive_failures=consecutive_failures,
            last_failure_reason=reason,
            last_restart_at=last_restart_at,
        ),
    )
    if not restart_due:
        print("recovery_restart_due=0")
        return 0
    print("recovery_restart_due=1")
    if cooldown_remaining > 0:
        print(f"recovery_restart_skipped_cooldown_remaining={cooldown_remaining}")
        return 0
    if not apply_vm_restart:
        print("recovery_restart_apply=disabled")
        return 0
    print("recovery_restart_apply=1")
    rc = restart_vm_for_recovery(
        vm_name,
        force_restart=force_restart,
        allow_utm_app_restart=allow_utm_app_restart,
        wait_seconds=wait_seconds,
        sleep_seconds=sleep_seconds,
    )
    if rc != 0:
        return rc
    write_haos_recovery_state(
        recovery_path,
        HaosRecoveryState(
            version=1,
            updated_at=time.time(),
            consecutive_failures=0,
            last_failure_reason="",
            last_restart_at=time.time(),
        ),
    )
    print("recovery_restart_completed=1")
    return 0


def watch(
    *,
    vm_name: str,
    host_alias: str,
    haos_interface: str,
    guest_device: str,
    apply_gateway: bool,
    apply_bridge: bool,
    force_bridge_restart: bool,
    apply_vm_restart: bool,
    allow_utm_app_restart: bool,
    restart_after_failures: int,
    restart_cooldown_seconds: int,
    utm_config_path: Path | None,
    state_path: Path | None,
    wait_seconds: int,
    sleep_seconds: int,
) -> int:
    log_timestamp("haos_watch_started_at")
    state = wait_for_state(state_path, wait_seconds=wait_seconds, sleep_seconds=sleep_seconds)
    resolved_state_path = state_path or default_state_path()
    print(f"host_state_path={resolved_state_path}")
    print(f"host_lan_ip={state.lan_ip}")
    print(f"host_lan_interface={state.lan_interface}")
    print(f"host_lan_kind={state.lan_kind}")
    print(f"host_egress_interface={state.egress_interface}")
    cache_path = haos_watch_state_path(state_path)
    print(f"haos_watch_state_path={cache_path}")
    cached = read_haos_watch_state(cache_path)
    print_cache_summary(cached)
    recovery_path = haos_recovery_state_path(state_path)
    print_recovery_summary(recovery_path, read_haos_recovery_state(recovery_path))
    cache_matches_host = watch_state_matches_host(
        cached,
        vm_name=vm_name,
        host_state=state,
        haos_interface=haos_interface,
        guest_device=guest_device,
    )
    print(f"cache_matches_host={1 if cache_matches_host else 0}")
    if cache_matches_host:
        print("utm_bridge_check=skipped_cached")
        status = ha_network_info(host_alias)
        print(f"haos_ssh_reachable={1 if status.reachable else 0}")
        if status.stderr:
            print(status.stderr.rstrip())
        if ssh_reports_gateway(status, state.lan_ip):
            print("haos_guest_agent_check=skipped_ssh_verified")
            print("gateway_matches=ssh_verified")
            clear_haos_recovery_state(recovery_path)
            return 0
        print("cache_health_check_failed=1")

    config_path = utm_config_path or default_utm_config_path(vm_name)
    current_bridge = ""
    if config_path.exists():
        try:
            current_bridge = bridge_interface(config_path)
            print(f"utm_bridge_interface={current_bridge or 'unknown'}")
            print(f"host_lan_interface={state.lan_interface}")
            if current_bridge == state.lan_interface:
                print("utm_bridge_matches=1")
            else:
                rc = reconcile_bridge(
                    vm_name=vm_name,
                    config_path=config_path,
                    interface=state.lan_interface,
                    apply_bridge=apply_bridge,
                    force_bridge_restart=force_bridge_restart,
                    wait_seconds=wait_seconds,
                    sleep_seconds=sleep_seconds,
                )
                if rc != 0:
                    return rc
                current_bridge = state.lan_interface
        except OSError as exc:
            print(f"utm_config_read_failed={config_path}")
            print(f"utm_config_read_error={exc}")
    else:
        print(f"utm_config_missing={config_path}")
    cache_matches_bridge = bool(current_bridge) and watch_state_matches(
        cached,
        vm_name=vm_name,
        host_state=state,
        bridge=current_bridge,
        haos_interface=haos_interface,
        guest_device=guest_device,
    )
    print(f"cache_matches_bridge={1 if cache_matches_bridge else 0}")
    if cache_matches_bridge:
        status = ha_network_info(host_alias)
        print(f"haos_ssh_reachable={1 if status.reachable else 0}")
        if status.stderr:
            print(status.stderr.rstrip())
        if ssh_reports_gateway(status, state.lan_ip):
            print("haos_guest_agent_check=skipped_ssh_verified")
            print("gateway_matches=ssh_verified")
            clear_haos_recovery_state(recovery_path)
            return 0
        print("cache_health_check_failed=1")

    status = ha_network_info(host_alias)
    print(f"haos_ssh_reachable={1 if status.reachable else 0}")
    if status.stderr:
        print(status.stderr.rstrip())
    if current_bridge and ssh_reports_gateway(status, state.lan_ip):
        print("haos_guest_agent_check=skipped_ssh_verified")
        print("gateway_matches=ssh_verified")
        write_haos_watch_state(
            cache_path,
            vm_name=vm_name,
            host_state=state,
            bridge=current_bridge,
            haos_interface=haos_interface,
            guest_device=guest_device,
        )
        clear_haos_recovery_state(recovery_path)
        return 0

    route = guest_ip_route(vm_name)
    if route.returncode != 0:
        print("haos_guest_agent_reachable=0")
        if route.stderr:
            print(route.stderr.rstrip())
        return record_recovery_failure(
            recovery_path=recovery_path,
            vm_name=vm_name,
            reason="guest_agent_unreachable",
            apply_vm_restart=apply_vm_restart,
            allow_utm_app_restart=allow_utm_app_restart,
            restart_after_failures=restart_after_failures,
            restart_cooldown_seconds=restart_cooldown_seconds,
            force_restart=force_bridge_restart,
            wait_seconds=wait_seconds,
            sleep_seconds=sleep_seconds,
        )
    print("haos_guest_agent_reachable=1")
    if route.stdout:
        print(route.stdout.rstrip())
    gateway_matches = route_matches_gateway(route.stdout, state.lan_ip)
    print(f"gateway_matches={1 if gateway_matches else 0}")
    if not gateway_matches:
        print("haos_network_update_required=1")
        if not apply_gateway:
            print("haos_network_apply=disabled")
            return 0
        rc = update_gateway_via_utm(vm_name, haos_interface=haos_interface, guest_device=guest_device, gateway=state.lan_ip)
        if rc != 0:
            return record_recovery_failure(
                recovery_path=recovery_path,
                vm_name=vm_name,
                reason="gateway_update_failed",
                apply_vm_restart=apply_vm_restart,
                allow_utm_app_restart=allow_utm_app_restart,
                restart_after_failures=restart_after_failures,
                restart_cooldown_seconds=restart_cooldown_seconds,
                force_restart=force_bridge_restart,
                wait_seconds=wait_seconds,
                sleep_seconds=sleep_seconds,
            )
    if current_bridge:
        write_haos_watch_state(
            cache_path,
            vm_name=vm_name,
            host_state=state,
            bridge=current_bridge,
            haos_interface=haos_interface,
            guest_device=guest_device,
        )
    if gateway_matches:
        return record_recovery_failure(
            recovery_path=recovery_path,
            vm_name=vm_name,
            reason="ssh_unreachable_gateway_ok",
            apply_vm_restart=apply_vm_restart,
            allow_utm_app_restart=allow_utm_app_restart,
            restart_after_failures=restart_after_failures,
            restart_cooldown_seconds=restart_cooldown_seconds,
            force_restart=force_bridge_restart,
            wait_seconds=wait_seconds,
            sleep_seconds=sleep_seconds,
        )
    return 0


def state_json(path: Path | None = None) -> str:
    state = read_state(path or default_state_path())
    if state is None:
        return "{}"
    return json.dumps(state.__dict__, indent=2, sort_keys=True)
