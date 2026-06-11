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
./master/bootstrap/bootstrap.sh links --agent cursor
./master/bootstrap/bootstrap.sh verify --agent cursor
```

Package manifests:

- `packages/Brewfile.core`: core Homebrew packages.
- `packages/Brewfile.large-app`: large GUI apps installed only with `--with-large-app`.
- `packages/agent-python.txt`: shared agent Python packages for `~/.local/share/agent-dotfiles/python`.
- `packages/uv-tools.txt`: uv-managed CLI tools.
- `packages/npm-global.txt`: global npm tools. Lines default to `npm install -g <package>`; append `| npx-install` for packages whose official setup is `npx <package> install`.
- `packages/mas-apps.txt`: Mac App Store apps.
- `packages/local-tools.txt`: repo-local tools checked by verify.
- `packages/ml-models.tsv`: optional model warmup list.

Codex config policy:

- master keeps the portable Codex config snapshot current.
- `links` symlinks Codex instructions from `master/agent/codex/AGENTS.md` into `~/.codex/AGENTS.md`.
- `links` symlinks repo-managed config into `~/.codex`.
- `links` installs only the skill symlinks present under `master/agent/skills/`, resolving each one to its canonical source under `shared/skills/`.
- master is the profile where hooks and full local workflow integrations belong.
- local/private runtime state such as memories stays outside this repo unless explicitly decided otherwise.

Cursor config policy:

- master keeps the portable Cursor settings snapshot current from the local app settings.
- `links` symlinks Cursor MCP config, user-level `hooks.json`, and `sandbox.json` from `master/agent/cursor/` into `~/.cursor`.
- Cursor `hooks.json` calls profile-local hook scripts under `master/agent/cursor/hooks/`; those scripts are symlinks to `shared/hooks/`.
- `master/agent/cursor/user-rules.md` is the repo-managed source for Cursor User Rules.
- Cursor User Rules are global app state; Cursor does not expose a stable documented file path for `links` to symlink or verify.
- After first install or any `user-rules.md` change, manually copy it into `Cursor Settings > Rules`.
- `links` does not symlink Cursor app `settings.json`; hooks sync the runtime settings back to `master/agent/cursor/settings.json`.
- `verify --agent cursor` checks that every `master/agent/skills/` skill is visible in at least one runtime skill directory such as `~/.codex/skills` or `~/.cursor/skills`.

Typical first-run sequence:

```sh
./master/bootstrap/bootstrap.sh install
./master/bootstrap/bootstrap.sh links --agent codex
./master/bootstrap/bootstrap.sh verify --agent codex
./master/bootstrap/bootstrap.sh links --agent cursor
./master/bootstrap/bootstrap.sh verify --agent cursor
```

Run `all` only when install, links, and verify should be performed together.
