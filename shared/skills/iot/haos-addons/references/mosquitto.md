# Mosquitto Broker

Use this when MQTT-backed integrations or local add-ons need the official HAOS MQTT broker.

## Scope

- Supervisor add-on slug: `core_mosquitto`.
- The script installs and starts the broker.
- User/password policy and any external MQTT exposure remain user-owned.

## Install

```sh
./scripts/install-mosquitto.sh
```

Equivalent HAOS command:

```sh
ssh haos 'ha apps install core_mosquitto --no-progress || true; ha apps start core_mosquitto --no-progress'
```

## Verify

```sh
ssh haos 'ha apps info core_mosquitto | grep -E "^(name|version|state|boot):"'
```

For MQTT discovery consumers, also verify HA's MQTT integration is connected in the HA UI after the broker starts.
