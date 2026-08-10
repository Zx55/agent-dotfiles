# Install Path

This skill installs Dayu through `uv tool install`, not through system Python, conda, or a project virtualenv.

## Default path

1. Ensure `uv` exists.
2. Ensure a `uv`-managed Python `3.11+` exists.
3. Install the `dev` branch from the `Zx55/dayu-agent` fork.
4. Refresh and replace the tool with `uv tool install`.
5. Verify `dayu-cli` and `dayu-render`.
6. Run `dayu-cli init` for the target workspace.
7. Rerun the doctor to confirm the final state.

## Preferred commands

Use the bundled script for real work:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace
```

Useful variants:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --overwrite-init
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --reset-init
./scripts/dayu_install_or_update.sh --workspace /path/to/dayu-workspace --skip-init
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --ref <branch-or-commit> --skip-init
```

Without `--ref`, the script installs:

```text
dayu-agent @ git+https://github.com/Zx55/dayu-agent.git@dev
```

The `--refresh-package dayu-agent` option forces uv to refresh the mutable branch instead of reusing stale Git metadata. Use `--ref` to pin a fork branch, tag, or full commit when reproducibility matters.

Init flags are intentionally explicit:

- `--skip-init` leaves an existing workspace config untouched
- `--overwrite-init` passes `dayu-cli init --overwrite`
- `--reset-init` passes `dayu-cli init --reset`

Use reset only when the reviewed fork change requires it or the user explicitly wants to rebuild generated init directories.

Manual fallback for the default fork branch:

```bash
uv tool install --managed-python --python 3.11 --force \
  --refresh-package dayu-agent \
  "dayu-agent @ git+https://github.com/Zx55/dayu-agent.git@dev"
```

## What the installer script assumes

- `curl` is available if the official uv installer is needed.
- GitHub access is available for cloning `Zx55/dayu-agent` through uv.
- `uv` may be missing and should be installed with Astral's standalone installer.
- Python should come from `uv`, not from conda or a system interpreter.
- `dayu-cli init` is interactive and should be run in a TTY.

## Verifying the result

Healthy setup means:

- `uv` runs
- `uv python find --managed-python 3.11` succeeds
- `dayu-cli --help` succeeds
- `dayu-cli prompt --help` exposes `--output`
- `dayu-render` is present and returns usage text when invoked without arguments
- the target workspace has a populated `config/` directory after `init`

## Optional render dependencies

Dayu's README says PDF rendering additionally needs:

- `pandoc`
- Google Chrome

Treat these as warnings unless the user explicitly needs PDF rendering during setup.

## Revision policy

The fork's `dev` branch is the default source because the Dayu skill depends on its Markdown output workflow:

- do not auto-check for updates before every Dayu usage
- update only when the user asks, or when install or repair work already requires it
- if the user wants a reproducible install, pass `--ref <full-commit-sha>`
- record the installed commit in the final response when practical
- keep revision-specific notes in [update.md](update.md), not in this install path reference
