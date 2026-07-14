# Launchd Jobs For The HA Host Orchestrator

Use this to verify the already installed HA host orchestrator. Do not install or manage legacy router services from this skill.

## Jobs

Root LaunchDaemons:

```text
com.user.ha-host-startup
com.user.ha-host-watch
```

`ha-host-startup` runs after boot, selects the current LAN IP dynamically, verifies the configured egress route, then applies router rules for all devices in `~/.router/device.json`.

`ha-host-watch` runs every five minutes by default. It repeats the same LAN and egress selection, compares it with `~/.ha_host/state.json`, and only reapplies routing when the selected LAN interface, LAN IP, egress interface, or route target changed. Wired Ethernet-class ports are preferred when available, with Wi-Fi as fallback.

User LaunchAgents:

```text
com.user.haos-start
com.user.haos-watch
```

`haos-start` waits for host state, then starts or confirms the UTM HAOS VM.

`haos-watch` checks host state, reconciles the UTM bridged interface to the selected Mac LAN interface, then uses `utmctl exec` through the guest agent to repair HAOS routing when repair is needed. It intentionally does not depend on `ssh haos` before repair, because a stale gateway can make SSH unreachable. After a successful check or repair, it writes `~/.ha_host/haos-watch-state.json`. Later watch runs skip both UTM config access and `utmctl exec` when the host LAN IP, prior UTM bridge, HAOS interface, and guest device are unchanged. SSH is only the final health check after guest-agent repair or cached match. If the cached health check fails, the watch falls back to UTM config and guest-agent repair. This cached steady state intentionally trusts the last verified UTM bridge. After manual UTM network edits, run the orchestrator doctor or remove `~/.ha_host/haos-watch-state.json` before relying on the next watch run.

By default, the installer allows forced bridge restart. If UTM must move the VM from one Mac interface to another, `haos-watch` requests a graceful VM stop first. If that stop times out, it force-stops the VM, updates the UTM config, and starts the VM again. Use `--no-force-bridge-restart` when this should fail instead of forcing the VM off. The installer can also disable changes with `--no-utm-bridge-apply` or `--no-haos-gateway-apply`.

macOS may prompt that `python3.12` wants to access another app's data when `haos-watch` reads or edits UTM's sandboxed VM config. Cached steady-state checks avoid UTM data access, but unattended bridge recovery still needs this permission ahead of time. Run the orchestrator `doctor.sh` interactively after install and allow the prompt, or grant the Python binary in the launchd plist Full Disk Access before relying on automatic recovery.

The launchd installer preflights read/write access to the UTM VM package with the shared agent Python. If macOS prompts, allow it during install so later bridge recovery can run unattended. Use `--skip-utm-permission-preflight` only when the VM does not exist yet or permission will be granted another way.

The master and HA host profiles use the shared agent Python:

```text
~/.local/share/agent-dotfiles/python/bin/python
```

Grant App Data or Full Disk Access to that shared agent Python when unattended bridge recovery needs access to UTM's sandboxed VM config. `doctor.sh` reports whether the shared agent Python is in use.

## Verify

```sh
launchctl print system/com.user.ha-host-startup
launchctl print system/com.user.ha-host-watch
launchctl print gui/$(id -u)/com.user.haos-start
launchctl print gui/$(id -u)/com.user.haos-watch
ha-host/tools/orchestrator/scripts/doctor.sh
tail -n 80 ~/.ha_host/host-startup.log
tail -n 80 ~/.ha_host/host-startup.err
tail -n 80 ~/.ha_host/host-watch.log
tail -n 80 ~/.ha_host/host-watch.err
tail -n 80 ~/.ha_host/haos-start.log
tail -n 80 ~/.ha_host/haos-start.err
tail -n 80 ~/.ha_host/haos-watch.log
tail -n 80 ~/.ha_host/haos-watch.err
cat ~/.ha_host/haos-watch-state.json
```

Then verify the router and HAOS state:

```sh
cd ~/agent-dotfiles
PYTHON=~/.local/share/agent-dotfiles/python/bin/python
PYTHONPATH=ha-host/tools/orchestrator/src \
  "$PYTHON" -m ha_host_orchestrator.entrypoints.host_startup --check-only --no-require-utun
PYTHONPATH=ha-host/tools/orchestrator/src \
  "$PYTHON" -m ha_host_orchestrator.entrypoints.host_watch --check-only --no-require-utun
ssh haos 'ha network info'
```

The installed runtime copy lives under:

```text
/usr/local/libexec/agent-dotfiles/orchestrator/
```

The checked-in source lives under:

```text
ha-host/tools/orchestrator/
```

If the installed copy needs to be repaired, use that tool's own README and installer from `ha-host/tools/orchestrator/`. Keep that operation separate from HAOS network configuration.
