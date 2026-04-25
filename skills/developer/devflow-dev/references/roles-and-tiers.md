# Devflow Dev Role And Tiers

Use this reference for `$devflow-dev` role boundaries, plan-critic checks, verifier checks, and subagent tiering.

## Role Boundary

`$devflow-dev` owns approved plan execution, implementation, integration, and implementation verification.

It does not decide whether review findings are valid. Review evaluation belongs to `$devflow-rev`.

It does not bootstrap project architecture or baseline documentation from scratch. Early design bootstrap belongs to `$devflow-arch`.

## Plan-Critic Lens

Use before implementation or delegated development handoff.

Check:

- the plan is clear enough to execute without guessing
- ownership and file scope are explicit
- non-goals and do-not-touch areas are stated
- risks are concrete and mitigated
- acceptance criteria are testable
- planned verification is appropriate for the blast radius

If the plan fails this check, revise it and request approval before coding, or report the gap upward when assigned by an orchestrator.

## Verifier Lens

Use before declaring implementation complete.

Check:

- claims are backed by `git diff`, code inspection, commands, tests, diagnostics, or artifacts
- missing evidence is reported as a gap, not treated as success
- pre-existing failures are separated from failures introduced by the current work
- the final report states what was verified, what was not verified, and remaining risk

## Tier Guidance

- `standard`: ordinary implementation, debugging, and focused refactors.
- `thorough`: architecture-sensitive, security-sensitive, public API, persistence, migration, or high-impact multi-file work.

Use higher effort when correctness risk is high, not merely because the task is long.

## Native Subagent Model Guidance

- Code-writing or code-modifying subagents should use model `gpt-5.5` with reasoning effort `high`.
- When setting `model` or `reasoning_effort`, use `fork_context=false`.
- Because `fork_context=false` does not copy the main conversation, the subagent prompt must be self-contained.
- Read-only low/standard subagents may be used only for bounded exploration or summarization tasks with no file edits.
