# Card Model

Use this reference when explaining how 米家自动化极客版 graphs work or reviewing screenshots where card semantics matter.

## Contents

- Mental Model
- Events Versus States
- Trigger Cards Versus Query Cards
- Connection Rules
- Common Card Roles
- Reading A Screenshot
- Logs
- Modeling Rules
- Editing And Layout Tips

## Mental Model

Geek mode is a graph of cards and directed connections. A card emits a signal or value. A downstream card receives it and either evaluates a condition, updates state, waits, loops, computes, queries a device, or executes an action.

Reference: 易举不易, `小米米家极客版教程1：基础逻辑。自动化极客版的运行逻辑是怎么样的，为什么我写的联动不执行`, BV1yM411c7nR.

Read every flow as:

1. Trigger source.
2. Guards and state checks.
3. Data preparation or state update.
4. Device action or virtual event.
5. Optional logging, reset, or stop path.

## Events Versus States

An event is a moment. It happens once, such as a button press or a device reporting that something occurred.

A state is durable. It describes the current condition after an event, such as a light being on, a mode being active, or a custom boolean flag being true.

Many automation bugs come from confusing these two. Use an event when the flow should start on a moment. Use a state/query/custom-state card when later logic needs to know whether a condition is still true.

In the editor, port color is the fastest visual cue:

- Purple ports represent events.
- Green ports represent states.
- A card output that shows both purple and green can be used in either event or state context.
- Connect event to event and state to state. Mixed-capability ports can connect to either matching downstream need.

Some device properties expose only an event even when they sound state-like. For example, a low-battery signal may be modeled only as an event, while a light switch may expose both `turned on` as an event and `is on` as a state. Do not infer state availability from real-world meaning. Inspect the ports the editor actually exposes.

## Trigger Cards Versus Query Cards

The visually similar cards `事件发生或状态更新` and `查询当前状态` have different execution semantics.

- `事件发生或状态更新` is active. It can start the graph when the selected device event occurs or the selected state updates. In screenshots, it often appears as a source card without a left input port.
- `查询当前状态` is passive. It waits for an upstream signal, then reads the current value. It will not start a flow by itself just because the selected device state changed.

If a user says "I saved the flow but it never runs", first check whether they used a query card where they needed a trigger card. A query card must be connected from an upstream event, timer, virtual event, or other trigger.

Timers can also expose both event and state semantics. `0:00` as an event means the moment when midnight arrives. A time range such as `0:00-6:00` is a state-like condition that can be queried or used as a guard.

Reference: 易举不易, `米家极客版 番外篇之10大疑问解答`, BV1ag411n72L.

`规则启用时查询一次` is different from waiting for the next state update. If a device already had the target state before the rule was enabled, no state update happens. Enable query-on-rule-start when the flow must initialize from current state after saving the rule, toggling the rule on, or rebooting / re-enabling the central gateway.

The standalone `本条自动化启用时` trigger can be useful for startup loops or initial checks. If it feeds a loop, keep the interval conservative. The video guidance called out very short default intervals as risky. Use at least a second-level interval unless there is a strong reason and a stop condition.

## Connection Rules

The basic graph rule from the video tutorial is one-to-many downstream, one-upstream input:

- An output port can fan out to many downstream cards.
- A normal input port accepts one upstream connection.
- Use fan-out when one event should notify multiple independent checks/actions.
- Use separate condition or logic cards when multiple prerequisites need to be combined before one action.

This is a useful review shortcut. If a graph appears to rely on several independent lines entering one normal input port, verify whether the UI actually permits that card shape or whether a logic card is needed.

When a purple event needs to become a green state for downstream guards, use an explicit conversion or custom-state pattern rather than forcing an incompatible connection. The tutorials demonstrate turning device events into custom states and then using those states in later "all conditions true" checks.

## Common Card Roles

- Event or state update card: starts a flow when a device event happens or a watched state changes.
- Query current state card: reads the current value at the time the signal arrives. Prefer this when the decision must use fresh state.
- Execute device action card: sends an action to a device. Confirm whether the action is local or cloud-dependent in the user's UI.
- Custom state card: model a boolean state such as `观影中`, `有人在家`, or `自动灯光启用`.
- Variable cards: store text or numeric values, assign values from devices, query variable values, compute numbers, or concatenate text.
- Time/delay card: delay execution or model a wait window. Check whether the delay must be cancellable.
- Loop card: repeat a signal at an interval. Always design a stop condition.
- Logic/condition card: branch based on boolean, comparison, count, mode, or device state.

`如果/否则` style cards should be read as "an upstream event asks this card to evaluate a state condition." The event arrives on the purple side, the card queries or receives the green condition, then the graph continues along the satisfied or otherwise branch. Do not model it as a self-starting state watcher unless the card visibly has a trigger/output combination that supports that behavior.

## Reading A Screenshot

When reviewing a graph screenshot, extract:

- Flow name and whether it is enabled.
- Start cards and whether there are multiple triggers.
- Direction of every visible line.
- Branch labels such as true/false, yes/no, success/failure, or value comparisons.
- Cards that mutate custom states or variables.
- Delay and loop durations.
- Whether any action can recursively trigger the same flow.
- Whether logs show the failing card or only the final symptom.

If a line endpoint or card setting is hidden, say exactly what is not visible and ask for that panel or log.

## Logs

Use logs as the verification source after building or modifying a flow. A clean explanation should name which card should log first, what card should log next, and which branch should be taken in a test run.

For debugging:

1. Confirm the trigger fired.
2. Confirm each query returned the expected value.
3. Confirm the branch decision matched the expected value.
4. Confirm state/variable writes happened before downstream reads.
5. Confirm the final device action or virtual event was emitted.

If the trigger did not fire, the problem is usually device capability, App/geek-mode boundary, disabled automation, missing virtual event, or gateway reachability. If the trigger fired but the action did not happen, inspect conditions, query values, branch direction, and cloud/local action support.

## Modeling Rules

- Keep one flow responsible for one domain-level behavior when possible, such as `观影模式状态维护` or `走廊夜灯`.
- Separate state maintenance from action execution when the state is reused by many flows.
- Prefer named virtual events and custom states over duplicated long action chains.
- Initialize custom states and variables if a false/default value would be ambiguous after reboot or first setup.
- Use query cards right before important decisions when device state may have changed since the trigger.
- Add delay only when the physical device needs time to settle or when debouncing repeated events.
- Avoid circular graphs unless they have an explicit stop condition and a testable reason.

## Editing And Layout Tips

Reference: 易举不易, `抢跑米家极客版。小米终于出图形化编程编辑智能场景了，可玩性大大增加`, BV1wM411k7g6.

- Copy and paste similar cards after configuring one card. This preserves the selected device and property and reduces misconfiguration.
- Keep connected lines visually separated. Drag cards into readable lanes before reviewing logic.
- If a card cannot connect, inspect port colors before assuming the feature is missing.
- Use intermediate logic cards when the graph shape needs merging, conversion, or "any event triggers this next step".
- Use the UI's one-time query / current value check when validating a card's selected property, but be aware that frequent fresh queries may increase device power use on battery devices.
