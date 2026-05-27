# Advanced Patterns

Use this reference for variables, loops, dynamic delays, unsupported devices, polling, reusable modes, and larger whole-home flows.

## Contents

- Variables
- Variable Card Patterns
- Variable Example: Indoor/Outdoor Temperature Difference
- Custom States
- Dynamic Delay And Debounce
- Loops And Polling
- Unsupported Triggers Or Actions
- Reusable Mode Pattern
- Staged Testing

## Variables

Use variables when a value should be reused or transformed, such as brightness, temperature, power, text message, count, or a selected mode.

Reference: 易举不易, `小米米家极客版教程8：卡片讲解5之6个变量卡片和设备执行卡片改版。米家自动化极客版变量系统怎么用`, BV1oH4y1a7r6.

Common variable cards include:

- Assign from device trigger.
- Query device value and assign.
- Update variable.
- Query variable.
- Numeric operation.
- Text concatenation.

Rules:

- Keep variable names domain-oriented, such as `夜灯亮度`, `水暖毯温度`, or `洗衣机功率`.
- Avoid using variables as hidden global state unless there is a clear owner flow.
- Query a variable immediately before decision if other flows may update it.
- Be careful with numeric precision. Round when comparing decimal values.
- If a device action accepts variables, verify the accepted type and range in a small test.

Prefer local variables for one rule and global variables only when the value must cross rule boundaries. The variable tutorial recommends making scope obvious in names. One practical convention is a prefix such as `p_` for global, `n_` for numeric, and `t_` for text, but follow the user's existing convention if one exists.

Current tutorial examples use two value families:

- Numeric variables: support comparison and math.
- Text variables: support matching and text concatenation.

When reviewing a variable flow, check type first. A text variable update usually needs an exact text match to trigger a branch. A numeric variable can participate in comparisons and formulas.

The editor may provide a current-value refresh affordance while configuring device-value assignment. Use it to verify selected property semantics before wiring a larger graph.

## Variable Card Patterns

- Device trigger assigns value: when a selected device value changes or selected event fires, store the current device value into a variable.
- Device query assigns value: an upstream signal asks the graph to query a device property and store the result.
- Variable update trigger: start or continue a graph when a variable updates and optionally matches a condition.
- Query variable value: read the current value when an upstream signal arrives.
- Numeric operation: compute a value from variables and constants, then store the result in another numeric variable.
- Text concatenation: build a text variable from literal text and variable placeholders, then feed it into speech, notification, or another text-accepting action.

In text fields that support variables, the tutorial demonstrates using `$` to open variable selection. Prefer this when composing long text to avoid switching between keyboard and mouse.

## Variable Example: Indoor/Outdoor Temperature Difference

Goal: when leaving home, remind the user to add or remove clothing if indoor/outdoor temperature difference is large.

Graph structure:

1. Outdoor temperature value changes -> assign `室外温度`.
2. Indoor temperature value changes -> assign `室内温度`.
3. Either assignment triggers numeric operation: compute `abs(室外温度 - 室内温度)` and store `室内外温差`.
4. Compare `室内外温差 >= 10`.
5. Write a boolean state or variable such as `需要增减衣物`.
6. When the leaving-home trigger fires, query `需要增减衣物`.
7. If true, speak or notify with prebuilt text such as `现在室内外温差为 X 度，注意增减衣物`.

Implementation cautions:

- If the comparison and downstream state write race each other, add a short delay before reading the comparison result. The video used a conservative delay to let the state update complete.
- Round or truncate long decimal values before speech output.
- If an execution card accepts only literal text or one variable rather than inline concatenation, build the full sentence in a text variable first, then pass that variable to the execution card.

## Custom States

Custom states are best for booleans: `在家`, `观影中`, `自动灯光启用`, `睡眠中`.

Use custom states when:

- A momentary event should become a durable mode.
- Multiple flows need the same guard.
- You need a manual override.

Avoid custom states when a real device state is authoritative and cheap to query. In that case, query the device directly.

Older tutorials used real device properties as cross-automation state relays before more direct global-state patterns were available. Examples included gateway prompt volume, night-light status, indicator-light switch, or other rarely used properties. Keep this in the toolbox for legacy setups, but mark it as a fallback because it hides automation state inside a physical device setting. Prefer virtual events, custom states, or global variables when the current UI supports them.

## Dynamic Delay And Debounce

Use delay to avoid acting on unstable physical state, such as a sensor bouncing or a device reporting multiple transitions.

Patterns:

- Door-open reminder: trigger on door open, delay, query door state again, then remind only if still open.
- Motion lighting: trigger on motion, query mode and ambient conditions, execute. For off logic, delay and re-check presence before turning off.
- Power-based completion: watch power drop, delay, query power again, then mark complete only if still below threshold.

If the delay must be cancelled by a later event, design the cancellation explicitly with a state update, stop condition, or separate flow.

