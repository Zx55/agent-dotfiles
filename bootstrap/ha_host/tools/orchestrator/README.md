# HA Host Orchestrator

This tool owns the macOS host side for HAOS routing and startup. It is split into four launchd-facing Python entrypoints, four shell entry scripts, and four plist templates:

```text
root: com.user.ha-host-startup -> ha_host_orchestrator.entrypoints.host_startup
root: com.user.ha-host-watch   -> ha_host_orchestrator.entrypoints.host_watch
user: com.user.haos-start      -> ha_host_orchestrator.entrypoints.haos_start
user: com.user.haos-watch      -> ha_host_orchestrator.entrypoints.haos_watch
```

The root host side selects the current LAN IP dynamically on every run. It enumerates macOS hardware ports, prefers wired Ethernet-class ports with valid IPv4 addresses, and falls back to Wi-Fi. It also verifies the configured egress route target because this Mac acts as the router for selected LAN clients.

Runtime state is local to the Mac:

```text
~/.ha_host/state.json
~/.ha_host/host-startup.log
~/.ha_host/host-startup.err
~/.ha_host/host-watch.log
~/.ha_host/host-watch.err
~/.ha_host/haos-start.log
~/.ha_host/haos-start.err
~/.ha_host/haos-watch.log
~/.ha_host/haos-watch.err
~/.ha_host/haos-watch-state.json
~/.router/device.json
```

`~/.router/device.json` remains the local device registry for clients routed through the Mac.

## Entry Points

Run source entrypoints with `PYTHONPATH` while developing:

```sh
cd ~/Documents/codex-workspace/agent-dotfiles
PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.host_startup --check-only --no-require-utun

PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.host_watch --check-only --no-require-utun

PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.haos_start --help

PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.haos_watch --help
```

The normal root startup entrypoint waits for a usable LAN IP, verifies the egress route, resolves all registered devices, applies `pf` router rules, and writes `~/.ha_host/state.json`.

The root watch entrypoint runs the same selection logic but only reapplies routing when the selected LAN interface, LAN IP, egress interface, or route target has changed from the stored state. This handles both directions, such as wired disappearing and falling back to Wi-Fi, or wired becoming available again and taking priority.

The user HAOS startup entrypoint waits for host state and starts the UTM VM.

The user HAOS watch entrypoint reads host state, reconciles the UTM bridged interface to the selected Mac LAN interface, then uses `utmctl exec` through the guest agent to reconcile HAOS routing when repair is needed. It does not require `ssh haos` to be reachable before repair, because a stale gateway is exactly one of the failure modes it handles. After a successful check or repair, it writes `~/.ha_host/haos-watch-state.json`. Later watch runs skip both UTM config access and `utmctl exec` when the host LAN IP, prior UTM bridge, HAOS interface, and guest device are unchanged, and use SSH only as a lightweight health check. If the cached health check fails, the watch falls back to UTM config and guest-agent repair. This cached steady state intentionally trusts the last verified UTM bridge. If UTM is edited manually while SSH remains healthy, run `scripts/doctor.sh`, remove `~/.ha_host/haos-watch-state.json`, or kickstart `com.user.haos-watch` after clearing the cache so the watch reads UTM config again.

By default, the installer sets `FORCE_BRIDGE_RESTART=1`. If the VM must change from one bridged Mac interface to another, `haos-watch` first asks UTM to stop the VM gracefully. If that graceful stop times out, it force-stops the VM, edits the UTM bridge config, and starts the VM again. Pass `--no-force-bridge-restart` if bridge drift should fail instead of forcing the VM off. Pass `--no-utm-bridge-apply` or `--no-haos-gateway-apply` if the watch should report drift without changing UTM or HAOS.

macOS may prompt that `python3.12` wants to access another app's data when the watch reads or edits UTM's sandboxed VM config. Steady-state cached runs avoid UTM data access, but unattended bridge recovery still needs that permission ahead of time. Run `scripts/doctor.sh` interactively after install and allow the prompt, or grant the Python binary shown in the launchd plist Full Disk Access before relying on automatic recovery.

`install-launchd.sh` preflights read/write access to the UTM VM package with the same service Python before it installs and loads launchd jobs. If macOS prompts, allow it during install so later bridge recovery can run unattended. Use `--skip-utm-permission-preflight` only when the VM does not exist yet or permission will be granted another way.

The HA host bootstrap creates a dedicated service Python:

```text
/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python
```

That Python is created from the shared agent Python with `venv --copies --without-pip` during `bootstrap/bootstrap.sh --profile ha_host install`, owned by `root:wheel`, and readable/executable by launchd user jobs. The four orchestrator launchd jobs use it by default. Grant App Data or Full Disk Access to this service Python, not to the shared uv Python. Pass `--python PATH` only when intentionally overriding this isolation for diagnostics.

## Launchd

Render and validate the four plist templates without installing:

```sh
bootstrap/ha_host/tools/orchestrator/scripts/install-launchd.sh --dry-run
```

Check runtime health and UTM config access:

```sh
bootstrap/ha_host/tools/orchestrator/scripts/doctor.sh
```

Install and load the four jobs:

```sh
bootstrap/ha_host/tools/orchestrator/scripts/install-launchd.sh \
  --vm-name HAOS-17.3 \
  --load-now
```

The installer copies the runtime to:

```text
/usr/local/libexec/agent-dotfiles/orchestrator/
```

The installer writes the HA host service Python binary into the plists. Run `bootstrap/bootstrap.sh --profile ha_host install` before installing launchd jobs so `/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python` exists.

Uninstall the launchd jobs and runtime copy:

```sh
bootstrap/ha_host/tools/orchestrator/scripts/uninstall-launchd.sh
```

## Target Device Settings

Devices routed through the Mac should use the currently selected Mac LAN IP from `~/.ha_host/state.json` as their gateway, public DNS such as `1.1.1.1`, and IPv6 disabled if they must not bypass the Mac route.

The Mac side is IPv4-only and uses `pf` rules scoped to registered target IPs.
