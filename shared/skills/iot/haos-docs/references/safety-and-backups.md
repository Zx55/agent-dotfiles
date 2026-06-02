# Safety And Backups

Use this before HA configuration edits, migrations, or restart-heavy debugging.

## Default Backup

Prefer official HA backups for HAOS configuration work. They are managed by Supervisor, visible in the HA backup UI, and restorable through HA.

```sh
ssh haos 'ha backups new --name pre-haos-docs-YYYY-MM-DD --no-progress'
ssh haos 'ha backups list'
```

Keep the backup name and slug in the report.

## File Backup Exception

Use ad hoc file copies only for trivial, explicitly temporary edits where a full HA backup would be disproportionate, or as a short-lived working checkpoint before an official HA backup exists:

```sh
./scripts/backup-config.sh configuration.yaml automations.yaml scripts.yaml
```

Clean up temporary file backups after an official HA backup is created and verified.

## Full Backup Required

Use an official HA backup before:

- large automation migrations
- custom integration changes
- add-on source changes
- `.storage` edits
- changes that may block HA startup

## Restart Safety

Before restart:

```sh
ssh haos 'ha core check'
```

If the check fails, do not restart. Restore or fix first.

## Secret Handling

Never store these in skill files, repo docs, or final answers:

- HA long-lived tokens
- webhook IDs
- Samba or MQTT passwords
- OAuth or device pairing credentials
- private household identifiers when not needed for debugging

Use placeholders in examples and say where the user should configure the secret in HA.
