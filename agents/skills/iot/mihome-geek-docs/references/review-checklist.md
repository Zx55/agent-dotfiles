# Review Checklist

Use this reference when the user asks whether a 米家自动化极客版 flow is reasonable, sends screenshots, or asks for help changing a graph.

## First Response Shape

For reviews, lead with findings. Do not start with a broad summary if there is a correctness risk.

Recommended format:

1. Decision: `可以接受`, `需要修改`, or `信息不足`.
2. Findings ordered by severity.
3. Evidence visible in screenshots, page state, or logs.
4. Proposed card-level change.
5. Verification routine.

## Information To Extract

- Intended behavior in the user's words.
- Trigger cards.
- Device state query cards.
- Custom state and variable names.
- Delay and loop cards with durations.
- True/false branch direction.
- Virtual event names.
- Final actions.
- Logs around the last run.
- Whether the flow is enabled.

## High-Risk Findings

- A loop has no visible stop path.
- A virtual event can re-trigger the same graph recursively.
- A delay assumes state is still true but no re-query happens after the delay.
- A custom state is written but never reset.
- App-owned trigger/action is modeled as if geek mode owns it.
- Multiple flows write the same custom state or variable without a clear owner.
- A device action can trigger the same source event repeatedly.
- The graph depends on cloud execution but is expected to work during network outage.
- The flow has no observable log point before the failure.
- A `查询当前状态` card is used as if it can start the flow by itself.
- A rule depends on pre-existing device state but does not query once when the rule is enabled.
- A relay device property is used as hidden global state without a naming convention or owner note.
- A long-running automation uses a shared counter but has no automation lock or release path.
- A command event also writes the state that should be owned by a status/confirmation event.
- A manual override lock can be set but no higher-priority routine or explicit close path can clear it.

## Medium-Risk Findings

- Repeated action chains should be replaced with a virtual event or reusable mode.
- Device state is read too early and may be stale by the time the action runs.
- Names are too generic, such as `事件1` or `状态2`.
- Numeric comparison lacks rounding or range guard.
- The flow handles the happy path but not manual override.
- The flow assumes all devices report state immediately after action.
- Purple event and green state ports are mixed without an explicit conversion, custom state, or compatible dual-color port.
- A variable crosses rule boundaries but is named like a local scratch value.
- A text variable branch assumes partial matching when the UI requires exact matching.
- A double-click or simultaneous-press emulation lacks a short reset window.
- App action, geek state update, and manual intent are represented by the same virtual event name.
- An automatic close path ignores a user-intent lock such as `空调锁-主动打开`.
- A large graph could be split by named virtual events, but the split events are too generic or can recursively call the original flow.

## Low-Risk Findings

- Flow can be split for readability.
- Logs could be easier to inspect.
- Variable names could be clearer.
- App/geek-mode division could be documented in the flow name.

## Review Questions

- What exactly should start this automation?
- If the trigger happens twice, what should happen?
- What should cancel the automation?
- What should happen after gateway reboot or first setup?
- What happens if someone manually changes the device state?
- Which state is authoritative: real device, custom state, variable, 米家 App, or another system?
- Which flow is the only writer for each shared variable?
- Does a lock guard a running automation, a durable mode, or a manual override?
- Is this virtual event a command, a status update, a manual-intent marker, or an internal split point?
- How will the user verify success without waiting for the real-world event?

## Fix Patterns

- Add a post-delay query before acting.
- Add a custom state for manual override.
- Move App-only trigger/action behind virtual events.
- Split state maintenance from action execution.
- Add stop condition to loops.
- Replace duplicated action chains with one named virtual event.
- Add temporary notification/log action during debugging, then remove it after verification.
- Replace a self-starting expectation on `查询当前状态` with `事件发生或状态更新` plus a downstream query.
- Enable query-on-rule-start when the automation should react to an already-true state after save/reboot.
- Convert events into custom states when downstream logic needs green state inputs.
- Build speech/notification text in a text variable before passing it to execution cards that cannot concatenate inline.
- Split App-owned device actions into command events and status events. Let status events own shared state writes.
- Add a global automation lock for long-running flows that use retry counters or delayed cleanup. Release it on success, timeout, cancellation, and fallback.
- Add a manual-intent lock when voice/manual control should block ordinary automation, and define which higher-priority routine may clear it.
- Use named virtual events as function-like split points for large graphs, such as entry, check, execute, retry, and delayed cleanup phases.

## Live Page Handling

If operating a browser/computer-use session:

1. Inspect first.
2. Report the current graph understanding.
3. Ask only if a destructive or broad edit is needed.
4. For authorized edits, change the smallest possible card/connection.
5. Run or ask the user to run a controlled test.
6. Re-check logs.

Do not export, copy, or store private screenshots unless the user explicitly requests a durable artifact.
