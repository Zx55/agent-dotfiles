# Home Assistant Bridge

Use this reference when the user asks whether Home Assistant can bridge devices into 米家, whether 米家 or geek mode can trigger Home Assistant, or how to integrate non-Mi devices such as LG webOS TVs, PS5-adjacent flows, MQTT devices, or custom scripts while keeping 米家 as the primary control surface.

## Contents

- Direction Matters
- Common Online Meaning Of HA + Mi Home
- Official Xiaomi Home Virtual Event Bridge
- HTTP And MQTT Capability Matrix
- 米家 Or Geek Mode To HA
- HA To 米家 Or Geek Mode
- Recommended Pattern For HA-Backed Scenes
- HA-Owned Device State Mirrors In 米家
- State-Machine Caveat For Virtual Events
- Security And Reliability
- Review Questions

## Direction Matters

Always identify the bridge direction before recommending an implementation:

- 米家设备 -> Home Assistant: HA imports Xiaomi/Mi Home devices and represents them as HA entities. This is the most common meaning of "HA 接入米家" in public tutorials.
- Home Assistant -> 米家: devices, scripts, or scenes already owned by HA are exposed back to 米家, 小爱, or geek mode. This is not solved by merely installing a Xiaomi integration in HA.
- 米家 App <-> geek mode: virtual events bridge two Xiaomi-owned automation surfaces. This stays inside 米家/中枢网关 automation.
- 米家/geek mode -> HA action: a Xiaomi-side trigger calls or indirectly signals Home Assistant. This can be a network-capable action, relay device, cloud bridge, Matter bridge, or the official Xiaomi Home integration observing a central-gateway virtual-service event. A virtual event alone is not an HA webhook.

Do not collapse these into one "bridge" design. A flow that imports 米家 devices into HA does not automatically make LG TV, PS5 status, or HA scripts appear in 米家 App.

## Common Online Meaning Of HA + Mi Home

Public guides most often describe one of these patterns:

1. Xiaomi/Mi Home devices are imported into Home Assistant through an integration.
2. HA then automates those devices or re-exports selected entities to another ecosystem, commonly HomeKit, Google, Alexa, or a third-party Matter bridge.
3. Xiaomi central gateway local mode can reduce cloud dependence for supported devices, but support depends on firmware, region, device type, and current integration behavior.

Current source notes:

- Official Xiaomi Home Integration for Home Assistant, `XiaoMi/ha_xiaomi_home`, is Xiaomi-supported and lets HA use Xiaomi IoT devices. It uses OAuth login and can subscribe to device messages through Xiaomi cloud MQTT or, with supported central gateway local mode, through the gateway's MQTT broker. Its FAQ says Bluetooth, infrared, and virtual devices are not supported. That limitation does not rule out using the real central gateway device's exposed virtual-service event/action as a bridge when the user's HA instance actually shows those entities or notify actions.
- Home Assistant's built-in Xiaomi Home / miio page covers legacy Xiaomi device and gateway support. It requires devices to be set up in Mi Home and notes subnet/VLAN caveats.
- Home Assistant's official Matter integration is a Matter controller. Official HA docs explicitly say Home Assistant is not a Matter bridge by itself and cannot turn existing HA devices into Matter devices. Third-party Matter bridge add-ons may expose HA entities to other Matter controllers, but this is a separate, custom bridge layer and must be tested with 米家 specifically.

## Official Xiaomi Home Virtual Event Bridge

Reference: `https://www.bilibili.com/video/BV1fYruYiE26/`, `https://www.bilibili.com/video/BV1NwNLexEqt/`, and `https://www.bilibili.com/video/BV1gYKHepEoE/`.

The official Xiaomi Home integration can be used as a bidirectional bridge when both of these are true:

1. Home Assistant has imported the user's central gateway through the Xiaomi Home integration.
2. The central gateway exposes the virtual-service event name and the action/notify entry for producing a virtual event.

Reusable pattern:

- 米家 App, 小爱, or geek mode produces a central-gateway virtual event with a scene-level name, such as `movie_mode`, `light_off_request`, or `season_winter`.
- HA automation watches the central gateway's virtual-service event name change and runs an HA script.
- HA can report back by calling the central gateway's exposed "produce virtual event" action/notify entry with another scene-level event name, such as `ha_light_off_done` or `ha_light_off_failed`.
- Geek mode can receive that returned event, update a variable, branch on timeout, or ask a speaker to play success/failure text.

This is still not a generic "all HA devices appear in 米家" bridge. Treat it as an event bus for scene commands, status acknowledgements, and a few mode/state mirrors. Let HA keep owning HA-only device details, and let 米家/geek mode keep owning household logic and local Xiaomi device logic.

## HTTP And MQTT Capability Matrix

Current public-source status:

