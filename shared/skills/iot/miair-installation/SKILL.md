---
name: miair-installation
description: Install, configure, repair, and verify MiAir for AirPlay or DLNA bridging to Xiaomi AI speakers. Use only when explicitly asked to set up MiAir on macOS native launchd or Linux/OpenWrt/NAS Docker host networking, manage fixed MiAir paths, configure Xiaomi cookie-based login, set up launchd autostart, diagnose discovery or playback issues, update MiAir, or advise on router DHCP fixed IP binding for MiAir.
disable-model-invocation: true
---

# MiAir Installation

Install and maintain MiAir as a local bridge that advertises AirPlay or DLNA on the LAN and asks Xiaomi AI speakers to play the bridged HTTP audio stream.

Use this skill only for explicit setup, update, repair, verification, launchd or Docker deployment, Xiaomi cookie setup, or router DHCP binding work. Do not use it for ordinary AirPlay listening, speaker control, general Xiaomi smart-home questions, or proactive installation work after MiAir is already healthy.

MiAir setup is machine-local. Never store Xiaomi account cookies, `passToken`, router admin credentials, or home IP details in this repository.

On a Mac that also runs the HA host profile, MiAir is an optional companion service. Keep it separate from the HA host orchestrator because it is a user-session media bridge, not a root router or UTM startup component.

## Source Of Truth

Upstream project: `https://github.com/KiriChen-Wind/MiAir`

### macOS Native Setup

- Install root: `~/.local/share/miair`
- Config root: `~/.config/miair`
- State and logs: `~/.local/state/miair`
- Core launchd plist: `~/Library/LaunchAgents/com.user.miair-core.plist`
- Watch launchd plist: `~/Library/LaunchAgents/com.user.miair-watch.plist`
- Runtime Python prerequisite: `~/.local/share/agent-dotfiles/python/bin/python`, created by the master or HA host bootstrap install flow

MiAir upstream defaults to `--conf-path conf`, so native `python miair.py` stores config in `./conf/config.json` relative to the current working directory. Always pass an explicit config path.
Do not patch files under `~/.local/share/miair/src`. macOS-local behavior belongs in the repo-managed wrapper at `ha-host/tools/miair-macos-wrapper` or this skill's scripts.

Keep the macOS runtime wrapper outside this skill directory. This skill owns installation, launchd scripts, doctor checks, watcher behavior, and operator documentation. `ha-host/tools/miair-macos-wrapper` is a small Python package with its own `pyproject.toml` and tests. The installer installs it into the MiAir venv and the doctor verifies the installed console script.

### Linux/OpenWrt/NAS Docker Setup

- Linux Docker source root: `/opt/miair/src`
- Linux Docker config root: `/opt/miair/conf`
- Linux Docker container: `miair`

## Workflow

1. Identify the target platform.
   - For the user's current Mac, prefer macOS native deployment after the bootstrap has created the shared agent Python.
   - For Linux, OpenWrt, NAS, soft router, or Raspberry Pi, use Docker host networking.
2. Confirm the LAN IP strategy.
   - MiAir should run with a stable LAN IP.
   - On macOS, dynamically select the active hardware port. Prefer a wired Ethernet-class port, then fall back to a Wi-Fi or AirPort port.
   - Prefer a router DHCP reservation for the host.
   - Pass that IP as `--hostname` on macOS or `MIAIR_HOSTNAME` in Docker.
3. Run the relevant doctor before changing state for repair or diagnosis.
4. Install, update, or repair with the bundled script.
5. Configure Xiaomi login through cookie fields in the Web UI when needed.
6. Verify launchd or Docker status, Web UI reachability, LAN IP selection, and AirPlay discovery from another Apple device when available.

## macOS Native

Use [references/mac-native.md](references/mac-native.md) for full launchd, IP watcher, and troubleshooting notes.

Install or update:

```bash
scripts/install_macos_native.sh --hostname <mac-lan-ip>
```

Useful checks:

```bash
scripts/miair_doctor.sh mac --hostname <mac-lan-ip>
launchctl print "gui/$(id -u)/com.user.miair-core"
launchctl print "gui/$(id -u)/com.user.miair-watch"
~/.local/share/miair/bin/miair-watch --verbose
tail -f ~/.local/state/miair/stderr.log
tail -f ~/.local/state/miair/ip-watch.log
```

The macOS installer also installs a launchd IP watcher that runs every 5 minutes. The watcher enumerates macOS hardware ports, prefers active wired Ethernet-class ports over Wi-Fi, updates the MiAir plist when the selected IP differs from the configured `--hostname`, then reloads and restarts the MiAir service. This is a bidirectional reconcile. If wired Ethernet disappears, MiAir can move to Wi-Fi, and if wired Ethernet returns, MiAir can move back to the wired address.

## Linux Docker

Use [references/linux-docker.md](references/linux-docker.md) for the full Docker workflow and fixed paths.

Install or update:

```bash
sudo scripts/install_linux_docker.sh --hostname <linux-host-lan-ip>
```

Useful checks:

```bash
scripts/miair_doctor.sh linux --hostname <linux-host-lan-ip>
docker logs -f miair
```

The Linux script uses fixed paths under `/opt/miair`, builds a local image from upstream source, runs the container with `--network=host`, sets `MIAIR_HOSTNAME`, and starts MiAir with `--hostname "$MIAIR_HOSTNAME"` so the explicit host LAN IP overrides saved config.

## Xiaomi Cookie Setup

Use cookie login by default. Account/password login can hit Xiaomi captcha or secondary verification.

In the MiAir Web UI, open the Xiaomi account dialog and enter:

- `userId`
- `passToken`

MiAir stores these in its local config path. Treat that config as secret material. Do not copy it into repositories, screenshots, issue reports, or commits.

## Router DHCP Binding

Use [references/router-dhcp.md](references/router-dhcp.md) when the user needs fixed IP guidance.

The host running MiAir should have a router DHCP reservation. On macOS, bind the preferred hardware port used at home, usually the active Ethernet adapter or the Wi-Fi adapter. If the Mac leaves home and later rejoins the same network, the IP watcher should correct MiAir when DHCP assigns a different valid LAN IP.

## Verification Expectations

After setup, report:

- install path and config path
- selected LAN IP
- service status from launchd or Docker, including the macOS IP watcher when relevant
- Web UI URL
- whether AirPlay discovery was tested
- any verification that could not be run
