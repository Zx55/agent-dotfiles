from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .mac_router.discovery import infer_subnet, resolve_targets
from .mac_router.registry import load_registry, save_registry
from .mac_router.router import router_args, run_router
from .network import HostNetwork, check_network, host_check_result
from .state import HostState, default_state_path, host_state_from_network, read_state, state_matches_network, write_state


@dataclass(frozen=True)
class HostOptions:
    registry: Path
    route_target: str
    require_utun: bool
    wait_seconds: int
    sleep_seconds: int
    scan: bool
    subnet: str | None
    timeout_ms: int
    workers: int
    state_path: Path | None = None


def selected_network(options: HostOptions) -> HostNetwork:
    return check_network(
        route_target=options.route_target,
        require_utun=options.require_utun,
        wait_seconds=options.wait_seconds,
        sleep_seconds=options.sleep_seconds,
    )


def resolve_all_targets(options: HostOptions, network: HostNetwork) -> tuple[dict, list[str]]:
    registry = load_registry(options.registry)
    selected = sorted(registry["devices"])
    if not selected:
        return registry, []
    subnet = options.subnet or infer_subnet(network.lan.interface)
    targets = resolve_targets(
        registry,
        selected,
        interface=network.lan.interface,
        scan=options.scan,
        subnet=subnet,
        timeout_ms=options.timeout_ms,
        workers=options.workers,
    )
    save_registry(options.registry, registry)
    return registry, targets


def apply_router_for_targets(options: HostOptions, network: HostNetwork, registry: dict, targets: list[str]) -> int:
    if not targets:
        print("no registered devices; router apply skipped")
        return 0
    defaults = registry["defaults"]
    dns = defaults.get("dns", "1.1.1.1")
    command_args = router_args(
        "apply",
        targets,
        lan_interface=network.lan.interface,
        mac_lan_ip=network.lan.ip,
        dns=dns,
        egress_interface=network.egress_interface,
        replace_targets=True,
        yes=True,
    )
    return run_router(command_args, sudo=True)


def print_network(prefix: str, network: HostNetwork) -> None:
    print(f"{prefix}lan_interface={network.lan.interface}")
    print(f"{prefix}lan_ip={network.lan.ip}")
    print(f"{prefix}lan_hardware_port={network.lan.hardware_port}")
    print(f"{prefix}lan_kind={network.lan.kind}")
    print(f"{prefix}egress_interface={network.egress_interface}")
    print(f"{prefix}route_target={network.route_target}")


def check(options: HostOptions) -> int:
    network = selected_network(options)
    result = host_check_result(network)
    print(result.stdout.rstrip())
    return result.returncode


def startup(options: HostOptions) -> int:
    network = selected_network(options)
    print_network("", network)
    registry, targets = resolve_all_targets(options, network)
    rc = apply_router_for_targets(options, network, registry, targets)
    if rc != 0:
        return rc
    state = host_state_from_network(network, registry_path=options.registry, target_ips=targets)
    state_path = write_state(state, options.state_path or default_state_path())
    print(f"state_path={state_path}")
    return 0


def watch(options: HostOptions) -> int:
    network = selected_network(options)
    current = read_state(options.state_path or default_state_path())
    if current and state_matches_network(current, network):
        print(f"no_change=1")
        print_network("", network)
        return 0
    if current:
        print("change_detected=1")
        print(f"previous_lan_interface={current.lan_interface}")
        print(f"previous_lan_ip={current.lan_ip}")
        print(f"previous_egress_interface={current.egress_interface}")
    else:
        print("state_missing=1")
    return startup(options)
