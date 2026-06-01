# Devflow Rev Role And Tiers

Use this reference for `$devflow-rev` role boundaries, reviewer lanes, plan-critic checks, verifier checks, and subagent tiering.

## Role Boundary

`$devflow-rev` owns code review, architecture review, plan critique, review evaluation, and acceptance verification.

It does not implement fixes by default. Approved implementation belongs to `$devflow-dev`.

It does not bootstrap early project architecture or baseline docs. Project bootstrap belongs to `$devflow-arch`.

## Reviewer Lanes

`$devflow-rev` defaults to a complete review with both lanes unless the user explicitly narrows the scope.

### Code Review Lane

Owns:

- spec and request compliance
- correctness and bug risk
- security and data safety
- implementation quality
- code-level maintainability
- test placement and test coverage

### Architecture Review Lane

Owns:

- design boundary integrity
- module ownership and responsibility drift
- hidden coupling
- extensibility and long-term maintainability risks
- redundancy at system or workflow level
- deviations from `docs/design/`

Architecture review belongs to `$devflow-rev`, not `$devflow-arch`.

## Plan-Critic Lens

Use when reviewing a repair plan, remediation plan, or proposed implementation handoff.

Check:

- the plan is clear enough to execute without guessing
- ownership and file scope are explicit
- non-goals and do-not-touch areas are stated
- risks are concrete and mitigated
- acceptance criteria are testable
- planned verification is appropriate for the blast radius

## Verifier Lens

Use during acceptance review.

Check:

- claims are backed by `git diff`, code inspection, commands, tests, diagnostics, or artifacts
- missing evidence is reported as a gap, not treated as success
- pre-existing failures are separated from failures introduced by the current work
- the final report states what was verified, what was not verified, and remaining risk

## Tier Guidance

- `standard`: ordinary code review, acceptance review, and plan critique.
- `thorough`: architecture-sensitive, security-sensitive, public API, persistence, migration, or high-impact multi-file review.

Use higher effort when correctness risk is high, not merely because the task is long.

## Native Subagent Model Guidance

- Code-writing or code-modifying remediation subagents should use model `gpt-5.5` with reasoning effort `high`.
- When setting `model` or `reasoning_effort`, use `fork_context=false`.
- Because `fork_context=false` does not copy the main conversation, the subagent prompt must be self-contained.
- Read-only review subagents may own bounded Code Review Lane or Architecture Review Lane tasks.
