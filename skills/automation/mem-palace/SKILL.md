---
name: mem-palace
description: Use when Codex needs cross-session continuity through long-term memory, especially for recalling prior decisions, user preferences, unfinished work, or earlier discussion context. This skill guides when to search memory and how to treat memory as a retrieval layer rather than a source of truth.
---

# Mem Palace

Use this skill when the task depends on history that may live outside the current session. Its role is to help Codex:

- recognize when long-term memory is relevant
- prefer memory for cross-session continuity
- treat memory results as historical context rather than authoritative truth

It is recommended to use `MemPalace` as the memory backend for storage and retrieval. This skill involves reading or searching memories. Memory writing is typically conducted as part of an offline or scheduled workflow.

## When to Use

Use this skill when the user asks about:

- prior decisions
- earlier discussions
- unfinished work from previous sessions
- stable user preferences
- project context established in earlier Codex runs
- historical rationale such as "why did we do this before?"

This skill is also useful when:

- the current answer would benefit from searching a memory backend
- you need to continue a longer-running thread of work across sessions

## When Not to Use

Do not use this skill by default for:

- questions answerable directly from the current repository
- live system state
- time-sensitive facts that should be re-verified
- one-off code questions with no historical dependency

Do not treat memory as a replacement for:

- reading the current workspace
- running commands
- checking fresh external facts

## Core Rules

1. Use memory as a retrieval layer for continuity, not as a truth oracle.
2. Prefer the current repository for current-state questions.
3. Prefer memory first for cross-session questions.
4. If memory may help but is uncertain, try it once rather than assuming.
5. If memory results conflict with the current repo or fresh evidence, trust the current evidence and explain the conflict briefly.

## Relationship to MemPalace

MemPalace is the current recommended long-term memory backend for this skill.

In the current setup:

- MemPalace indexes and retrieves those artifacts
- Codex uses this skill to decide when memory should be consulted
- a separate background summarization pipeline keeps the indexed content refreshed

Keep this distinction clear:

- MemPalace is the memory backend
- this skill is the workflow layer

For the MemPalace installation and usage, read:

- [references/mempalace-installation.md](references/mempalace-installation.md)
- [references/mempalace-usage.md](references/mempalace-usage.md)

## Core Workflow

1. Decide whether the current task is historical or current-state.
   If it is primarily about prior sessions, prior decisions, or user preferences, memory is likely relevant.

2. Prefer an existing memory search path first.
   If a memory backend is already available, use it to search for the relevant context.

3. Answer with source-aware caution.
   Use memory to recover context, but distinguish between remembered history and currently verified facts.

4. Fall back gracefully.
   If memory is unavailable or unhelpful, continue using the repository, local files, or fresh research rather than blocking on memory.

## Preferred Decision Heuristic

Use this quick heuristic:

- "What is the bug in this file?" -> inspect the repo first
- "What did we decide yesterday?" -> search memory first
- "What is my preference for this workflow?" -> search memory first
- "What is the latest API behavior?" -> verify current docs or current code first
- "Continue the thing we were doing before" -> search memory, then inspect the repo

## Output Expectations

When using this skill, produce:

- a clear choice about whether memory is relevant
- a memory-first workflow only when history actually matters
- explicit distinction between recalled context and fresh verification

Keep the workflow lightweight.

Do not turn interactive memory retrieval into a pipeline-management task when a direct search is enough.
