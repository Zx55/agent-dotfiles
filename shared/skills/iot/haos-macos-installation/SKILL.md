---
name: haos-macos-installation
description: Install, restore, configure, and verify Home Assistant OS on a macOS UTM host. Use only when explicitly asked to set up or repair an HAOS VM on a Mac, migrate after reinstalling the Mac, restore an HA backup, configure UTM networking, install and verify Terminal & SSH as the automation boundary, verify the HA host orchestrator, or troubleshoot HAOS store/Docker/GitHub/GHCR connectivity on a macOS host.
disable-model-invocation: true
---

# HAOS macOS Installation

Use this setup skill for a Mac that runs Home Assistant OS in UTM and is managed from the same `agent-dotfiles` repository. Do not use it for ordinary Home Assistant automation design, dashboard editing, or device integration work after the HAOS host is already healthy.

Keep secrets out of the repo and the final answer. This includes Home Assistant tokens, Tailscale auth keys, router credentials, Apple ID details, and any home public IP.

## Source Of Truth

- Host bootstrap profile: `ha-host/bootstrap/`
- HA host orchestrator: `ha-host/tools/orchestrator/`
- HA host orchestrator command reference: `ha-host/tools/orchestrator/README.md`
- Local router registry runtime state: `~/.router/device.json`, not this repo
- HAOS VM runtime state: UTM and the HAOS data disk, not this repo
- HA configuration runtime state: HAOS `/config`, reachable after this skill only through a verified `ssh haos` management path

## Workflow

1. Identify the current phase.
   - Fresh Mac after iCloud sync and `agent-dotfiles` restore: run `ha-host/bootstrap/bootstrap.sh`.
   - New HAOS VM: download the official HAOS generic aarch64 qcow2 and create the UTM VM manually.
   - Existing HAOS VM: inspect UTM network mode, HAOS IP, backups, and connectivity before changing state.
   - Host routing repair: verify the installed orchestrator, launchd jobs, and HAOS network state before changing HAOS.
2. Read the specific reference for the phase.
   - Fresh or restored host flow: [references/workflow.md](references/workflow.md)
   - HAOS image and UTM settings: [references/utm-haos.md](references/utm-haos.md)
   - Current bridged networking and Mac gateway checks: [references/networking.md](references/networking.md)
   - Launchd jobs for the host orchestrator: [references/launchd-service.md](references/launchd-service.md)
   - Recovery and rollback: [references/recovery.md](references/recovery.md)
3. Prefer safe sequencing.
   - Make or identify an official HA backup before network changes.
   - Use UTM shared networking/NAT for first boot, Home Assistant Core download, initial UI onboarding, and Terminal & SSH installation.
   - Treat `Terminal & SSH` as the automation boundary: install it manually from the HA app store, configure an SSH public key, enable start-on-boot, and add a local `Host haos` entry in `~/.ssh/config`.
   - Do not rely on the Mac gateway or any scripted HAOS setup before Terminal & SSH is installed and a local `ssh haos` alias works.
   - Switch to bridged only after SSH access and a baseline official HA backup exist, or when local discovery matters and the final home-lab topology is being tested.
   - In the normal restored host state, the orchestrator launchd jobs own dynamic Mac-side LAN selection, router apply, HAOS VM startup, and drift checks. Do not install separate router scripts from this skill.
4. Verify each layer separately.
   - Mac package/tool readiness.
   - UTM VM boot and HA UI.
   - HAOS `ha network info` and `ha supervisor info`.
   - DNS and Docker registry reachability from HAOS.
   - If launchd is involved, verify all four orchestrator jobs with `launchctl print` and check the `pf` anchor. The startup jobs are one-shot tasks, so `state = not running` with `last exit code = 0` is healthy.
   - Do not hand off to add-on installation until `ssh haos 'ha supervisor info'` succeeds.

## Common Commands

Mac host:

```sh
./ha-host/bootstrap/bootstrap.sh install --dry-run
./ha-host/bootstrap/bootstrap.sh verify
PYTHON=~/.local/share/agent-dotfiles/python/bin/python
PYTHONPATH=ha-host/tools/orchestrator/src "$PYTHON" -m ha_host_orchestrator.entrypoints.host_startup --check-only --no-require-utun
PYTHONPATH=ha-host/tools/orchestrator/src "$PYTHON" -m ha_host_orchestrator.entrypoints.host_watch --check-only --no-require-utun
launchctl print system/com.user.ha-host-startup
launchctl print system/com.user.ha-host-watch
launchctl print gui/$(id -u)/com.user.haos-start
launchctl print gui/$(id -u)/com.user.haos-watch
```

HAOS through SSH:

```sh
ssh haos 'ha network info'
ssh haos 'ha supervisor info'
ssh haos 'ha resolution info'
ssh haos 'ha backups list'
ssh haos 'curl -I --connect-timeout 8 https://registry-1.docker.io/v2/'
```

Expected Docker Registry result is `HTTP/2 401`, which means the network reached the registry and authentication would be required for API access.

If `registry-1.docker.io` times out while other HA/GitHub endpoints work, use [references/networking.md](references/networking.md) to separate Clash/TUN egress issues from HAOS routing issues.

## Acceptance Criteria

Report the final state with concrete evidence:

- UTM network mode and HAOS URL
- HAOS IPv4 address, gateway, DNS servers, and IPv6 status
- `host_internet` and `supervisor_internet`
- official HA backup name and slug
- whether Terminal & SSH is installed, starts on boot, and `ssh haos ...` works from the Mac
- whether first boot/onboarding was completed through UTM shared networking/NAT before switching to bridged mode
- whether the four host orchestrator launchd jobs are installed and last exited successfully
- any recovery command needed if the network breaks
