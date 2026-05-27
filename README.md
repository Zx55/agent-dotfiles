# Agent Dotfiles

This repository is the source of truth for personal agent configuration and the
portable parts of a macOS development environment.

The target is a practical migration baseline, not a byte-for-byte clone of the
current machine. A new Mac should become 70-80% ready through repeatable package
installation, symlinked configuration, and explicit manual steps for secrets,
app logins, and machine-local state.

## Layout

```text
agent-dotfiles/
  agents/
    AGENTS.md
    codex/
      automations/
      config.toml
      hooks.json
      hooks/
      rules/              # optional, when present
    skills/
    tools/

  dotfiles/
    git/
      gitconfig
      gitignore_global
    secrets/
      secret.example
      secret.local        # ignored
    zsh/
      zprofile
      zshrc

  bootstrap/
    bootstrap.sh
    master/
      packages/
        Brewfile.core
        Brewfile.large-app
        agent-python.txt
        local-tools.txt
        mas-apps.txt
        npm-global.txt
        uv-tools.txt
      scripts/
        all.sh
        install.sh
        links.sh
        verify.sh
        warm_ml_models.sh
    ha_host/
      packages/
        Brewfile.core
        agent-python.txt
        uv-tools.txt
      scripts/
        audit.sh
        install.sh
        links.sh
        verify.sh
  .githooks/
    pre-commit
```

`agents/AGENTS.md` is the shared instruction source for agent tools. Codex links
it to `~/.codex/AGENTS.md`. Other agents can link the same source to whatever
filename they require later.

`agents/codex/config.toml` is the portable Codex config snapshot. Bootstrap
copies it to `~/.codex/config.toml`; it is not symlinked because Codex writes
machine-local runtime state such as hook trust hashes into the live config.
Codex-owned portable paths use `~/...`. MCP server paths go through
`mcp-launcher` instead of `[mcp_servers.<name>.env]`, because Codex passes MCP
env values literally.

`agents/codex/hooks.json` registers a small Codex lifecycle hook that runs on
session start, resume, clear, user prompt submit, and stop. The hook calls
`agents/codex/hooks/sync_config.py` to sync the live
`~/.codex/config.toml` back to `agents/codex/config.toml`, remove local-only
hook trust state, and rewrite portable machine-local home prefixes such as
`/Users/<user>/...` back to `~/...`. A separate hook calls
`agents/codex/hooks/sync_automations.py` to sync every
`~/.codex/automations/<id>/automation.toml` file back to a portable snapshot
under `agents/codex/automations/`, and to remove portable snapshots whose live
automation no longer exists. The automation hook intentionally ignores
runtime files such as `memory.md` and `.run-jitter-salt`.

`agents/skills/` and `agents/tools/` are agent-only assets. General purpose tools
should live elsewhere if they appear later.

`agents/codex/automations/` stores portable Codex App automation snapshots when
there are active automations to manage. Bootstrap copies each `automation.toml`
to `~/.codex/automations/<id>/` and expands `~/...` to the local home path
during install, because the App currently reads local `automation.toml` files
but the format is not documented as a stable public API. During link and after
install, the Codex automation hook treats each live
`~/.codex/automations/<id>/automation.toml` as managed state, snapshots it into
the repository, and removes snapshots for live automations that were deleted.
Runtime files such as automation `memory.md` and `.run-jitter-salt` are
intentionally not migrated.

`~/.codex/memories` is not migrated or linked by this repository. Codex memories
are local generated recall state that may be rewritten by the Codex memory
pipeline. Stable cross-device instructions belong in `agents/AGENTS.md`, skills,
or checked-in docs, not in generated memory files.

## Bootstrap

The bootstrap layer is shell-based because it must run before Python, Node, or uv
can be assumed to exist.

Common commands:

```sh
./bootstrap/bootstrap.sh --profile master all --agent codex
./bootstrap/bootstrap.sh --profile master install
./bootstrap/bootstrap.sh --profile master links --agent codex
./bootstrap/bootstrap.sh --profile master verify --agent codex
./bootstrap/bootstrap.sh --profile master install --with-large-app
./bootstrap/bootstrap.sh --profile master install --skip-agent-python
./bootstrap/bootstrap.sh --profile ha_host audit
./bootstrap/bootstrap.sh --profile ha_host verify
```

`master` is the default profile and only `codex` is supported for now.

`bootstrap/bootstrap.sh` is a thin profile dispatcher. It only parses
`--profile <name>` and the requested step, then forwards all remaining arguments
to `bootstrap/<profile>/scripts/<step>.sh`.

`bootstrap/master/scripts/all.sh` runs the master install, links, and verify
steps in order. It owns the combined master-profile options that need to be
split across those steps.

`bootstrap/master/scripts/install.sh` installs packages and local tools. It
installs Homebrew if needed, then runs `Brewfile.core`. With
`--with-large-app`, it starts `Brewfile.large-app` in the background after core
packages finish. Large app logs go to `~/.dotfiles-bootstrap/logs/`.

