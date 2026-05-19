# Memory Contract

This skill is based on the current Codex memory implementation. It must stop before applying edits if this contract appears stale.

## Primary References

- Official docs: `https://developers.openai.com/codex/memories`
- Config reference: `https://developers.openai.com/codex/config-reference`
- Read prompt source: `https://github.com/openai/codex/blob/main/codex-rs/memories/read/src/prompts.rs`
- Read path template: `https://github.com/openai/codex/blob/main/codex-rs/memories/read/templates/memories/read_path.md`
- Write storage source: `https://github.com/openai/codex/blob/main/codex-rs/memories/write/src/storage.rs`
- Write workspace source: `https://github.com/openai/codex/blob/main/codex-rs/memories/write/src/workspace.rs`
- Config memory types: `https://github.com/openai/codex/blob/main/codex-rs/config/src/types.rs`

## Current Assumptions

- `memory_summary.md` is the main memory content injected into the prompt, and Codex truncates it before injection.
- `MEMORY.md` is the searchable registry and the primary file to query for memory details.
- `raw_memories.md` and `rollout_summaries/` are Codex write-pipeline material. They are read-only evidence for semantic checks and audit-only for edits.
- `skills/` may contain memory-owned skill material. It is audit-only unless the user explicitly scopes maintenance there.
- `.git` inside the memory root is Codex runtime state used as a baseline. Do not delete, rewrite, or reinitialize it.
- Memories are generated state. Manual edits are allowed only as narrow maintenance after backup and verification.

## Stop Conditions

Stop before `apply` if any of these are true:

- Expected core files are missing and Codex docs/source no longer support the expected layout.
- New core files appear to replace `MEMORY.md` or `memory_summary.md`.
- The user asks to rewrite `raw_memories.md`, `rollout_summaries/`, `.git/`, or unknown generated state.
- Rollout evidence needed for a semantic edit is missing, unclear, or conflicts with the planned edit.
- Inspection finds likely secrets and the requested edit would copy those secrets into a report, plan, final answer, or another file.
- The needed edit is broad enough that it should be done by Codex's memory consolidation instead of this skill.
