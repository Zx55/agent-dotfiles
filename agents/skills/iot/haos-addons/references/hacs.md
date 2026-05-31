# HACS

Use this when the user wants HACS available for community integrations after `ssh haos` is working.

## Scope

- HACS is a custom integration under `/config/custom_components/hacs`.
- The script can download the HACS files and restart HA Core.
- GitHub authorization and the HA integration setup remain interactive in the HA UI.

## Install

```sh
./agents/skills/iot/haos-addons/scripts/install-hacs.sh
```

Equivalent HAOS commands:

```sh
ssh haos 'cd /config && wget -O - https://get.hacs.xyz | bash -'
ssh haos 'ha core restart --no-progress'
```

## Finish In HA UI

```text
Settings -> Devices & services -> Add integration -> HACS
```

Do not store GitHub device codes or tokens in durable files.

## Verify

```sh
ssh haos 'test -f /config/custom_components/hacs/manifest.json && grep -n "domain\\|name" /config/custom_components/hacs/manifest.json'
```