`bootstrap/master/scripts/links.sh` creates symlinks from this repository into
the home directory, except for Codex `config.toml`, which is copied as a local
runtime file, and Codex App automation snapshots, which are copied after
expanding portable home paths. Existing targets are moved to
`~/.dotfiles-backup/<timestamp>/` before replacement.

`bootstrap/master/scripts/verify.sh` checks package files, local tool sources,
Codex config loading, installed runtime tools, and expected symlinks.

`bootstrap/ha_host` is a conservative Home Assistant host profile for macOS. Its
install step ensures Homebrew exists and installs the minimal host package
manifest for remote Codex access, Tailscale access, UTM virtualization, and a
small uv-managed agent Python environment. Network exposure, sleep policy, VM
creation, and Home Assistant OS setup remain explicit follow-up decisions.
Its links step is copy-only and intentionally does not install Codex hooks, so
the HA host receives config from this repository without syncing runtime config
back.

The repository uses `.githooks/pre-commit` through `git config core.hooksPath
.githooks`. Before each commit, the hook syncs `~/.codex/config.toml` back to
`agents/codex/config.toml` only when `~/.codex/hooks.json` points to this repo,
syncs every `~/.codex/automations/*/automation.toml` file back to
`agents/codex/automations/`, removes snapshots for deleted live automations,
automatically stages the portable snapshots, and verifies that the portable
Codex config loads.

## Package Manifests

`Brewfile.core` contains default Homebrew formulae and casks. It includes core
CLI tools, Codex, Zotero, Chrome, iTerm2, Raycast, zsh completion support, and
other daily utilities.

`Brewfile.large-app` contains slower or larger GUI apps. It is opt-in through
`--with-large-app`.

`uv-tools.txt` contains uv-installed tools:

```text
dayu-agent
huggingface-hub
ipython
./agents/tools/mcp-launcher
ruff
whisperx
zotero-mcp-server
```

`npm-global.txt` is intentionally empty for now.

`agent-python.txt` contains packages for the shared agent Python environment at
`~/.local/share/agent-dotfiles/python`. Bootstrap creates that environment with
uv-managed Python 3.12 and installs the listed packages with `uv pip install`.
Project-specific packages should stay in project-local environments such as
`.venv`.

`local-tools.txt` installs repo-managed local binaries such as
`zotero-mcp-wrapper`.

`mas-apps.txt` lists Mac App Store app IDs. These require `mas` and an App Store
account already signed in on the machine.

## Dotfiles

The zsh files are split by shell responsibility:

- `dotfiles/zsh/zprofile` sets Homebrew shell environment and OrbStack shell
  integration.
- `dotfiles/zsh/zshrc` configures oh-my-zsh, aliases, uv completion, secret
  loading, optional TeX path, optional `~/Documents/scripts` aliases, and cargo
  only when present.

The zsh config intentionally does not prepend `node@18`. Homebrew's regular
`node` formula is reached through `/opt/homebrew/bin` from `brew shellenv`.

The git config uses GitHub CLI as the credential helper. It does not contain
tokens. GitHub authentication still needs `gh auth login` on a new machine.

## Secrets

Committed secret files must contain templates only.

- `dotfiles/secrets/secret.example` is committed.
- `dotfiles/secrets/secret.local` is ignored.
- `~/.secret` should be a symlink to `dotfiles/secrets/secret.local`.

Codex config blocks both secret paths from `secret_safe` filesystem access:

```toml
"~/.secret" = "none"
"~/Documents/codex-workspace/agent-dotfiles/dotfiles/secrets/secret.local" = "none"
```

Bootstrap may create `secret.local` from `secret.example`, but real values must
be filled manually.

## Migration Scope

Migrated:

- Agent instructions
- Codex portable config
- Custom skills
- Agent helper tools
- Codex App automation definitions
- Shell and git dotfiles
- Homebrew, uv, npm, local binary, and Mac App Store package manifests

Not migrated:

- API keys and tokens
- Agent auth files
- Runtime logs and SQLite state
- Codex generated memories under `~/.codex/memories`
- Codex App automation runtime memory and jitter state
- Browser, app, or plugin cache
- Generated images and temporary artifacts
- App login sessions
- Large machine-specific histories

## Current Status

Already linked on the current machine:

- `~/.codex/AGENTS.md`
- `~/.codex/config.toml` as a regular local file copied from the portable snapshot
- `~/.codex/hooks.json`
- `~/.codex/rules`
- `~/.zshrc`
- `~/.zprofile`
- `~/.gitconfig`
- `~/.gitignore_global`
- `~/.secret`
- most `~/.codex/skills/*` categories

Remaining work:

- Install or confirm Mac App Store apps through `mas` when setting up a new Mac.
