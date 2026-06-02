# HA Bridge

Use this for Home Assistant automations that exchange events, commands, or state mirrors with another system such as Mi Home, a local device bridge, MQTT, webhook, or a voice-control surface.

Keep this reference generic. Device names in examples are illustrative only.

## Ownership Model

Identify the owner before designing:

- External system owns an entry surface, such as voice, app scene, virtual event, webhook, MQTT topic, or button.
- HA owns devices and services that HA can observe or control.
- HA bridge logic translates between event names and HA actions.
- A state mirror stores a simplified observed state for another system. It is not proof of physical state unless updated from HA's observed state.

## Event Types

Use distinct names for:

- Command event: another system asks HA to do something.
- Observed status event: HA reports what actually happened.
- Acknowledgement event: HA reports that a command path completed.
- Failure or timeout event: HA reports that a command path did not complete as expected.
- Startup sync event: HA replays current observed state after restart.

Do not reuse one event name for command intent and observed state.

## Recommended Shape

Command flow:

```text
external command event
-> HA validates event name
-> HA calls owned service or script
-> HA optionally waits for observed state
-> HA emits status, acknowledgement, or failure event
```

State sync flow:

```text
HA observed entity state changes
-> HA maps rich state to a small event name
-> HA emits the mirror event to the external system
```

Startup sync flow:

```text
HA starts
-> delay until integrations settle
-> query current HA observed states
-> emit current mirror events
```

## Review Checklist

- Are command events and observed status events separate?
- Does each shared mirror have one authoritative writer?
- Does startup or unknown-state recovery exist when the external system keeps state?
- Can repeated commands with the same event name be observed reliably?
- Does `mode` match expected repeat behavior?
- Is failure or silent continuation an intentional choice?
- Do logs prove each hop: inbound event, HA action, target state, outbound event?

## Examples

Examples may mention a TV, console, climate device, light scene, or MQTT device, but the bridge should be written around generic event maps and HA service calls. Avoid hard-coding one device family into the skill instructions.