| Side | Receive HTTP | Send HTTP | Receive MQTT | Send MQTT | Notes |
| --- | --- | --- | --- | --- | --- |
| Home Assistant | Yes, webhook trigger | Yes, `rest_command` | Yes, MQTT trigger/entities | Yes, `mqtt.publish` | HA can be both the receiver and sender if the integration or broker is configured. |
| Xiaomi Home Integration in HA | N/A for user automations | Controls Xiaomi devices through Xiaomi cloud HTTP or gateway MQTT internally | Subscribes to Xiaomi cloud or central-gateway MQTT internally | Publishes Xiaomi device commands internally in local mode | This is the integration's implementation detail. It may expose central-gateway virtual-service events/actions when the gateway is imported, but its FAQ still says virtual devices are unsupported. Verify the exact HA entity/action before designing around it. |
| 米家 App / geek mode | Not confirmed as a generic server | Not confirmed as a generic HTTP client | Not confirmed as a generic broker client | Not confirmed as a generic MQTT publisher | Treat direct HTTP/MQTT actions as unavailable until the user's live UI shows a concrete card/action. Existing public geek-mode tutorials center on device actions, variables, loops, and virtual events. |

Implication: HA's webhook/MQTT support only solves the HA side. A 米家-side flow still needs a verified way to emit the signal. If no direct HTTP/MQTT card exists, use a relay that HA can observe, such as a supported switch, plug, or harmless Xiaomi device property.

## 米家 Or Geek Mode To HA

If the user wants 米家 or geek mode to trigger an HA script, use this decision order:

1. If the user's HA instance imports the central gateway and exposes the virtual-service event name, use a central-gateway virtual event as the scene command. This is the preferred local Xiaomi-owned bridge when available.
2. Check the user's live 米家 App or geek-mode UI for a direct network action. If it can send HTTP, call an HA webhook. If it can publish MQTT, publish to HA's MQTT broker.
3. If there is no direct event or network action, use a Xiaomi-owned relay that HA can observe. Examples include a supported switch, plug, register-like virtual device, or harmless device property. 米家/geek mode changes the relay, HA watches the imported entity, then HA runs the script.
4. If HA cannot observe the relay through the official Xiaomi integration, test another integration or bridge before designing the automation around it.
5. If the target is only a voice/manual command, consider keeping the visible command in 米家 and using HA only for state observation or follow-up actions.

Home Assistant supports webhook and MQTT triggers, but that only solves the HA receiving side. The Xiaomi side must still have a verified way to send the HTTP request or MQTT message.

Webhook receiving pattern in HA, if the Xiaomi side can send HTTP:

```yaml
automation:
  triggers:
    - trigger: webhook
      webhook_id: lg_movie_mode
      allowed_methods:
        - POST
      local_only: true
  actions:
    - action: script.lg_movie_mode
```

MQTT receiving pattern in HA:

```yaml
automation:
  triggers:
    - trigger: mqtt
      topic: mihome/scene/lg_movie_mode
      payload: "on"
  actions:
    - action: script.lg_movie_mode
```

Do not store real webhook IDs in this skill or in durable examples from the user's home. Treat webhook IDs like passwords.

Default relay receiving pattern in HA, when Xiaomi cannot send HTTP/MQTT:

```yaml
automation:
  triggers:
    - trigger: state
      entity_id: switch.mihome_lg_movie_mode_relay
      to: "on"
  actions:
    - action: script.lg_movie_mode
```

The relay entity name above is illustrative. In a real home, first verify that the Xiaomi device or property appears in HA through the user's selected Xiaomi integration and that its state changes quickly enough.

## HA To 米家 Or Geek Mode

If HA needs to affect Xiaomi-owned automation, prefer the least surprising owner:

- If the target is a real Xiaomi device imported into HA, let HA control that entity directly.
- If the target is a geek-mode branch or App-visible acknowledgement, and HA exposes the central gateway's "produce virtual event" action/notify entry, let HA emit a scene-level virtual event back to the central gateway.
- If the target is Xiaomi App-only logic, keep the App automation as owner and let HA change an observable relay that triggers the App or geek flow.
- If the target is geek-mode logic, use the relay to enter geek mode through a virtual event only when the user's current UI supports that path.
- If using a third-party Matter bridge, expose only scene-level switches/buttons, not every HA entity. Verify that 米家 can add and control that Matter bridge in the user's environment before depending on it.

Keep command and status separate:

- Command: 米家 or HA asks the other side to do something, such as `开启观影模式`.
- Status: the owning side reports what happened, such as `电视已开机` or `观影模式已进入`.
- State mirror: a helper entity, virtual state, or relay reflects a mode for later guards. It is not proof of the physical device state unless it is updated from the physical owner's observed state.

## Recommended Pattern For HA-Backed Scenes

For devices primarily controlled by HA, such as LG webOS TV, PS5-related TV input flows, or future MQTT devices, do not start by trying to expose the whole device model into 米家. Start with scene-level commands and a small set of status mirrors.

Pattern:

