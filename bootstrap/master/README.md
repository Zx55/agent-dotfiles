# Master Bootstrap

This profile is for the primary personal Mac environment. It owns the full Codex runtime setup, development tooling, portable config links, and optional large applications.

Use `ha_host` instead for a dedicated Home Assistant host. The HA host profile is intentionally lighter and copies Codex config without hooks or symlinks.

Common commands:

```sh
./bootstrap/bootstrap.sh --profile master install
./bootstrap/bootstrap.sh --profile master install --with-large-app
./bootstrap/bootstrap.sh --profile master links --agent codex
./bootstrap/bootstrap.sh --profile master verify --agent codex
./bootstrap/bootstrap.sh --profile master all --agent codex
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
- `links` may symlink or copy repo-managed config into `~/.codex`.
- master is the profile where hooks and full local workflow integrations belong.
- local/private runtime state such as memories stays outside this repo unless explicitly decided otherwise.

Typical first-run sequence:

```sh
./bootstrap/bootstrap.sh --profile master install
./bootstrap/bootstrap.sh --profile master links --agent codex
./bootstrap/bootstrap.sh --profile master verify --agent codex
```

Run `all` only when install, links, and verify should be performed together.
