# Prechecks

Run these before installing or updating any HAOS add-on, custom integration, or local add-on.

## Management Boundary

```sh
ssh haos 'ha supervisor info'
ssh haos 'ha network info'
ssh haos 'ha resolution info'
```

Confirm:

- `ssh haos` works without a password prompt.
- Supervisor is healthy and supported.
- `host_internet: true`.
- `supervisor_internet: true`.
- No blocking resolution issue is present.

If any of these fail, use `haos-macos-installation` first. Do not debug UTM, Terminal & SSH, or `mac-router` from this skill.

## Disk And Backup

Check `/config` capacity:

```sh
ssh haos 'df -h /config'
```

Create an official HA backup before touching `/config/custom_components`, local add-on source under `/addons`, or add-on options:

```sh
ssh haos 'ha backups new --name pre-haos-addons-YYYY-MM-DD --no-progress'
ssh haos 'ha backups list'
```

Keep the backup name and slug in the report. Do not include secrets.

## Network Endpoints

For network installs, verify the relevant endpoint before changing runtime state:

```sh
ssh haos 'curl -I --connect-timeout 8 https://github.com/'
ssh haos 'curl -I --connect-timeout 8 https://registry-1.docker.io/v2/'
```

`registry-1.docker.io/v2/` returning `HTTP/2 401` is a healthy reachability result.
