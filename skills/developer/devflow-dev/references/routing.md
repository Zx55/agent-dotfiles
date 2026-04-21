# Devflow Dev Routing

Use this reference to choose the operating mode for `devflow-dev`.

## Default Route: Implementation Worker

Use Implementation Worker by default.

Implementation Worker is appropriate when the user asks for:

- implementation of a known change
- a single-agent refactor
- a bug fix
- a bounded feature step
- an accepted review follow-up task
- a task assigned by a main orchestrator

In Implementation Worker mode:

- do not spawn subagents
- start with a plan unless explicitly told the plan is already approved and to write code directly
- keep changes inside the assigned ownership and file scope
- run relevant tests and report verification results
- do not commit unless the user explicitly asks or the surrounding workflow requires it

## Explicit Route: Multi-Agent Development Orchestration

Use Multi-Agent Development Orchestration only when the user explicitly asks for it.

Examples of explicit triggers:

- "multi-agent mode"
- "use subagents"
- "parallel development"
- "have subagents implement this"
- "you orchestrate and workers code"
- "delegate the feature steps to agents"

In Multi-Agent Development Orchestration mode:

- the main agent owns the overall development plan, durable plan document, task assignment, integration, verification, and commits
- subagents own bounded implementation tasks
- subagents must use `$devflow-dev` in Implementation Worker mode
- every task should trace back to a durable feature plan
- read `references/multi-agent.md` before assigning work

## Review Inputs

`devflow-dev` may execute an accepted review report, but it should not be the owner for deciding whether review findings are valid.

If the task is to evaluate a review, author a review, or decide whether findings are valid, route to `$devflow-rev`.

If the task is to implement already accepted review findings, stay in Implementation Worker mode unless the user explicitly asks for multi-agent orchestration.

## Ambiguous Requests

If the user asks for "a plan", "implementation options", "refactor plan", or "feature breakdown", that is not enough to use subagents.

Stay in Implementation Worker mode unless the user explicitly asks for subagents, multi-agent execution, parallel delegated work, or worker agents.
