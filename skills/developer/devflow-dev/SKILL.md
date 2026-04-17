---
name: devflow-dev
description: Use for implementation work in projects that already have design docs and development rules. This skill enforces plan-first execution for both feature work and review-driven fixes, with explicit step breakdowns, risks, tests, and acceptance criteria.
---

# Devflow Dev

Use this skill for implementation work in a project that already has defined boundaries and development rules.

Read these first:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/design/`
4. `docs/development/review-checklist.md`
5. `docs/development/testing-guidelines.md`

## Modes

### Review-Driven

- The user may give you a review directly, or point you to a review report or review comments file.
- Analyze each review item one by one.
- If an item is valid, provide a complete modification plan.
- If an item is not valid, explain why, what risk it introduces, and what a better solution would be.
- If the review does not include acceptance criteria, add them.

### Feature-Driven

- Based on the docs and the current implementation state, propose candidate implementation plans and priorities.
- Be explicit about what should be done and what should not be done.
- After the user selects a plan, continue by breaking it down further.

## Hard Rules

- By default, every change must start with a plan.
- Do not modify code or documents until the user approves the plan.
- Only skip the planning step if the user explicitly says to write code directly or edit directly.
- Do not widen public surface area just to make implementation or testing easier.
- If a change affects design boundaries, workflow semantics, persistence format, or testing boundaries, explicitly state which documents need to be updated.

## Template

This skill includes a reusable implementation-plan template:

- `templates/docs/development/implementation-plan.template.md`

Use it as a structure guide for feature plans, review follow-up plans, and step-by-step execution proposals.

## Plan Format

Break every plan into `Step1`, `Step2`, and so on.

Each step must include:

- `Goal`
- `Do`
- `Do Not`
- `Planned Files And Purpose`
- `Risks`
- `Tests`
- `Acceptance Criteria`
- `Decision Points` if there are any

Requirements for `Planned Files And Purpose`:

- list the files or directories you expect to change
- explain why each one would be changed
- if the step does not require file edits, explicitly write `No file changes`

## Startup Behavior

- If the user invokes this skill without a concrete task, briefly explain which baseline documents you rely on, how you normally handle tasks, and that you will always produce a plan before making changes.
- If the user already gave you a concrete task, start working on that task directly. Do not say that you are ready for tasks.
