# Automation

Use this skill in Codex Automations only in `plan` mode.

Recommended weekly prompt:

```text
Use $codex-memory-maintenance plan to review Codex memories.

Do not apply changes. Inspect ~/.codex/memories, verify proposed semantic edits against relevant rollout summaries, write a maintenance plan only if there are actionable issues, and avoid copying any secret values into the report or response.
```

Expected behavior:

- Automation opens its own run.
- The run writes audit and plan artifacts under `~/.codex-memory-maintenance`.
- The plan names the rollout evidence used for semantic edits, or says that no direct evidence was found.
- The run does not modify `~/.codex/memories`.
- If the plan needs action, the user can start a normal Codex session and explicitly invoke `$codex-memory-maintenance apply`.
