# Devflow Rev Routing

Use this reference to choose the operating mode for `devflow-rev`.

Review lanes are not modes. Use lanes to decide review scope, and use modes to decide whether the work stays in one agent or is orchestrated across subagents.

## Default Route: Review-Only

Use Review-Only by default.

Review-Only is appropriate when the user asks for:

- code review
- architecture review
- review report authoring
- review finding evaluation
- document alignment review
- acceptance review after an implementation
- refactor guidance without delegated implementation

In Review-Only mode:

- do not spawn subagents
- do not implement fixes by default
- run both Code Review Lane and Architecture Review Lane unless the user explicitly requests only one lane
- produce findings, risks, repair directions, and acceptance criteria
- create or update a durable review report when the work needs a shared execution record
- verify completed work against the review report when asked

## Review Scope

- Default review scope is both lanes. See `roles-and-tiers.md` for lane ownership.
- If the user explicitly asks for code review only, skip architecture review and state that scope limit.
- If the user explicitly asks for architecture review only, skip code review and state that scope limit.

## Explicit Route: Multi-Agent Review Orchestration

Use Multi-Agent Review Orchestration only when the user explicitly asks for it.

Examples of explicit triggers:

- "multi-agent mode"
- "use subagents"
- "parallel review"
- "parallel remediation"
- "have subagents fix this"
- "you review, subagents implement"
- "split code review and architecture review across agents"
- "delegate each item to an agent"
- "use subagents to inspect or repair these findings"

In Multi-Agent Review Orchestration mode:

- the main agent owns planning, review, task assignment, integration, verification, and commits
- read-only subagents may own bounded Code Review Lane or Architecture Review Lane tasks
- code-writing subagents own bounded implementation tasks
- code-writing subagents normally use `$devflow-dev`
- every task should trace back to a durable review report
- read `references/multi-agent.md` before assigning work

## Ambiguous Requests

If the user asks for a "deep review", "thorough investigation", "detailed codebase analysis", or "implementation plan", that is not enough to use subagents.

Stay in Review-Only mode unless the user also explicitly asks for subagents, multi-agent execution, parallel delegated work, or worker agents.

If the user asks for both review and implementation but does not mention subagents, produce the review or repair plan first and ask for approval before implementing.
