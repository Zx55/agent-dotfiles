# Editing Policy

`apply` may edit only the files listed as editable. Everything else is read-only evidence or audit-only state.

## Editable

- `~/.codex/memories/MEMORY.md`
- `~/.codex/memories/memory_summary.md`

Allowed edits:

- remove or rewrite obvious low-value noise
- merge duplicate entries
- mark stale entries as superseded when removal would be risky
- normalize portable paths when meaning is unchanged
- remove secret-like content after confirming the replacement preserves necessary non-secret context

Semantic edits require evidence-check approval from `evidence-check.md` before editing.

## Audit-Only

- `~/.codex/memories/raw_memories.md`
- `~/.codex/memories/rollout_summaries/`
- `~/.codex/memories/.git/`
- unknown generated files

Do not delete, truncate, rewrite, normalize, or reinitialize audit-only paths during normal maintenance.

## Backup Requirement

Before any edit, run:

```bash
python3 agents/skills/automation/codex-memory-maintenance/scripts/backup_memories.py
```

The backup must be under `~/.codex-memory-maintenance/backups/<timestamp>/`.

## Verification Requirement

After edits, run:

```bash
python3 agents/skills/automation/codex-memory-maintenance/scripts/verify_memories.py
```

If verification fails, tell the user what failed and where the backup is. Do not attempt destructive rollback without explicit user approval.
