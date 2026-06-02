# PS5 HA Bridge

Use this when installing, updating, or verifying the local `ps5-ha-bridge` HAOS add-on from `agent-dotfiles`.

## Scope

- Source path: `ha-host/tools/ps5-ha-bridge/`.
- HAOS local add-on path: `/addons/ps5_ha_bridge`.
- Local add-on slug after Supervisor load: `local_ps5_ha_bridge`.
- Requires Mosquitto, because the add-on exposes MQTT discovery entities.
- Pairing is done in the add-on Web UI, not in add-on options.

The bridge exposes scene-level PS5 power only:

- `switch.ps5_power`.
- `binary_sensor.ps5_actual_power`.

Do not expose the full PS5 device model back into Mi Home. Mi Home / geek mode should only receive scene-level command and status events.

## Runtime State

The add-on stores runtime state outside the repo:

```text
/config/ps5-ha-bridge/state.json
/config/ps5-ha-bridge/credentials/
```

Do not copy NPSSO tokens, Remote Play credentials, or files from that runtime directory into this repo.

## Install Or Update

Install Mosquitto first:

```sh
./scripts/install-mosquitto.sh
```

Then install the local add-on:

```sh
./scripts/install-ps5-ha-bridge.sh
```

The script copies the source directory to `/addons/ps5_ha_bridge`, excluding local development artifacts such as `.venv`, then asks Supervisor to reload local add-ons and start `local_ps5_ha_bridge`.

## Pairing

Open the add-on Web UI. If no saved pairing exists, it shows:

- a discovered PS5 selector
- an `Open this page to get NPSSO` link
- an `NPSSO` field
- a `Link Device PIN` field

Get NPSSO while logged into the same PSN account:

```text
https://ca.account.sony.com/api/v1/ssocookie
```

On the PS5:

```text
Settings > System > Remote Play > Link Device
```

Enter the NPSSO token and current 8-digit PIN in the add-on Web UI. NPSSO is used once and is not saved by the bridge.

## Verify

```sh
ssh haos 'ha apps info local_ps5_ha_bridge | grep -E "^(name|version|state|boot):"'
```

In HA, verify:

- `switch.ps5_power` exists and can wake/rest the console.
- `binary_sensor.ps5_actual_power` reflects confirmed discovered state.
- The add-on log does not show repeated MQTT authorization errors.

For Mi Home/geek integration, use `binary_sensor.ps5_actual_power` for status events and `switch.ps5_power` for commands.
