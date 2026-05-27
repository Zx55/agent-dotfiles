---
name: mihome-geek-docs
description: Guide Mi Home / Xiaomi Home automation geek-mode work for Xiaomi central gateway users. Use when Codex needs to explain, design, review, or troubleshoot 米家自动化极客版 flows, especially screenshots of card graphs, virtual-event bridges between 米家 App and geek mode, custom states, variables, loops, delayed actions, device capability questions, browser/computer-use inspection of a local geek-mode page, or advanced smart-home automation patterns.
---

# MiHome Geek Docs

Use this skill to help with 米家自动化极客版 as an operating guide, not as a generic smart-home explainer. Treat the user's live gateway UI, screenshots, logs, and 米家 App device capability lists as the source of truth for their home. Public tutorials are supporting evidence because gateway firmware, browser UI, device local-access support, and card behavior can drift.

Never preserve login codes, home IPs, room names, device names, account identifiers, or screenshots containing private household details in durable files unless the user explicitly asks. When reporting from screenshots, anonymize room and device names unless the exact name is needed to debug a flow.

## Task Router

- Basic setup, gateway entry, browser requirements, and login-code flow: read [references/setup-and-login.md](references/setup-and-login.md).
- Card semantics, graph-reading, triggers, states, query cards, execution cards, logs, and common modeling mistakes: read [references/card-model.md](references/card-model.md).
- Virtual events, 米家 App <-> geek-mode bridging, virtual states, manual-control handoff patterns, and function-like graph split points: read [references/virtual-events.md](references/virtual-events.md).
- Variables, loops, polling, dynamic delay, custom states, reusable modes, automation locks, override locks, unsupported triggers, and advanced patterns: read [references/advanced-patterns.md](references/advanced-patterns.md).
- Reviewing a user-provided automation screenshot or live page: read [references/review-checklist.md](references/review-checklist.md).
- Source links and what each source is useful for: read [references/source-map.md](references/source-map.md).

Load only the reference needed for the user request. If the request spans design and review, start with the review checklist, then load the specific concept reference for the weak point.

When distilling videos or other long tutorials into this skill, write the notes into the topic-specific reference that will be used later, such as virtual events, card model, advanced patterns, or review checklist. Do not create a standalone video-notes file unless the user explicitly asks for a viewing log. Add short inline provenance such as "Reference: <video title or URL>" near the relevant section when it materially supports the guidance.

## Workflow

1. Identify the artifact the user wants: explanation, flow design, screenshot review, live-page inspection, troubleshooting, or durable doc update.
2. Identify the current source of truth: user screenshot, live browser page, 米家 App automation page, gateway logs, or public tutorial. Prefer live UI and logs over memory.
3. Restate the intended behavior in plain terms before judging the graph: trigger, guard conditions, state updates, side effects, recovery path, and expected logs.
4. Check whether the flow crosses ownership boundaries. 米家 App owns App-only triggers/actions. Geek mode owns graph logic, state, variables, local card orchestration, and virtual-event receivers. Virtual events are the bridge.
5. Review for correctness risks before style: accidental repeated triggers, loops that cannot stop, stale states, cloud/local mismatch, missing initialization, race conditions after device-state changes, and action chains that cannot be observed in logs.
6. Give a concrete fix pattern and a verification path. Prefer small test flows, temporary logging cards, and one-device dry runs before changing whole-home routines.

## Browser Or Screenshot Handling

When the user provides screenshots, inspect the visible card titles, ports, line direction, disabled/enabled state, and any warning or log text. Ask for an additional screenshot only if a connection, card setting, or log detail is not visible enough to answer.

When the user asks to inspect or operate the local geek-mode page, use the browser/computer-use capability available in the environment. Avoid changing flows unless the user explicitly asks for edits. For live operations, first collect state, then propose the minimal click path, then perform it if the user's request clearly authorizes changes.

## Output Expectations

For design help, return:

- Goal and assumptions.
- Recommended graph structure.
- Where 米家 App, virtual events, and geek mode each own behavior.
- Edge cases and verification steps.

For review help, return:

- Findings first, ordered by risk.
- The visible evidence from screenshot/UI/logs.
- Suggested rewrite or card-level change.
- A small verification routine.
