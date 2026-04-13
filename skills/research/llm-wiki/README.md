# LLM Wiki Skill

This skill helps Codex build and maintain a personal markdown-first research wiki at `~/Documents/codex-workspace/llm-wiki`.

The skill is split into a few parts:

- `SKILL.md` is the main entry point for agent behavior.
- `references/` contains the operational rules and playbooks.
- `roadmaps/` contains longer-term design notes.
- `prompts/` contains integration snippets for system-level setup.

## Prompts

The `prompts/` directory is meant for integration points outside the skill itself.

- `prompts/schedule.md` is a prompt template for a scheduled maintenance task.
- `prompts/AGENTS.md` is a prompt snippet for the root `~/.codex/AGENTS.md`.

These files are not part of the core wiki contract. They exist to help you wire the skill into your broader Codex workflow.

## Recommended Setup

To make the skill useful in practice:

1. Add the root trigger guidance from `prompts/AGENTS.md` into `~/.codex/AGENTS.md`.
2. Set up a scheduled task that uses `prompts/schedule.md` as the maintenance prompt.
3. Keep the actual wiki at `~/Documents/codex-workspace/llm-wiki`.
4. Install `wiki_cli` from `~/Documents/codex-workspace/llm-wiki/tools/wiki-cli`.

## Core Flow

The intended workflow is:

1. The root `AGENTS.md` decides when to invoke the `llm-wiki` skill.
2. The skill uses `SKILL.md` and `references/` to decide how to ingest, query, lint, or maintain the wiki.
3. Scheduled maintenance uses `prompts/schedule.md`, which in turn points the agent back to this skill and its maintenance reference.
