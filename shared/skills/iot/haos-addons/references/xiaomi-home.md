# Xiaomi Home

Use this when installing or updating the official Xiaomi Home custom integration on HAOS after `ssh haos` is working.

## Scope

- Official repository: `https://github.com/XiaoMi/ha_xiaomi_home`.
- Runtime path: `/config/custom_components/xiaomi_home`.
- Source checkout path used by the script: `/config/ha_xiaomi_home`.
- Xiaomi OAuth login and device selection remain interactive in the HA UI.

The integration imports supported Xiaomi devices into HA. It does not automatically expose HA-owned devices back into Mi Home. Keep Mi Home / geek bridge design in `mihome-geek-docs`.

## Version Policy

Use a tagged release by default. The script uses the latest tag unless `XIAOMI_HOME_VERSION=<tag>` is set.

List tags:

```sh
git ls-remote --tags --refs https://github.com/XiaoMi/ha_xiaomi_home.git |
  awk '{sub("refs/tags/", "", $2); print $2}' |
  sort -V |
  tail
```

## Install Or Update

```sh
./scripts/install-xiaomi-home.sh
```

The script runs the upstream `./install.sh /config` and restarts HA Core.

## Finish In HA UI

```text
Settings -> Devices & services -> Add integration -> Xiaomi Home
```

Do not handle or store Xiaomi account credentials in durable notes.

## Verify

```sh
ssh haos 'grep -n "domain\\|name\\|version" /config/custom_components/xiaomi_home/manifest.json'
```

After login, inspect the central gateway entities/actions needed for virtual-event bridging. Use `mihome-geek-docs` for the automation design.
