# Master Bootstrap

This profile is for the primary personal Mac environment. It owns the full Codex runtime setup, development tooling, portable config links, and optional large applications.

Use `ha-host` instead for a dedicated Home Assistant host. The HA host profile is intentionally lighter and links its own profile-managed Codex config and skills.

Common commands:

```sh
./master/bootstrap/bootstrap.sh install
./master/bootstrap/bootstrap.sh install --with-large-app
./master/bootstrap/bootstrap.sh links --agent codex
./master/bootstrap/bootstrap.sh verify --agent codex
./master/bootstrap/bootstrap.sh all --agent codex
```

Package manifests:

- `packages/Brewfile.core`: core Homebrew packages.
- `packages/Brewfile.large-app`: large GUI apps installed only with `--with-large-app`.
- `packages/agent-python.txt`: shared agent Python packages for `~/.local/share/agent-dotfiles/python`.
- `packages/uv-tools.txt`: uv-managed CLI tools.
- `packages/npm-global.txt`: global npm tools.
- `packages/mas-apps.txt`: Mac App Store apps.
- `packages/local-tools.txt`: repo-local tools checked by verify.
- `packages/ml-models.tsv`: optional model warmup list.

Codex config policy:

- master keeps the portable Codex config snapshot current.
- `links` symlinks shared global instructions from `shared/AGENTS.md` into `~/.codex/AGENTS.md`.
- `links` symlinks repo-managed config into `~/.codex`.
- `links` installs only the skill symlinks present under `master/agent/skills/`, resolving each one to its canonical source under `shared/skills/`.
- master is the profile where hooks and full local workflow integrations belong.
- local/private runtime state such as memories stays outside this repo unless explicitly decided otherwise.

Typical first-run sequence:

```sh
./master/bootstrap/bootstrap.sh install
./master/bootstrap/bootstrap.sh links --agent codex
./master/bootstrap/bootstrap.sh verify --agent codex
```

Run `all` only when install, links, and verify should be performed together.
