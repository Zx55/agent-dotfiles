# Evidence Check

Use rollout summaries as read-only evidence before planning or applying semantic memory edits.

## Scope

Evidence check is required for edits that change meaning, remove content, merge entries, or mark memories stale. It is not required for purely mechanical formatting, file-size reporting, or exact path normalization when the path meaning is unchanged.

## Plan Mode

For each proposed semantic edit:

1. Identify the target memory entry in `MEMORY.md` or `memory_summary.md`.
2. Find related evidence in `MEMORY.md`, especially `rollout_summary_files`, `rollout_path`, `thread_id`, and project keywords.
3. Open the most relevant 1-2 files under `~/.codex/memories/rollout_summaries/`.
4. Check whether the rollout evidence supports the proposed edit.
5. Record the evidence in the plan.

Each planned semantic edit should include:

- target file and section
- proposed action
- evidence file path or a clear note that no direct rollout evidence was found
- evidence conclusion: `supports`, `unclear`, or `conflicts`
- any relevant SHA-256 hash from the audit JSON when available

If evidence is `unclear`, keep the edit conservative or require user confirmation. If evidence `conflicts`, do not include the edit as apply-ready.

## Apply Mode

Before editing, rerun audit and compare the plan against current files:

1. Confirm every evidence file referenced by the plan still exists.
2. Confirm target memory files still contain the expected section or nearby text.
3. If the plan recorded hashes, compare them with the latest audit JSON.
4. Reopen evidence for edits that are broad, destructive, or potentially stale.

Stop before editing if evidence disappeared, target text drifted materially, or the evidence no longer supports the edit. Write a new plan instead.

## Rollout Handling

`rollout_summaries/` is evidence, not an editable prompt surface.

- Do not delete, truncate, rewrite, or normalize rollout files during normal maintenance.
- Absolute `/Users/<name>/...` paths in rollout files are usually historical evidence paths. Flag them in audit, but do not edit them by default.
- Only escalate rollout content when it contains likely secrets, private credentials, or sensitive project material that should not exist even in private evidence.

For public export or GitHub publication, use a separate scrub/export process. Do not treat private migration snapshot policy as public-share policy.
