---
name: dayu-installation
description: Install, update, verify, and initialize the Dayu CLI with uv-managed Python. Use when Dayu is missing, broken, needs an upgrade, or a workspace has not been initialized with `dayu-cli init`.
---

# Dayu Installation

Install and stabilize `dayu-cli` for local use through `uv`, then finish first-run setup with `dayu-cli init`.

Do not use this skill for normal research work such as `download`, `prompt`, `interactive`, `write`, or `dayu-render` usage after setup is already complete. Those belong in the separate `dayu` skill.

## When To Use

Use this skill when the user wants to:

- install `dayu-cli` for the first time
- update Dayu to a newer stable release
- verify whether a Dayu installation is healthy
- initialize a new Dayu workspace
- repair a broken `uv`, Python, PATH, or `dayu-cli` setup

## Scope

This skill owns setup only:

- install `uv` if needed
- require `uv`-managed Python `3.11+`
- install or replace the Dayu release wheel
- verify `dayu-cli` and `dayu-render`
- run `dayu-cli init` for a target workspace
- diagnose common setup failures

This skill does not own:

- ongoing Dayu usage
- WeChat setup
- financial analysis workflows
- recurring update checks

## Core Workflow

### 1. Confirm the setup target

Before changing anything, determine:

- whether the user wants install, update, verify, or repair
- which workspace path should be initialized
- whether `dayu-cli init` should overwrite an existing workspace config

If the workspace path is not specified, default to `~/.dayu/workspace`.

### 2. Run the doctor first

Run [scripts/dayu_doctor.sh](scripts/dayu_doctor.sh) before editing the machine state. This gives a quick read on:

- whether `uv` is installed
- whether a `uv`-managed Python `3.11+` exists
- whether Dayu is already installed
- whether `dayu-cli` and `dayu-render` can run
- whether the target workspace already looks initialized

If the doctor shows setup is already healthy and the user only asked for verification, stop there and summarize the result.

### 3. Install or update Dayu through `uv`

Use [scripts/dayu_install_or_update.sh](scripts/dayu_install_or_update.sh) for the actual setup path.

For first install or repair, read [references/install.md](references/install.md). For update requests, read [references/update.md](references/update.md) before and after installation; that reference owns release-note review, version-specific cleanup, CLI surface checks, and deciding whether this skill or the sibling `dayu` skill needs documentation changes.

Default behavior:

- install `uv` with the official standalone installer if it is missing
- install `uv`-managed Python `3.11`
- resolve the requested stable Dayu GitHub release wheel
- install Dayu with `uv tool install`
- verify the installed executables
- run `dayu-cli init` unless `--skip-init` is explicitly requested

Use `tty=true` when running the installer if `dayu-cli init` will run, because the init step is interactive.

### 4. Treat `init` as part of setup

For this skill, `dayu-cli init` is part of installation completeness. A Dayu install is not fully ready until the target workspace has usable config under `workspace/config` or the chosen `--base` directory.

Because `init` is interactive, do not try to fake provider selection or API key input. Run the command in a TTY and let the user complete the prompts.

If the workspace already has config and the user wants to rebuild it, rerun init with overwrite enabled.

For provider/config refreshes after an update, follow [references/update.md](references/update.md). Only use overwrite when the user wants that refresh.

### 5. Verify the final state

After installation or update, rerun [scripts/dayu_doctor.sh](scripts/dayu_doctor.sh). For update-specific verification, including CLI help checks and stale documentation search, follow [references/update.md](references/update.md).

Warn, but do not fail setup, if optional render dependencies are missing. Those are only needed for some render flows.

## Network And Proxy

These steps depend on GitHub and Astral downloads. If a network command hangs, times out, or fails because the host cannot reach the internet:

- check the machine's network settings first
- if this environment already has a known proxy workflow, use it
- if proxy requirements are unclear, ask the user before guessing
- once connectivity is restored, retry the failed command

## References

- Read [references/install.md](references/install.md) for the standard install path.
- Read [references/update.md](references/update.md) when Dayu is being upgraded or when the CLI may have changed.
- Read [references/troubleshooting.md](references/troubleshooting.md) when setup fails or the doctor reports a broken state.
- Read [references/openai_compatible_provider.md](references/openai_compatible_provider.md) when the user's API key or endpoint is OpenAI-compatible but not OpenAI itself.

## Output Expectations

When using this skill, produce:

- the setup goal and workspace target
- the doctor result before changes
- the exact install or update command used
- whether `init` was run and against which workspace
- for updates, the release/CLI audit result and any skill files changed
- the final verification result
- any remaining manual follow-up, such as adding the `uv` tool bin directory to `PATH`
