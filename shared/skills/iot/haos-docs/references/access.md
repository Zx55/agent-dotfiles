# Access

Use this when choosing how to inspect or edit Home Assistant OS configuration.

## SSH First

Default management path:

```sh
ssh haos 'ha supervisor info'
ssh haos 'ls -la /config /homeassistant 2>/dev/null || true'
```

If SSH fails, do not repair networking or Terminal & SSH from this skill. Use `haos-macos-installation`.

## Config Paths

Common HAOS path mapping:

```text
/config -> /homeassistant
```

Treat the HAOS runtime config directory as source of truth. A local working copy is not authoritative unless the user explicitly says a local file is the desired source to sync.

## Samba

Samba is an alternate file access path after the Samba add-on is installed by `haos-addons`.

Use Samba when the user wants Finder/editor access or when bulk file transfer is easier. Still verify HA state over SSH after edits:

```sh
ssh haos 'ha core check'
```

Do not put Samba passwords in local files or reports.

## Do Not Edit

Avoid direct edits to these unless explicitly requested and backed up:

- `/homeassistant/.storage/*`
- database files such as `home-assistant_v2.db*`
- secrets files beyond adding references that the user owns

Prefer documented YAML, Pyscript files, UI automation exports, and HA services.
