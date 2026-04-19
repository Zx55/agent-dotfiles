# Troubleshooting

## Network fetches fail or hang

Dayu setup needs access to:

- `github.com`
- `api.github.com`
- `astral.sh`

If `curl` hangs, times out, or fails with connectivity errors:

- check whether the machine needs a proxy to reach GitHub or Astral
- if the environment already has a known proxy method, use it
- if the correct proxy method is not known, ask the user instead of guessing
- retry the failed command after connectivity is fixed

If GitHub API access is rate-limited or blocked, rerun the installer with an explicit release tag:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --version v0.1.1
```

## `uv` installed but not on `PATH`

The standalone installer usually places `uv` in `~/.local/bin`.

Check:

```bash
~/.local/bin/uv --version
```

If that works but `uv` is still not found, either:

- add `~/.local/bin` to `PATH`
- use `uv tool update-shell`

The doctor and installer scripts report the detected tool bin directory when relevant.

## No `uv`-managed Python `3.11+`

The setup path requires `uv`-managed Python. Install it with:

```bash
uv python install --managed-python 3.11
```

Then verify:

```bash
uv python find --managed-python 3.11
```

## Dayu installed but `dayu-cli` is not found

Check the `uv` tool bin directory:

```bash
uv tool dir --bin
```

If the directory contains `dayu-cli` but it is not on `PATH`, add that directory to `PATH` or use the absolute executable path.

## `dayu-cli init` cannot run interactively

`init` needs a TTY because it prompts for:

- model provider
- API keys
- optional web provider keys

If the command was launched without a TTY, rerun it in an interactive terminal or with a TTY-capable tool call.

## Workspace config already exists

If the workspace was initialized before and needs to be rebuilt, rerun init with overwrite enabled:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --overwrite-init
```

## Render checks fail

`dayu-render --help` should work once the tool is installed. Actual PDF output may still need:

- `pandoc`
- Google Chrome

Missing render dependencies should be treated as a follow-up task, not a core install failure, unless the user explicitly asked for PDF rendering during setup.
