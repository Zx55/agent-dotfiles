# Agent Dotfiles

This repository is the source of truth for personal agent configuration and the portable parts of macOS agent environments. It is organized by machine profile instead of one global bootstrap.

## Layout

```text
agent-dotfiles/
  master/
    bootstrap/
    agent/
      codex/
      skills/
    dotfiles/
    tools/

  ha-host/
    bootstrap/
    agent/
      codex/
      skills/
    dotfiles/
    tools/

  shared/
    AGENTS.md
    hooks/
    skills/

  docs/
```

`master/` is the daily personal Mac profile. It owns the full Codex setup, desktop automation skills, research and finance skills, Zotero tooling, and daily dotfiles.

`ha-host/` is the dedicated Home Assistant host profile. It owns HAOS/MiAir operational skills, the HA host orchestrator, MiAir wrapper, PS5 HA bridge, and a smaller Codex runtime.

`shared/AGENTS.md` contains agent-neutral global instructions. Profile link scripts symlink it into the active agent runtime config directory.

`shared/hooks/` contains hook implementation scripts only. Each profile keeps its own `agent/codex/hooks.json`, and that file decides which profile receives synced config and automation snapshots.

`shared/skills/` contains the canonical skill sources. Profile directories under `*/agent/skills/` contain only symlinks to the shared skill directories, so profile skill selection is managed by filesystem links instead of bootstrap script lists.

## Bootstrap

Run the profile entrypoint directly. There is no root-level profile dispatcher.

```sh
./master/bootstrap/bootstrap.sh all --agent codex
./master/bootstrap/bootstrap.sh install
./master/bootstrap/bootstrap.sh links --agent codex
./master/bootstrap/bootstrap.sh verify --agent codex

./ha-host/bootstrap/bootstrap.sh audit
./ha-host/bootstrap/bootstrap.sh install
./ha-host/bootstrap/bootstrap.sh links --agent codex
./ha-host/bootstrap/bootstrap.sh verify --agent codex
```

Both profiles use symlinks for shared global instructions, profile-managed Codex files, skills, and dotfiles. Existing targets are backed up under `~/.dotfiles-backup/<timestamp>/` before replacement.

## Profiles

Master includes the broad daily skill set and tools:

- symlinks under `master/agent/skills/` for the current broad daily skill set
- `master/tools/mcp-launcher`
- `master/tools/zotero-mcp-wrapper`
- `master/tools/zotero-add-local-file-plugin`

HA host includes the operational host skill set and tools:

- symlinks under `ha-host/agent/skills/iot/` only
- `ha-host/tools/orchestrator`
- `ha-host/tools/miair-macos-wrapper`
- `ha-host/tools/ps5-ha-bridge`

## Secrets

Committed secret files must contain templates only.

- `master/dotfiles/secrets/secret.example` and `ha-host/dotfiles/secrets/secret.example` are committed.
- `master/dotfiles/secrets/secret.local` and `ha-host/dotfiles/secrets/secret.local` are ignored.
- `~/.secret` should be a symlink to the active profile's `secret.local`.

Codex config blocks `~/.secret` and each profile's `secret.local` from `secret_safe` filesystem access.

## Migration Notes

The profile split design and migration checklist live in `docs/profile-split-migration.md`. Historical old-layout paths in that document describe migration sources and validation checks, not active entrypoints.
