# Devflow Rev Routing

Use this reference to choose the operating mode for `devflow-rev`.

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
- produce findings, risks, repair directions, and acceptance criteria
- create or update a durable review report when the work needs a shared execution record
- verify completed work against the review report when asked

## Explicit Route: Multi-Agent Review Remediation

Use Multi-Agent Review Remediation only when the user explicitly asks for it.

Examples of explicit triggers:

- "multi-agent mode"
- "use subagents"
- "parallel remediation"
- "have subagents fix this"
- "you review, subagents implement"
- "delegate each item to an agent"
- "use subagents to inspect or repair these findings"

In Multi-Agent Review Remediation mode:

- the main agent owns planning, review, task assignment, integration, verification, and commits
- subagents own bounded implementation tasks
- subagents normally use `$devflow-dev`
- every task should trace back to a durable review report
- read `references/multi-agent.md` before assigning work

## Ambiguous Requests

If the user asks for a "deep review", "thorough investigation", "detailed codebase analysis", or "implementation plan", that is not enough to use subagents.

Stay in Review-Only mode unless the user also explicitly asks for subagents, multi-agent execution, parallel delegated work, or worker agents.

If the user asks for both review and implementation but does not mention subagents, produce the review or repair plan first and ask for approval before implementing.
