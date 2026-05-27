---
name: haos-macos-installation
description: Install, restore, configure, and verify Home Assistant OS on a macOS UTM host. Use only when explicitly asked to set up or repair an HAOS VM on a Mac, migrate after reinstalling the Mac, restore an HA backup, configure UTM networking, install Terminal & SSH/File editor/Samba/Mosquitto, configure HAOS bridged networking through the Mac as a gateway, set up or verify the haos-mac-router launchd service, or troubleshoot HAOS store/Docker/GitHub/GHCR connectivity on a macOS host.
---

# HAOS macOS Installation

Use this setup skill for a Mac that runs Home Assistant OS in UTM and is managed from the same `agent-dotfiles` repository. Do not use it for ordinary Home Assistant automation design, dashboard editing, or device integration work after the HAOS host is already healthy.

Keep secrets out of the repo and the final answer. This includes Samba passwords, Home Assistant tokens, Tailscale auth keys, router credentials, Apple ID details, and any home public IP.

## Source Of Truth

- Host bootstrap profile: `bootstrap/ha_host/`
- Mac-side router tool: `bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh`
- Mac-side router command reference: `bootstrap/ha_host/tools/haos-mac-router/README.md`
- Mac-side router launchd installer: `scripts/install-haos-mac-router-service.sh`
- Mac-side router launchd wrapper: `scripts/haos-mac-router-launchd.sh`
- Mac-side router launchd plist template: `templates/com.user.haos-mac-router.plist`
- HAOS VM runtime state: UTM and the HAOS data disk, not this repo
- HA configuration runtime state: HAOS `/config`, reachable through Terminal & SSH, File editor, or Samba

## Workflow

1. Identify the current phase.
   - Fresh Mac after iCloud sync and `agent-dotfiles` restore: run `bootstrap/bootstrap.sh --profile ha_host`.
   - New HAOS VM: download the official HAOS generic aarch64 qcow2 and create the UTM VM manually.
   - Existing HAOS VM: inspect UTM network mode, HAOS IP, backups, and connectivity before changing state.
   - Bridged network repair: use the Mac-side router tool and HAOS network commands.
2. Read the specific reference for the phase.
   - Fresh or restored host flow: [references/workflow.md](references/workflow.md)
   - HAOS image and UTM settings: [references/utm-haos.md](references/utm-haos.md)
   - Bridge, NAT, DNS, and Mac gateway routing: [references/networking.md](references/networking.md)
   - Launchd service for the Mac-side router: [references/launchd-service.md](references/launchd-service.md)
   - Recovery and rollback: [references/recovery.md](references/recovery.md)
3. Prefer safe sequencing.
   - Make a full HA backup before network changes.
   - Use UTM shared networking/NAT for first boot, Home Assistant Core download, initial UI onboarding, and Terminal & SSH installation.
   - Do not rely on the Mac gateway before Terminal & SSH is installed and a local `ssh haos` alias works.
   - Switch to bridged only after SSH access and a baseline backup exist, or when local discovery matters and the final home-lab topology is being tested.
   - Prove manual `haos-mac-router.sh apply` works before creating a launchd service.
4. Verify each layer separately.
   - Mac package/tool readiness.
   - UTM VM boot and HA UI.
   - HAOS `ha network info` and `ha supervisor info`.
   - DNS and Docker registry reachability from HAOS.
   - App installation through `ha apps install <slug>` or the HA UI.
   - If launchd is involved, verify both `launchctl print` and the `pf` anchor. The service is a one-shot rule apply job, so `state = not running` with `last exit code = 0` is healthy.
   - Before installing the launchd service on a changed network, ensure `ssh haos 'ha network info'` works or pass explicit installer arguments for HAOS IP, Mac LAN IP, DNS, and interface names.

## Common Commands

Mac host:

```sh
./bootstrap/bootstrap.sh --profile ha_host install --dry-run
./bootstrap/bootstrap.sh --profile ha_host verify
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh status
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh plan --haos-ip <haos-ip> --lan-interface en0
```

HAOS through SSH:

```sh
ssh haos 'ha network info'
ssh haos 'ha supervisor info'
ssh haos 'ha resolution info'
ssh haos 'curl -I --connect-timeout 8 https://registry-1.docker.io/v2/'
```

Expected Docker Registry result is `HTTP/2 401`, which means the network reached the registry and authentication would be required for API access.

If `registry-1.docker.io` times out while other HA/GitHub endpoints work, use [references/networking.md](references/networking.md) to separate Clash/TUN egress issues from HAOS routing issues.

## Acceptance Criteria

Report the final state with concrete evidence:

- UTM network mode and HAOS URL
- HAOS IPv4 address, gateway, DNS servers, and IPv6 status
- `host_internet` and `supervisor_internet`
- backup status
- whether Terminal & SSH, File editor, Samba share, and Mosquitto were installed or intentionally skipped
- whether first boot/onboarding was completed through UTM shared networking/NAT before switching to bridged mode
- whether the Mac-side router is manual-only or installed as a launchd service
- any recovery command needed if the network breaks
