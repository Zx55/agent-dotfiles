---
name: haos-docs
description: Use, inspect, edit, and verify Home Assistant OS configuration and automations after HAOS is already installed and reachable. Use for SSH or Samba based access to `/homeassistant`, YAML automations, scripts, Pyscript logic, entity and service inspection, logs, backups, HA config checks, reloads, restarts, and HA-side bridge automation maintenance. Do not use for macOS UTM installation, Terminal & SSH bootstrap, host networking repair, or add-on installation.
---

# HAOS Docs

Use this skill for day-to-day Home Assistant OS configuration and automation work after the HAOS host is already healthy. The normal management boundary is:

```sh
ssh haos 'ha supervisor info'
```

If that command fails, stop and use `haos-macos-installation`. If an add-on or custom integration is missing or needs installation, use `haos-addons`.

Keep secrets out of the repo and final answer. This includes Home Assistant tokens, Samba passwords, MQTT passwords, Xiaomi account data, webhook IDs, OAuth tokens, and device pairing credentials.

## Source Of Truth

- HA runtime config: `/homeassistant` or `/config` on HAOS. `/config` is often a symlink to `/homeassistant`.
- HA UI state and logs are authoritative for what is currently loaded.
- Local repo files are drafts, documentation, or backups unless explicitly synced to HAOS.
- Do not edit `.storage` unless the task explicitly requires it and a backup exists.
- Mi Home / geek-mode graph semantics belong to `mihome-geek-docs`.
- Add-on installation and custom integration installation belong to `haos-addons`.

## Task Router

- Access methods, SSH, Samba, and path mapping: read [references/access.md](references/access.md).
- Editing `configuration.yaml`, `automations.yaml`, `scripts.yaml`, and reload/restart workflow: read [references/config-workflow.md](references/config-workflow.md).
- YAML automations, scripts, UI-managed automations, and automation inventory: read [references/automations.md](references/automations.md).
- If `configuration.yaml` contains `pyscript:`, `/config/pyscript` exists, or the task involves writing or migrating Python automations, read [references/pyscript.md](references/pyscript.md) and include `/config/pyscript/*.py` in the automation inventory.
- HA-side bridge patterns between HA and another system: read [references/ha-bridge.md](references/ha-bridge.md).
- Logs, traces, entity state checks, service-call testing, and debugging: read [references/logs-and-debugging.md](references/logs-and-debugging.md).
- Backups, rollback, and safety boundaries: read [references/safety-and-backups.md](references/safety-and-backups.md).

Load only the reference needed for the current task. If the task spans multiple areas, start with `config-workflow.md`, then load the specific reference for the automation type or bridge.

## Workflow

1. Verify access.
   - Run `scripts/status.sh` or `ssh haos 'ha supervisor info'`.
   - Confirm `/config` and `/homeassistant` mapping before reading or writing files.
   - If Samba is requested, verify it as an access method, not as the source of truth.
2. Identify the artifact.
   - One-off inspection, config edit, automation design, automation migration, Pyscript maintenance, bridge maintenance, log/debug conclusion, or verification result.
3. Build an automation inventory before changing behavior.
   - Read `configuration.yaml`.
   - Read `automations.yaml` and `scripts.yaml` when relevant.
   - If `pyscript:` is configured or `/config/pyscript` exists, read `references/pyscript.md` and inspect `/config/pyscript/*.py`.
4. Back up before edits.
   - Prefer an official HA backup through `ha backups new` or the HA UI backup page.
   - Use ad hoc file copies only for trivial, explicitly temporary edits, and clean them up after an official HA backup exists.
5. Make the smallest change.
   - Keep UI-owned automations and file-owned automations distinct.
   - Do not migrate YAML to Pyscript or Pyscript to YAML unless the user asks or clearly approves.
   - Keep bridge code generic and event-name driven instead of tied to one device model.
6. Verify.
   - Run `scripts/check-config.sh` or `ssh haos 'ha core check'`.
   - Reload the smallest surface that applies: automation, script, Pyscript, or HA Core.
   - Inspect logs after reload or restart.
7. Report evidence.
   - Mention config check result, changed files, backup path, reload/restart performed, and remaining UI-only steps.

## Common Commands

```sh
./scripts/status.sh
ssh haos 'ha backups new --name pre-haos-docs-YYYY-MM-DD --no-progress'
ssh haos 'ha backups list'
./scripts/check-config.sh
ssh haos 'ha core logs | tail -n 120'
ssh haos 'ha core check'
```

## Acceptance Criteria

Report concrete evidence:

- `ssh haos 'ha supervisor info'` succeeded before HA config work started.
- The source files inspected, including Pyscript files when configured.
- Backup path or explicit reason no backup was needed.
- `ha core check` result before any restart.
- Reload or restart action performed, or why it was not needed.
- Logs, entity states, automation traces, or service-call results that verify the requested behavior.
