# PS5 HA Bridge

`ps5-ha-bridge` is a Home Assistant OS add-on for exposing scene-level PlayStation 5 power control to Home Assistant through MQTT. It exists to cover the power-control path that can be unreliable with `ps5-mqtt`/`playactor`, while activity details can stay with Home Assistant's PlayStation integration.

The add-on exposes one Home Assistant MQTT switch and one diagnostic binary sensor:

- `switch.ps5_power`: `ON` wakes the PS5, `OFF` puts it into rest mode, and the state reflects the latest discovered PS5 power status.
- `binary_sensor.ps5_actual_power`: actual PS5 power state from discovery only. Use this for automations and Mi Home/geek status events.

Power commands use a transition window: the bridge publishes the requested switch state immediately, then polls more frequently until the PS5 reports the target state or the window expires. This avoids Home Assistant briefly flipping the switch back to stale state while the console is still waking or entering rest mode.

## Ownership Boundary

- Home Assistant owns the PS5-facing bridge.
- Mi Home and geek mode should receive only scene-level commands and status events later.
- Do not expose the full PS5 device model back into Mi Home.

## Runtime State

The add-on keeps runtime state outside this repository:

```text
/config/ps5-ha-bridge/state.json
/config/ps5-ha-bridge/credentials/
```

`state.json` stores the paired PS5 host, device id, last known status, and whether the add-on is currently in re-pair mode. Remote Play credentials are stored in `credentials/`. NPSSO tokens are used once during pairing and are not saved by this bridge.

Do not commit real NPSSO tokens, MQTT passwords, paired Remote Play credentials, or files copied back from `/config/ps5-ha-bridge/`.

## HAOS Add-on

This directory is a local Home Assistant add-on:

```text
config.yaml
Dockerfile
run.sh
src/ps5_ha_bridge/addon.py
```

The add-on reads options from `/data/options.json`, reads Mosquitto service credentials from the Supervisor API, and stores PS5 pairing state under `/config/ps5-ha-bridge/`.

### Pairing

Pairing is handled through the add-on Web UI, not through add-on configuration.

If there is no saved pairing, or if `Re-pair` has been selected, the Web UI shows:

- a discovered PS5 selector
- an `Open this page to get NPSSO` link
- an `NPSSO` field
- a `Link Device PIN` field

Get an NPSSO token from Sony while logged into the same PSN account:

```text
https://ca.account.sony.com/api/v1/ssocookie
```

On the PS5, open:

```text
Settings > System > Remote Play > Link Device
```

Then enter the NPSSO token and the current 8-digit PIN in the add-on Web UI.

### Re-pair Mode

Selecting `Re-pair` stops the MQTT bridge, clears the retained Home Assistant MQTT discovery for `switch.ps5_power`, and persists `pairing_mode: true` in `/config/ps5-ha-bridge/state.json`. This removes the Power widget while the bridge is not paired.

After pairing succeeds, the add-on clears re-pair mode, restarts the MQTT bridge, and republishes the Power switch.

### MQTT Discovery

Current retained discovery:

```text
homeassistant/switch/ps5/power/config
```

Current runtime topics:

```text
ps5-ha-bridge/ps5/power/set
ps5-ha-bridge/ps5/power/state
ps5-ha-bridge/ps5/power/actual_state
ps5-ha-bridge/ps5/availability
ps5-ha-bridge/ps5/attributes/state
```

Relevant add-on options:

```yaml
bridge:
  poll_interval_seconds: 30
  availability_failures: 3
  command_transition_timeout_seconds: 60
  command_transition_poll_seconds: 1
  actual_state_confirmations: 3
```

`command_transition_timeout_seconds` is the maximum time the bridge will hold the requested switch state while waiting for PS5 discovery to catch up. During that window `attributes/state` includes `command_pending: true`. `power/actual_state` and `binary_sensor.ps5_actual_power` publish only confirmed discovered PS5 state; `actual_state_confirmations` controls how many consecutive readings are required before the diagnostic binary sensor changes.

After any power command, the bridge keeps using `command_transition_poll_seconds` until the transition timeout expires, even if the Remote Play command itself fails. Power commands run in the background so status polling continues during the command attempt. This lets Home Assistant correct the actual power state quickly without lowering the normal background poll interval.

Older retained discovery topics from earlier builds are cleared by the bridge:

```text
homeassistant/button/ps5/wake/config
homeassistant/button/ps5/standby/config
homeassistant/binary_sensor/ps5/power/config
homeassistant/sensor/ps5/status/config
homeassistant/sensor/ps5/activity/config
homeassistant/button/ps5/go_home/config
```

## Local CLI Testing

The CLI is a development and diagnostics path. The add-on Web UI is the normal pairing surface.

Install locally:

```sh
cd ha-host/tools/ps5-ha-bridge
uv venv --seed .venv
uv pip install --python .venv/bin/python -e .
```

Optional local config:

```sh
.venv/bin/ps5-ha-bridge init-config
```

Local config defaults to:

```text
~/.config/ps5-ha-bridge/config.yaml
~/.config/ps5-ha-bridge/credentials/
```

Useful checks:

```sh
.venv/bin/ps5-ha-bridge discover
.venv/bin/ps5-ha-bridge status --host <ps5-ip>
.venv/bin/ps5-ha-bridge pair --host <ps5-ip> --pin <link-device-pin> --npsso "$NPSSO"
.venv/bin/ps5-ha-bridge standby --host <ps5-ip>
.venv/bin/ps5-ha-bridge wake --host <ps5-ip>
```

For local MQTT daemon testing:

```sh
.venv/bin/ps5-ha-bridge daemon
```

The local daemon uses the same `switch.ps5_power` discovery shape as the add-on, but HAOS deployment should use the add-on.
