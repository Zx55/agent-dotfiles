# Modes

Default to `plan` when the user invokes the skill without a mode.

## audit

Use for read-only inspection.

1. Run `scripts/inspect_memories.py`.
2. Summarize the generated report path.
3. Do not create a plan and do not edit memory files.

## plan

Use for weekly automation and normal review.

1. Run `audit`.
2. Read the report.
3. Use `risk-checks.md` to classify findings.
4. Use `evidence-check.md` to verify proposed semantic edits against relevant rollout summaries before writing the plan.
5. Write a concise Markdown plan in `~/.codex-memory-maintenance/plans/`.
6. Stop without editing `~/.codex/memories`.

## apply

Use only when the user explicitly asks to apply or directly maintain memories.

1. Run `audit`.
2. Produce or refresh the plan.
3. Use `evidence-check.md` to confirm the plan evidence has not drifted.
4. Run `scripts/backup_memories.py`.
5. Apply only edits allowed by `editing-policy.md`.
6. Run `scripts/verify_memories.py`.
7. Report the backup path, edited files, and verification result.

Weekly automation must not run `apply`.
