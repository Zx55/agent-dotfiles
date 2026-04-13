# MemPalace Usage

This reference covers the MemPalace commands and usage patterns that matter for this skill.

## Core Commands

For the current workflow, MemPalace is used for:

- checking whether the backend is available
- searching long-term memory
- optionally getting a compact wake-up context

### Status

Use to confirm the backend is installed and the palace is accessible.

```bash
~/.mempalace/.venv/bin/mempalace status
```

### Search

Use when the task is clearly about prior sessions, earlier decisions, or user preferences.

```bash
~/.mempalace/.venv/bin/mempalace search "query"
```

### Wake-up

Use when you want a compact long-term context refresh before continuing a thread of work.

```bash
~/.mempalace/.venv/bin/mempalace wake-up
```

## Usage Rules

1. Prefer `search` for cross-session recall.
2. Prefer `wake-up` when continuing a thread and a compact context refresh is enough.
3. Use `status` for backend diagnostics.

## What Not to Do

- Do not treat MemPalace as the source of truth for time-sensitive facts.
- Do not assume backend-specific commands are necessary unless the task actually requires them.
