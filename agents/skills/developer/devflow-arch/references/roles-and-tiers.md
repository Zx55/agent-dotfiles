# Devflow Arch Role And Tiers

Use this reference for `$devflow-arch` role boundaries and effort selection.

## Role Boundary

`$devflow-arch` owns early project design and documentation bootstrap for the baseline documents listed in `SKILL.md`.

It does not own code review, architecture review of an implementation, plan critique for implementation handoff, or acceptance verification. Those belong to `$devflow-rev`.

It does not implement production code. Approved implementation belongs to `$devflow-dev`.

## Tier Guidance

- `standard`: default for ordinary project bootstrap, baseline docs, and small design updates.
- `thorough`: use when the baseline affects multiple subsystems, public workflow semantics, persistence format, security boundaries, or long-lived project rules.

Use higher effort when the documentation will constrain future implementation or review decisions.

## Output Expectations

- State the proposed documentation set before writing substantial docs unless the user explicitly asks to write directly.
- Keep rules stable, actionable, and specific to the project.
- Avoid turning early bootstrap docs into speculative future architecture.
