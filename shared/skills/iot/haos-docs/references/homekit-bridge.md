# HomeKit Bridge

Use this for Home Assistant's built-in HomeKit Bridge integration, especially when HA is an auxiliary bridge for Apple Home controls rather than the primary automation system.

## Ownership Model

- Keep the household automation source of truth outside Apple Home when the user says another system owns automation.
- Treat Apple Home as a convenient local control and status surface unless the user explicitly wants Apple Home automations, sharing, or remote access.
- Do not assume an Apple Home Hub exists. Without an Apple TV or HomePod, focus on same-LAN Home app and Control Center use.
- Prefer Home Assistant HomeKit Bridge before Homebridge when the target entities already exist in HA and the required behavior is simple exposure, service calls, or state display.

## Configuration Ownership

Identify whether HomeKit Bridge is UI-owned or YAML-owned before editing.

For YAML-owned bridges, keep the include explicit:

```yaml
homekit: !include homekit.yaml
```

Use one bridge per meaningful surface or trust boundary, for example separate ports for broad device groups. Keep a stable `name` and `port`. Do not edit `.storage` directly to rename, repair, or allocate accessories. Use YAML, the HA UI, or restart/reload behavior.

For UI-created bridges, prefer UI changes unless the user explicitly wants migration to YAML. Avoid mixing UI and YAML ownership silently.

## Exposure Strategy

Expose a short, curated list first:

```yaml
- name: HA Example Bridge
  port: 21064
  filter:
    include_entities:
      - switch.example_power
      - script.good_night
      - binary_sensor.example_door
      - sensor.example_temperature
  entity_config:
    switch.example_power:
      name: Example Power
      type: switch
    script.good_night:
      name: Good Night
    binary_sensor.example_door:
      name: Front Door
    sensor.example_temperature:
      name: Room Temperature
```

Do not expose whole domains or every entity from a vendor integration at the start. Apple Home becomes hard to use when diagnostic switches, enum sensors, maintenance fields, and internal actions are exposed as accessories.

Rooms are usually best assigned in Apple Home. Do not create many HA HomeKit bridges just to model rooms. Use separate bridges only when the bridge itself has a different purpose, pairing boundary, or operational risk.

## Entity Semantics

Prefer entities that HomeKit can represent natively:

- `switch`, `light`, `button`, and `script` for simple controls. Scripts often appear as a momentary switch-like control in Apple Home.
- `binary_sensor` with `device_class` such as `door`, `window`, `opening`, `occupancy`, or `motion`.
- `sensor` with `device_class` such as `temperature` or `humidity`.
- `climate` when the HA climate entity has correct current temperature and supported modes.

Avoid exposing data that HomeKit cannot model cleanly:

- Generic percentage sensors such as liquid level or consumable remaining amount.
- Enum sensors such as charging state, replace-fluid reminder, or vendor-specific modes.
- Diagnostic events, low-level action entities, and setup helpers.

If a value matters but HomeKit has no semantic match, keep it in HA unless the user explicitly accepts a lossy representation.

## Template And Wrapper Patterns

Use template sensors when the raw entity has the wrong unit, missing device class, or awkward display name.

```yaml
template:
  - sensor:
      - name: Room Temperature
        unique_id: room_temperature
        default_entity_id: sensor.room_temperature
        device_class: temperature
        state_class: measurement
        unit_of_measurement: "°C"
        availability: "{{ states('sensor.raw_temperature') | is_number }}"
        state: "{{ ((states('sensor.raw_temperature') | float - 32) * 5 / 9) | round(1) }}"
```

Validate units from HA runtime state, not just from entity names. Some vendor integrations expose temperature values in Fahrenheit even when the physical device or UI looks metric.

Climate current temperature is read from the climate entity's `current_temperature` attribute. HomeKit Bridge `linked_temperature_sensor` does not rewrite climate current temperature. If an otherwise usable climate entity has a bad or missing current temperature, either:

- accept the original climate entity as-is, or
- create a small proxy climate entity that forwards control to the original climate and reads current temperature from a separate sensor.

Keep proxy climate entities narrow. If fan and swing services are not useful in Apple Home, do not expose fan or swing features in the wrapper because HomeKit may create extra controls.

## Linked Battery

Use linked battery services instead of exposing battery sensors as standalone HomeKit accessories.

```yaml
entity_config:
  binary_sensor.example_door:
    name: Front Door
    linked_battery_sensor: sensor.example_door_battery
  switch.example_device:
    name: Example Device
    linked_battery_sensor: sensor.example_device_battery
```

Use `linked_battery_charging_sensor` only when HA has a binary sensor where `on` means charging. Do not pass an enum sensor such as `Charging` / `Not Charging` directly.

Do not bind consumable level, liquid level, filter life, or other maintenance percentages as battery unless that is truly the device battery. Misleading battery services are worse than leaving the data in HA.

## Runtime Inspection

When the HA CLI cannot query entity states directly, inspect recorder state carefully. Copy the SQLite database and its WAL/SHM files together before reading locally:

```sh
tmpdir=$(mktemp -d /tmp/ha-db.XXXXXX)
scp -q haos:/config/home-assistant_v2.db "$tmpdir/"
scp -q haos:/config/home-assistant_v2.db-wal "$tmpdir/"
scp -q haos:/config/home-assistant_v2.db-shm "$tmpdir/"
sqlite3 "$tmpdir/home-assistant_v2.db" '.tables'
```

Query latest state and attributes through `states`, `states_meta`, and `state_attributes`. This is read-only inspection and should not replace HA Developer Tools when the UI is available.

## Verification

Before edits:

```sh
ssh haos 'ha supervisor info'
ssh haos 'ha backups new --name pre-homekit-bridge-YYYY-MM-DD --no-progress'
```

After edits:

```sh
ssh haos 'ha core check'
ssh haos 'ha core restart --no-progress'
ssh haos 'ha core logs | grep -i "homekit\|pyscript" | tail -n 100'
```

Use `.storage/core.config_entries` and `.storage/homekit.*.aids` only as read-only verification that a YAML import, include list, entity config, or linked battery service was picked up. Do not edit those files directly.

Check that:

- The bridge config entry contains the expected `include_entities`.
- Linked battery config appears under the existing accessory, not as a new included entity.
- The AID file allocated new accessories only when new accessories were intended.
- HomeKit logs do not show accessory setup failures.
- Apple Home shows the intended names, rooms can be assigned in Apple Home, and controls perform the expected HA service path.

## Reporting

Report the official backup name and slug, files changed, `ha core check` result, restart or reload performed, and what Apple Home still needs from the user, such as assigning rooms or checking a newly exposed tile.
