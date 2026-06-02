# Safety And Backups

Use this before HA configuration edits, migrations, or restart-heavy debugging.

## Default Backup

Prefer official HA backups for HAOS configuration work. They are managed by Supervisor, visible in the HA backup UI, and restorable through HA.

```sh
ssh haos 'ha backups new --name pre-haos-docs-YYYY-MM-DD --no-progress'
ssh haos 'ha backups list'
```

Keep the backup name and slug in the report.

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

Never store these in skill files, local docs, or reports:

- HA long-lived tokens
- webhook IDs
- Samba or MQTT passwords
- OAuth or device pairing credentials
- private household identifiers when not needed for debugging

Use placeholders in examples and say where the user should configure the secret in HA.
