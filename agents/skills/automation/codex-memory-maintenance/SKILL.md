---
name: codex-memory-maintenance
description: Maintain Codex memory files only when explicitly invoked. Use for auditing, planning, backing up, and safely applying small maintenance edits to ~/.codex/memories.
---

# Codex Memory Maintenance

Use this skill only when the user explicitly invokes `$codex-memory-maintenance` or when an automation prompt names it.

This skill maintains Codex memories conservatively. It must not treat memories as ordinary notes. Codex owns the memory write pipeline, and this skill exists to audit, plan, back up, and apply small human-directed maintenance edits.

## Modes

Default mode is `plan`.

- `audit`: run deterministic inspection and write an audit report.
- `plan`: run `audit`, use rollout evidence to check proposed semantic edits, then produce a maintenance plan. Do not edit core memory files.
- `apply`: run `audit`, refresh or validate the plan, re-check referenced evidence for drift, back up editable files, apply only approved edits, then verify.

Read [references/modes.md](references/modes.md) before choosing behavior if the request is ambiguous.

## Required Contract Check

Before `plan` or `apply`, read [references/memory-contract.md](references/memory-contract.md). If the local memory layout, official docs, or referenced Codex source assumptions appear incompatible with that contract, stop and tell the user the skill needs to be updated before maintenance continues.

## Runtime Paths

- Codex memory root: `~/.codex/memories`
- Maintenance root: `~/.codex-memory-maintenance`
- Reports: `~/.codex-memory-maintenance/reports`
- Plans: `~/.codex-memory-maintenance/plans`
- Backups: `~/.codex-memory-maintenance/backups`

Do not write reports, plans, backups, state, or temporary files inside `~/.codex` or this dotfiles repository.

## Workflow

1. Resolve the requested mode. Use `plan` when unspecified.
2. Run inspection:

   ```bash
   python3 agents/skills/automation/codex-memory-maintenance/scripts/inspect_memories.py
   ```

3. For `audit`, summarize the report path and stop.
4. For `plan`, read [references/risk-checks.md](references/risk-checks.md) and [references/evidence-check.md](references/evidence-check.md), then write a concise plan under `~/.codex-memory-maintenance/plans/`.
5. For `apply`, read [references/evidence-check.md](references/evidence-check.md) and [references/editing-policy.md](references/editing-policy.md), run backup, apply only allowed edits, then run verification:

   ```bash
   python3 agents/skills/automation/codex-memory-maintenance/scripts/backup_memories.py
   python3 agents/skills/automation/codex-memory-maintenance/scripts/verify_memories.py
   ```

## Automation

Weekly automation should use `plan`, not `apply`. See [references/automation.md](references/automation.md).
