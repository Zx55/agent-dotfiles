---
name: haos-addons
description: Install, update, configure, and verify Home Assistant OS add-ons, custom integrations, and local device-bridge add-ons after HAOS is already reachable through `ssh haos`. Use for Samba share, Mosquitto broker, HACS, Pyscript, Xiaomi Home, PS5 HA Bridge, HAOS add-on status checks, and add-on troubleshooting that should run over an existing Terminal & SSH management path. Do not use for UTM VM setup, Terminal & SSH bootstrap, mac-router, or HAOS host networking repair.
---

# HAOS Add-ons

Use this skill only after the HAOS host bootstrap is complete and the Mac can run:

```sh
ssh haos 'ha supervisor info'
```

If that command fails, stop and use `haos-macos-installation` to repair Terminal & SSH, UTM networking, or Mac-side routing first.

Keep secrets out of the repo and final answer. This includes Samba passwords, MQTT passwords, Home Assistant tokens, Xiaomi account data, GitHub device codes, PSN NPSSO tokens, and PS5 Remote Play credentials.

## Source Of Truth

- HAOS runtime state: Supervisor storage and HAOS `/config`, not this repo.
- Local PS5 add-on source: `ha-host/tools/ps5-ha-bridge/`.
- Add-on/custom-integration helper scripts: `scripts/`.
- Component references: `references/`.
- Mi Home / geek automation semantics: `mihome-geek-docs`, not this skill.

## Workflow

1. Verify the management boundary.
   - Run `scripts/status.sh` or `ssh haos 'ha supervisor info'`.
   - Confirm `host_internet` and `supervisor_internet` before installing from the network.
   - Create or identify a recent official HA backup before changing `/config/custom_components` or local add-on source.
2. Read only the reference for the requested component.
   - Shared prechecks: [references/prechecks.md](references/prechecks.md)
   - Samba share: [references/samba.md](references/samba.md)
   - Mosquitto broker: [references/mosquitto.md](references/mosquitto.md)
   - HACS: [references/hacs.md](references/hacs.md)
   - Pyscript: [references/pyscript.md](references/pyscript.md)
   - Xiaomi Home: [references/xiaomi-home.md](references/xiaomi-home.md)
   - PS5 HA Bridge: [references/ps5-ha-bridge.md](references/ps5-ha-bridge.md)
3. Prefer scripts for repeatable install/update.
   - Use `scripts/install-samba.sh`, `scripts/install-mosquitto.sh`, `scripts/install-hacs.sh`, `scripts/install-pyscript.sh`, `scripts/install-xiaomi-home.sh`, or `scripts/install-ps5-ha-bridge.sh`.
   - Use `scripts/install-all.sh` only for an explicit baseline install request.
   - Set `HAOS_SSH_TARGET=<host>` when the SSH alias is not `haos`.
4. Keep interactive setup interactive.
   - Samba credentials and share policy stay user-owned.
   - HACS GitHub authorization stays in the HA UI.
   - Pyscript runtime automation logic belongs to `haos-docs` after the integration is installed.
   - Xiaomi OAuth login and device selection stay in the HA UI.
   - PS5 HA Bridge pairing stays in the add-on Web UI.
5. Verify each component separately.
   - Use the component reference's verification commands.
   - Report installed version, running state, boot policy, and any remaining interactive step.

## Common Commands

```sh
./scripts/status.sh
./scripts/install-samba.sh
./scripts/install-mosquitto.sh
./scripts/install-hacs.sh
./scripts/install-pyscript.sh
./scripts/install-xiaomi-home.sh
./scripts/install-ps5-ha-bridge.sh
```

## Acceptance Criteria

Report concrete evidence:

- `ssh haos 'ha supervisor info'` succeeded before add-on work started.
- Official HA backup status before custom integration or local add-on changes.
- For each requested component, whether it is installed, enabled or configured, restart or reload status, and boot policy when the component is a HAOS add-on.
- Any UI-only setup that remains for the user.
- Any restart performed or still needed.
