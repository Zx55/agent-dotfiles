---
name: devflow-dev
description: Use for implementation work in projects that already have design docs and development rules. This skill enforces plan-first execution for feature work, refactors, and accepted review follow-up, with explicit step breakdowns, risks, tests, and acceptance criteria.
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

Read `references/routing.md` when deciding between Implementation Worker and Multi-Agent Development Orchestration.

### Implementation Worker

- This is the default mode.
- Do not spawn subagents in this mode.
- Use this mode for ordinary implementation, single-agent refactors, and bounded tasks assigned by a main orchestrator.
- Every change starts with a plan unless the user or orchestrator explicitly says the plan is approved and asks you to write code directly.
- When assigned by `devflow-rev` or `devflow-dev` orchestration, follow the assigned ownership, expected files, do-not-touch areas, tests, and acceptance criteria.
- Do not re-enter multi-agent mode from a subagent task.

### Multi-Agent Development Orchestration

- Use this mode only when the user explicitly asks for `multi-agent`, subagents, parallel development, delegated implementation, or asks that subagents do the development work.
- The main agent becomes the orchestrator and owns planning, durable plan documents, task assignment, integration, testing, commits, and user reporting.
- Subagents are implementation workers and must use `$devflow-dev` in Implementation Worker mode, not Multi-Agent Development Orchestration.
- For subagents that write or modify code, always spawn them with model `gpt-5.5` and reasoning effort `high`.
- When explicitly setting a subagent model or reasoning effort, spawn with `fork_context=false`; include all required task context in the prompt instead of relying on full-history fork context.
- Lightweight subagent models may be used only for read-only code exploration, investigation, or summarization tasks with no file edits.
- Read `references/multi-agent.md` before spawning or assigning subagents.

## Development Activities

These activities can appear in Implementation Worker mode or as the main agent's planning/integration work during Multi-Agent Development Orchestration.

### Feature Planning

- Based on the docs and current implementation state, propose candidate implementation plans and priorities.
- Be explicit about what should be done and what should not be done.
- After the user selects a plan, expand it into concrete steps with files, risks, tests, and acceptance criteria.

### Plan Execution

- Implement the approved plan or assigned step.
- Keep changes surgical and traceable to the approved plan.
- Run the relevant tests and report anything that could not be verified.

### Accepted Review Follow-Up

- Treat an accepted review report or review finding as implementation input.
- Do not re-litigate review validity unless implementation reveals a concrete contradiction or hidden risk.
- If review validity is unclear, route the issue back to `$devflow-rev` instead of deciding it inside `$devflow-dev`.
- If the accepted review input is missing implementation details, add a plan with acceptance criteria before coding.

## Hard Rules

- By default, every change must start with a plan.
- Do not modify code or documents until the user approves the plan.
- Only skip the planning step if the user explicitly says to write code directly or edit directly.
- Do not widen public surface area just to make implementation or testing easier.
- If a change affects design boundaries, workflow semantics, persistence format, or testing boundaries, explicitly state which documents need to be updated.
- Default to Implementation Worker unless the user explicitly requests Multi-Agent Development Orchestration.

## Template

This skill includes one reusable feature-plan template:

- `templates/docs/development/feature-plan.template.md`

Use `feature-plan.template.md` for durable plans in both single-agent and multi-agent work.

Only write a feature-plan document after the user has approved the plan. New plan documents should normally start with `status: approved`, not `status: draft`.

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
