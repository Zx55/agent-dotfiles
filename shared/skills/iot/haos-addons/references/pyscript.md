# Pyscript

Use this when installing or updating Pyscript on HAOS after `ssh haos` is working.

## Scope

- Official repository: `https://github.com/custom-components/pyscript`.
- Runtime path: `/config/custom_components/pyscript`.
- Script path for user automations: `/config/pyscript`.
- Pyscript is a Home Assistant custom integration, not a HAOS add-on.

Pyscript lets Home Assistant run Python functions with state, event, time, and service triggers. It is useful for bridge logic that is always enabled and easier to maintain as code than as many UI automations.

## Install Or Update

```sh
./scripts/install-pyscript.sh
```

The script uses the upstream manual install path: download `hass-custom-pyscript.zip`, unpack it into `/config/custom_components/pyscript`, ensure `/config/pyscript` exists, append a minimal `pyscript:` block to `configuration.yaml` when missing, and run `ha core check`.

The script restarts HA Core after a successful config check unless `PYSCRIPT_NO_RESTART=1` is set.

## Configuration

Default script-managed configuration:

```yaml
pyscript:
  hass_is_global: true
```

Keep `allow_all_imports` disabled unless a script genuinely needs external Python imports. Enable it manually only after reviewing the code that will run under Pyscript.

## Finish In HA UI

If HA does not load the integration after restart, add it from:

```text
Settings -> Devices & services -> Add integration -> Pyscript Python scripting
```

For bridge scripts, keep the Python files in `/config/pyscript` and use the Mi Home / geek-mode semantics from `mihome-geek-docs`.

## Verify

```sh
ssh haos 'test -f /config/custom_components/pyscript/manifest.json && grep -n "domain\\|name\\|version" /config/custom_components/pyscript/manifest.json'
ssh haos 'grep -n "^pyscript:" /config/configuration.yaml'
ssh haos 'test -d /config/pyscript && ls -la /config/pyscript'
ssh haos 'ha core check'
```

After adding or changing scripts, inspect Home Assistant logs for `custom_components.pyscript` errors.
