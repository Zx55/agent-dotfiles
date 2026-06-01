# Samba Share

Use this when the user wants HAOS file access from macOS Finder or wants a file-transfer path for backups and local add-ons.

## Scope

- Supervisor add-on slug: `core_samba`.
- Script can install and start the add-on.
- Credentials, allowed shares, and share policy remain user-owned and should be configured in the HA UI.

## Install

```sh
./ha-host/agent/skills/iot/haos-addons/scripts/install-samba.sh
```

Equivalent HAOS command:

```sh
ssh haos 'ha apps install core_samba --no-progress || true; ha apps start core_samba --no-progress'
```

## Verify

```sh
ssh haos 'ha apps info core_samba | grep -E "^(name|version|state|boot):"'
```

Report whether credentials and share policy still need to be configured in the HA UI.
