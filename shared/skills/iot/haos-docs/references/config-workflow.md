# Config Workflow

Use this for Home Assistant configuration edits.

## Preflight

```sh
ssh haos 'ha supervisor info'
ssh haos 'ha core info'
ssh haos 'ls -la /homeassistant /config 2>/dev/null || true'
```

Read `/homeassistant/configuration.yaml` first. It defines which files or integrations own automation behavior.

If `configuration.yaml` contains `pyscript:` or `/config/pyscript` exists, include `/config/pyscript/*.py` in the review.

## Backup

Before edits, prefer an official HA backup:

```sh
ssh haos 'ha backups new --name pre-haos-docs-YYYY-MM-DD --no-progress'
ssh haos 'ha backups list'
```

Use `./scripts/backup-config.sh` only as a short-lived file checkpoint for trivial edits, or when the user explicitly asks for file-level copies. Clean up temporary file backups after an official HA backup exists.

Keep the backup name and slug in the report.

## Editing

Use the smallest ownership surface:

- `automations.yaml` for HA automation rules.
- `scripts.yaml` for reusable HA action sequences.
- `/config/pyscript/*.py` for Pyscript logic when Pyscript is configured.
- `configuration.yaml` only for integration-level configuration and includes.

Do not mix UI and file ownership silently. If an automation is UI-managed, preserve its `id` and schema unless the user explicitly wants a migration.

## Validation

Always run:

```sh
ssh haos 'ha core check'
```

Reload the smallest relevant surface after a successful check. If only automations changed, use the HA UI or available HA services to reload automations. If Pyscript changed, use the Pyscript reload path in `pyscript.md`.

Restart HA Core only when the changed surface requires it or a reload fails.

## Rollback

If `ha core check` fails after an edit:

1. Do not restart HA Core.
2. Restore from the official HA backup, or from a temporary file checkpoint if one was intentionally used for a trivial edit.
3. Run `ha core check` again.
4. Report the failed check and restored backup source.
