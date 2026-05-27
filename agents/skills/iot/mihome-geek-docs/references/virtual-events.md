# Virtual Events

Use this reference when the user asks about 虚拟事件, 米家 App and geek-mode interop, virtual states, or how to let unsupported triggers/actions participate in geek-mode logic.

## Contents

- What Virtual Events Are For
- Bridge From 米家 App To Geek Mode
- Bridge From Geek Mode To 米家 App
- Virtual State With Custom State
- Manual And Voice Control
- Naming Guidelines
- Review Questions

## What Virtual Events Are For

Virtual events are bridge signals exposed through the central gateway automation system. They are useful when one side can observe or execute something that the other side cannot.

Reference: 易举不易, `[教程]小米中枢网关的虚拟事件怎么用？打通极客版和App联动`, BV1thiQBSE8Z.

Common uses:

- 米家 App trigger -> central gateway virtual event -> geek-mode logic.
- Geek-mode decision -> central gateway virtual event -> 米家 App automation action.
- Manual control / 小爱 voice command -> 米家 App action -> virtual event -> geek-mode flow.
- Two virtual events plus a custom state -> virtual boolean state, such as `观影模式已开启`.
- Reusable scene command, such as `客厅灯光温馨模式`, so multiple flows emit one virtual event instead of duplicating device actions.
- Internal graph split point, similar to a named function entry. A large geek-mode flow can emit `晚安-检查门`, `晚安-执行`, or `晚安-空调延时关闭` to split entry checks, retries, actions, and delayed cleanup into smaller readable graphs.

Virtual events are not magic local execution. Whether the final trigger or action is local depends on the device, gateway support, App automation implementation, and the user's current UI. Verify with logs and local/cloud indicators when precision matters.

The core reason virtual events exist is that geek mode is a local LAN service running on the central gateway, while 米家 App automations can see broader cloud-side and personal-device triggers. Virtual events let those two automation surfaces exchange simple named signals.

The App side can expose triggers that local geek mode may not own, including examples from the video such as car arrival/departure, charging completion, phone Bluetooth state, app open/close, wearable triggers, home/away personal state, outdoor environment, and sound recognition. Treat these examples as categories to inspect in the user's current App, not as guaranteed support for every account and device.

## Bridge From 米家 App To Geek Mode

Use this when the App has a trigger that geek mode cannot directly use.

Example: an older robot vacuum exposes `清扫完成` in 米家 App automation but not as a geek-mode trigger.

Pattern:

1. In 米家 App, create an automation.
2. Trigger: the App-only device event, such as `扫地机清扫完成`.
3. Action: central gateway generates a virtual event, such as `清扫完成`.
4. In geek mode, create a flow whose trigger is the virtual event `清扫完成`.
5. Continue with geek-mode state checks and actions.

Name the event as a domain fact, not a device implementation detail. Prefer `清扫完成` over `扫地机A事件转发1`.

Virtual events are text-matched signals. If two places use the same event text, they refer to the same signal. Keep an explicit event-name list in the user's own notes or in the flow naming convention, otherwise similar names will become hard to audit.

## Internal Function-Like Split Points

Use virtual events as labeled entry points when one graph becomes too large to review or when a long-running routine has distinct phases. Treat the event name as the function label and keep each downstream graph responsible for one phase.

Good split points:

- `晚安-检查门`: query current door state, announce open doors, update retry count.
- `晚安-执行`: run the actual bedtime actions after all guards have passed.
- `晚安-空调延时关闭`: own the delayed air-conditioner close path.

When using this pattern, still review the virtual event like a public API: name it by domain meaning, document which flow emits it, and ensure it cannot recursively trigger its caller unless that loop has an explicit stop condition.

## Bridge From Geek Mode To 米家 App

Use this when geek mode can decide the logic but the App owns the final action.

Pattern:

1. In geek mode, compute the condition or mode.
2. Emit a virtual event such as `关闭空调伴侣`.
3. In 米家 App, create an automation.
4. Trigger: central gateway receives the virtual event.
5. Action: App-only device control.

This keeps the core decision in geek mode while leaving unavailable device actions in 米家 App.

This pattern is also useful for finer control over App scenes. The video uses a charging-complete example: the App can emit a broad `充电完成` event, while geek mode can split the result by home/awake/sleep conditions and decide whether to do nothing, notify a phone, or ask 小爱 to speak.

## Command, Status, And Manual-Intent Events

When App automation performs an action that geek mode cannot perform directly, distinguish three meanings instead of reusing one virtual event for all of them:

- Command event: geek mode or a manual scene asks App to do something, such as `打开卧室空调`.
- Status event: App reports that its action path has completed or should be reflected in geek state, such as `卧室空调已打开`.
- Manual-intent event: a user-owned voice/manual entry point records that a person intentionally took control, such as `卧室空调主动打开`.

Use command events for App-owned device actions. Use status events as the single owner for shared variables such as `空调状态`. Use manual-intent events for override locks such as `空调锁-主动打开`, so automatic temperature logic can avoid undoing a human request while a higher-priority bedtime routine can still close the device later.

Do not let a status event emit the command event that caused it. That creates a recursive bridge. If App emits a status event after running a command, geek mode should update state or locks only.

A register or virtual-switch device can store state inside 米家, but it is still a state mirror, not proof of a real device state. It only tracks direct device control if that control path also writes the register or emits the matching virtual event.

## Virtual State With Custom State

Use this when a mode needs to be remembered.

Example: `观影模式`.

Pattern:

1. Virtual event `开启观影模式` enters a custom-state card and sets `观影中 = true`.
2. Virtual event `关闭观影模式` enters a custom-state card and sets `观影中 = false`.
3. Other lighting flows query `观影中` before auto-opening lights.
4. If `观影中 = true`, skip automatic lighting or use dimmed lighting.

This separates mode state from the devices that happen to implement the mode.

When a true global virtual state is unavailable in the current UI, older workflows sometimes use a real but low-impact device property as a relay. Treat this as a fallback pattern, not a normal virtual-event design. See [advanced-patterns.md](advanced-patterns.md) for relay cautions.

## Manual And Voice Control

For 小爱 or App manual controls:

1. Use a 米家 App manual scene or automation as the voice-visible surface.
2. Make the scene generate a virtual event.
3. Let geek mode receive the event and perform the detailed logic.

This is often easier to maintain than exposing every device action to voice control separately.

## Naming Guidelines

- Use short, stable, action-oriented names.
- Encode domain meaning, such as `洗衣完成`, `开启观影模式`, `关闭观影模式`, `离家`, `到家`.
- Avoid names tied to temporary device names or room layouts.
- Use paired names for paired states, such as `开启X` and `关闭X`.
- Do not reuse the same virtual event for unrelated meanings.

Maintain a short event registry when the home grows beyond a few events:

- Event text.
- Direction: App -> geek mode, geek mode -> App, or both.
- Owner flow.
- Meaning.
- Reset or duplicate-handling rule if it represents a mode.

## Review Questions

- Which side owns the trigger: 米家 App or geek mode?
- Which side owns the final action?
- Is the virtual event name a stable domain fact?
- Is a custom state needed to remember the event after it fires?
- Does the graph handle duplicate events?
- Is there a reset path if the mode becomes stale?
- Can logs prove that the virtual event was generated and received?
