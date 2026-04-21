# Install Path

This skill installs Dayu through `uv tool install`, not through system Python, conda, or a project virtualenv.

## Default path

1. Ensure `uv` exists.
2. Ensure a `uv`-managed Python `3.11+` exists.
3. Resolve the latest stable Dayu wheel from GitHub Releases.
4. Install or replace the tool with `uv tool install`.
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
./scripts/dayu_install_or_update.sh --workspace /path/to/dayu-workspace --skip-init
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --version <tag>
```

The script resolves the latest wheel dynamically when `--version latest` is used. If GitHub REST API release lookup is blocked or rate-limited, it falls back to `gh release view`; for explicit release tags it can also verify the conventional wheel URL directly.

Manual fallback for a known release tag:

```bash
tag=vX.Y.Z
version="${tag#v}"
uv tool install --managed-python --python 3.11 --force \
  "dayu-agent @ https://github.com/noho/dayu-agent/releases/download/${tag}/dayu_agent-${version}-py3-none-any.whl"
```

## What the installer script assumes

- `curl` is available for network fetches.
- `gh` is optional but useful when GitHub REST API release lookup returns 403.
- `uv` may be missing and should be installed with Astral's standalone installer.
- Python should come from `uv`, not from conda or a system interpreter.
- `dayu-cli init` is interactive and should be run in a TTY.

## Verifying the result

Healthy setup means:

- `uv` runs
- `uv python find --managed-python 3.11` succeeds
- `dayu-cli --help` succeeds
- `dayu-render` is present and returns usage text when invoked without arguments
- the target workspace has a populated `config/` directory after `init`

## Optional render dependencies

Dayu's README says PDF rendering additionally needs:

- `pandoc`
- Google Chrome

Treat these as warnings unless the user explicitly needs PDF rendering during setup.

## Version policy

Prefer stability over aggressive upgrades:

- do not auto-check for updates before every Dayu usage
- update only when the user asks, or when install or repair work already requires it
- if the user wants a pinned version, pass `--version <tag>`
- keep version-specific notes in [update.md](update.md), not in this install path reference