1. Integrate the device into HA and verify capabilities in HA first: power off, wake/power on, source select, volume, mute, app launch, status freshness, and failure behavior.
2. Create HA scripts for user-facing scenes, such as `观影模式`, `打开 PS5 输入`, `关闭电视`, or `夜间静音`.
3. Choose one 米家 entry surface for each script: central-gateway virtual event, manual scene, voice scene, relay switch, HTTP webhook, MQTT message, or Matter-exposed scene switch. Pick based on the user's actual UI and tested bridge path.
4. In geek mode, model only the household logic and guards: sleep mode, presence, time, lighting state, and manual override. Do not duplicate LG or PS5 protocol details there.
5. Mirror only useful state back into 米家/geek mode, such as `观影中`, `电视开机`, or `PS5输入中`. Avoid mirroring every HA attribute.
6. Test one command and one status update before expanding to a full scene.

This keeps 米家 as the main operating surface while letting HA own devices that 米家 does not natively understand.

## HA-Owned Device State Mirrors In 米家

Use this pattern when most household automation should remain in 米家/geek mode, but the physical device is owned by HA, such as an LG TV, Roon endpoint, PS5-adjacent media state, or a non-Mi light.

Ownership rule:

- HA owns the real device state because it is the side that can observe the physical device.
- 米家/geek mode owns household decisions and stores only a small mirror variable, such as `tv_power = 1/0`, `tv_input_ps5 = 1/0`, or `ha_movie_mode = 1/0`.
- The mirror variable must be updated by HA state-change automations, not only by command acknowledgements. Otherwise 米家 will be guessing after manual remote control, HA dashboard control, device failure, or reboot recovery.

Recommended state sync flow:

```text
HA device state changes
-> HA automation maps it to a simple mirror event
-> HA emits central-gateway virtual event, for example ha_tv_power_on or ha_tv_power_off
-> geek mode receives the event and sets the corresponding variable to 1 or 0
-> 米家/geek automations use that variable only as a guard or display mirror
```

Recommended command flow:

```text
米家/geek mode decides a scene should control an HA-owned device
-> 米家 emits command event, for example mihome_tv_power_on
-> HA runs the real device script
-> HA waits for the real state to change or times out
-> HA emits either a state mirror event, such as ha_tv_power_on, or a failure event
```

Do not set the 米家 mirror variable directly at command start unless it is clearly named as pending state, for example `tv_power_pending = 1`. The physical-state mirror should be updated only from HA's observed state or from a verified HA script result.

For binary mirrors, use explicit on/off event names rather than one toggle event. Toggles are hard to recover after either side misses an event.

## State-Machine Caveat For Virtual Events

Reference: `https://www.bilibili.com/video/BV1NwNLexEqt/`.

When HA watches the central gateway's virtual-service event name as a state or attribute change, repeated writes of the same event name may not trigger again because the observed value did not change. This matters for voice/manual commands such as "关灯" that users may issue repeatedly.

Use one of these patterns:

- Alternate request values, such as `light_off_request_1` and `light_off_request_2`.
- Reset to a neutral value after handling, then allow the next command to write the request value again.
- Use a distinct acknowledgement event from HA, such as `ha_light_off_done`, only after the HA-side script has finished.

For failure feedback, pair a timeout in geek mode with a local variable. Set the variable to pending when the request event starts, update it when the HA acknowledgement event arrives, and after a short delay announce failure only if the variable is still pending.

## Security And Reliability

- Keep HA webhooks local-only unless remote access is explicitly required.
- Use unguessable webhook IDs and do not paste them into docs, screenshots, or public examples.
- Avoid webhook commands for destructive or safety-sensitive actions such as unlocking, opening doors, or disabling alarms.
- For relay-device bridges, document the relay's real purpose in the flow name or event registry, otherwise it will look like an unrelated switch/property.
- Prefer one scene command per bridge path. Broad "execute arbitrary HA service" bridges are harder to audit and easier to trigger accidentally.
- Verify after HA, gateway, router, and proxy restarts. Bridge designs that depend on cloud MQTT, local gateway MQTT, central-gateway virtual events, Matter, or relay device state can fail in different ways.

## Review Questions

- Which direction is this bridge actually using?
- Is the trigger source owned by 米家 App, geek mode, HA, or a third-party bridge?
- Can the Xiaomi side really send HTTP/MQTT, or are we only assuming it can?
- If using the official Xiaomi Home integration, does HA actually expose the central gateway virtual-service event/action needed for this flow?
- If using virtual-service event-name changes, what prevents repeated same-name commands from being ignored?
- For HA-owned devices, what HA state-change automation keeps 米家/geek variables synchronized with physical state?
- If a relay is used, can HA observe it reliably and fast enough?
- Does the design expose a scene-level command or a whole device model?
- Is command state separate from physical status?
- What log proves each hop: 米家 App/geek mode, HA automation, target device, and any mirrored status?