For button multi-click emulation, use a counter plus reset delay. The tutorial example increments a count on single click, triggers the double-click action when count reaches two, and resets the count after a short window such as 600 ms. The review risk is stale count: if reset is missing or too long, two unrelated clicks may be treated as one double click.

For simultaneous two-switch press, use paired temporary custom states. Each switch press sets its own short-lived state true, resets it after the allowed window, and checks whether the other switch's state is currently true. Feed either ordering into a shared action path.

## Loops And Polling

Use loops only when there is no proper event trigger or when repeated gradual control is required.

Rules:

- Every loop needs a stop condition.
- Keep intervals conservative. Fast polling can burden the gateway and cause noisy logs.
- Prefer event triggers over polling when available.
- Poll by querying current state, then branch, then stop or continue.
- Record why polling is needed in the flow name or design note if the flow is complex.

Good uses:

- Periodically query a Wi-Fi device that cannot be a geek-mode trigger.
- Gradually adjust brightness or temperature.
- Watch power consumption to infer completion.

Bad uses:

- Replacing a reliable device event.
- Whole-home scans without a specific purpose.
- A loop that can survive forever after the mode is no longer relevant.

Reference: 易举不易, `今天米家更新了什么28。米家11.5。自动化执行支持循环，UI优化`, BV1TSoYB7EXK. 米家 App automation also added execution loops in later App versions, so do not assume loop semantics belong only to geek mode. Ask whether the user's loop is in App automation or geek mode before giving click-level instructions.

For 米家 App execution loops, the video demonstrates two loop styles: a finite repeat count and an always-loop mode. Finite loops are easier to review because the end is explicit. Always-loop mode needs an external stop path, such as disabling the automation or gating it with a condition. The video also notes that this App-side loop was cloud-executed at the time of the walkthrough, with local support expected later, so verify current local/cloud status in the user's UI before promising offline behavior.

Execution order matters inside App automation loops. Actions are displayed and executed from top to bottom rather than simultaneously. When reviewing a loop, check not only the interval and count, but also whether delay, device actions, notifications, and automation-enable/disable actions appear in the intended order.

## Unsupported Triggers Or Actions

When a device capability appears in 米家 App but not in geek mode:

1. Check whether 米家 App can trigger on it.
2. If yes, bridge App -> virtual event -> geek mode.
3. If no, check whether current state can be queried in geek mode.
4. If query exists, consider loop polling.
5. If neither trigger nor query exists, the capability probably cannot be owned by geek mode. Keep it in 米家 App or another system.

When geek mode can decide but cannot execute the final action, bridge geek mode -> virtual event -> 米家 App.

If neither side exposes a direct bridge but both can observe or control a harmless device property, a relay device/property can be used as a last resort. Example pattern: 米家 App changes a gateway indicator or night-light property, and geek mode watches that property as a proxy for `有人在家` or `离家`. Use clear naming and comments because future reviewers will not otherwise know why a light or volume property controls household logic.

## Automation Locks And Override Locks

Use a global variable as an automation lock when multiple triggers can start the same long-running flow and the platform does not provide a visible mutex. The lock should be part of the domain model, not a local scratch variable, because it must be read by future trigger instances.

Pattern for a long-running routine such as bedtime:

1. Entry triggers query `自动化锁-X = 0` plus the real preconditions.
2. If allowed, immediately set `自动化锁-X = 1`, initialize retry counters, and emit the next internal event.
3. Split checking, retry, execution, and delayed cleanup into separate named virtual events or clearly separated lanes.
4. Every terminal path releases the lock, including success, timeout, cancellation, and morning fallback.
5. Keep counters owned by the locked flow. Reset them before starting the loop and avoid sharing them across unlocked concurrent instances.

Use a separate override lock when a human action should block ordinary automation but not higher-priority routines. Example: `空调锁-主动打开 = 1` means temperature automation must not close an air conditioner that a person opened through a voice/manual scene. Bedtime delayed close can ignore or clear that lock if the intended household rule gives bedtime higher priority.

Do not collapse real device state, automation lock, and manual override into one variable. Use names that reveal the owner, such as `睡眠状态`, `自动化锁-晚安`, `空调状态`, and `空调锁-主动打开`.

## Reusable Mode Pattern

For modes such as `观影`, `睡眠`, `离家`, or `夜灯`:

1. One flow owns the mode state.
2. Other flows query the mode state and branch.
3. Device actions live in dedicated action flows or App automations when they are reused.
4. Voice/manual controls emit virtual events instead of directly mutating many device actions.

This reduces duplicated logic and makes review easier.

## Staged Testing

For complex flows, verify in stages:

1. Trigger-only: confirm the first card fires.
2. Query-only: confirm the queried value is the expected current value.
3. Branch-only: confirm true/false direction.
4. State update: confirm custom state or variable changed.
5. Single safe action: test one light or notification before expanding to many devices.
6. Full action chain: run once and inspect logs.
