---
name: miair-installation
description: Install, configure, repair, and verify MiAir for AirPlay or DLNA bridging to Xiaomi AI speakers. Use only when explicitly asked to set up MiAir on macOS native launchd or Linux/OpenWrt/NAS Docker host networking, manage fixed MiAir paths, configure Xiaomi cookie-based login, set up launchd autostart, diagnose discovery or playback issues, update MiAir, or advise on router DHCP fixed IP binding for MiAir.
---

# MiAir Installation

Install and maintain MiAir as a local bridge that advertises AirPlay or DLNA on the LAN and asks Xiaomi AI speakers to play the bridged HTTP audio stream.

Do not use this skill for ordinary AirPlay listening, speaker control, general Xiaomi smart-home questions, or proactive installation work after MiAir is already healthy. Runtime usage and product research belong outside this setup skill unless the user asks for install, update, repair, verification, or DHCP binding help.

MiAir setup is machine-local. Never store Xiaomi account cookies, `passToken`, router admin credentials, or home IP details in this repository.

## Source Of Truth

Upstream project: `https://github.com/KiriChen-Wind/MiAir`

### macOS Native Setup

- macOS native install root: `~/.local/share/miair`
- macOS config root: `~/.config/miair`
- macOS state and logs: `~/.local/state/miair`
- macOS launchd-visible executable: `~/.local/share/miair/bin/MiAir`
- macOS wrapper console script: `~/.local/share/miair/venv/bin/miair-macos-wrapper`
- macOS launchd plist: `~/Library/LaunchAgents/com.user.miair.plist`

MiAir upstream defaults to `--conf-path conf`, so native `python miair.py` stores config in `./conf/config.json` relative to the current working directory. Always pass an explicit config path.
Do not patch files under `~/.local/share/miair/src`. macOS-local behavior belongs in the repo-managed wrapper at `agents/tools/miair-macos-wrapper`.

### Linux/OpenWrt/NAS Docker Setup

- Linux Docker source root: `/opt/miair/src`
- Linux Docker config root: `/opt/miair/conf`
- Linux Docker container: `miair`

## Workflow

1. Identify the target platform.
   - For the user's current Mac, prefer macOS native deployment.
   - For Linux, OpenWrt, NAS, soft router, or Raspberry Pi, use Docker host networking.
2. Confirm the LAN IP strategy.
   - MiAir should run with a stable LAN IP.
   - Prefer a router DHCP reservation for the host.
   - Pass that IP as `--hostname` on macOS or `MIAIR_HOSTNAME` in Docker.
3. Run the relevant doctor before changing state when the user asks for repair or diagnosis.
4. Install or update with the bundled script.
5. Open the Web UI and configure Xiaomi login through cookie fields.
6. Verify that iPhone and MiAir host are on the same LAN, then test AirPlay discovery and playback.

## macOS Native

Use [references/mac-native.md](references/mac-native.md) for the full path, launchd, and troubleshooting notes.

Install or update:

```bash
scripts/install_macos_native.sh --hostname <mac-lan-ip>
```

Useful checks:

```bash
scripts/miair_doctor.sh mac --hostname <mac-lan-ip>
launchctl print "gui/$(id -u)/com.user.miair"
tail -f ~/.local/state/miair/stderr.log
```

The macOS script installs Homebrew formulae `uv`, `ffmpeg`, and `portaudio` if missing, clones or updates MiAir under `~/.local/share/miair/src`, creates and maintains `~/.local/share/miair/venv` with `uv`, installs MiAir and `agents/tools/miair-macos-wrapper` into that venv, writes `~/.local/share/miair/bin/MiAir` as the launchd-visible executable, writes a launchd plist, and loads the service. The wrapper may adapt macOS-local behavior such as preferring the configured `--hostname` for AirPlay mDNS address publication, exporting that hostname as `MIAIR_HOSTNAME` for upstream RTSP authentication code, or adding a macOS native `dns-sd -R` RAOP registration, but it must not modify files under `~/.local/share/miair/src`.

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

The host running MiAir should have a router DHCP reservation. If the Mac leaves home and later rejoins the same Wi-Fi, MiAir usually works again without reconfiguration when it receives the same LAN IP.

## Verification Expectations

After setup, report:

- install path and config path
- selected LAN IP
- service status from launchd or Docker
- Web UI URL
- whether AirPlay discovery was tested
- any verification that could not be run
