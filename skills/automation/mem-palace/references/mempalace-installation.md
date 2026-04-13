# MemPalace Installation

This reference describes the current recommended way to install MemPalace locally and verify that the CLI works.

Use it when:

- MemPalace is not installed yet
- the local installation looks broken or inconsistent
- a task depends on knowing where the MemPalace runtime lives

## Recommended Layout

Use `~/.mempalace` as the stable home for MemPalace runtime and data.

Recommended layout:

- `~/.mempalace/.venv`
- `~/.mempalace/config.json`
- `~/.mempalace/palace`
- `~/.mempalace/wal`

Meaning:

- `~/.mempalace/.venv`
  Dedicated Python environment for the MemPalace CLI and backend runtime
- `~/.mempalace/config.json`
  MemPalace configuration
- `~/.mempalace/palace`
  Main memory store
- `~/.mempalace/wal`
  MemPalace write-ahead or internal log files

## Installation Approach

Prefer `uv` for installation and environment management.

Recommended pattern:

1. create a dedicated environment under `~/.mempalace/.venv`
2. install MemPalace into that environment from PyPI
3. use the environment's `mempalace` executable directly instead of relying on a global shell path

### Recommended Install Commands

Create the runtime directory and environment:

```bash
mkdir -p ~/.mempalace
uv venv ~/.mempalace/.venv
```

Install MemPalace:

```bash
uv pip install --python ~/.mempalace/.venv/bin/python mempalace
```

## Command Convention

Prefer the dedicated executable path:

```bash
~/.mempalace/.venv/bin/mempalace
```

Do not assume plain `mempalace` is on `PATH`.

## Quick Verification

After installation, verify that the CLI is reachable and the local palace can be opened.

Recommended checks:

1. confirm the executable exists
2. run a lightweight status command
3. run a simple search command

Example:

```bash
~/.mempalace/.venv/bin/mempalace status
~/.mempalace/.venv/bin/mempalace search "test"
```

The exact search results are not important for installation verification.

What matters is:

- the command starts successfully
- the runtime can access the local MemPalace directory
- the CLI fails, if at all, in a normal application-level way rather than "command not found" or broken-environment errors

## Operational Preference

When documenting or scripting backend-specific behavior, assume:

- the memory backend is currently MemPalace
- the installation root is `~/.mempalace`
- the executable is `~/.mempalace/.venv/bin/mempalace`
