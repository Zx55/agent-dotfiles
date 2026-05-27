#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
BACKUP_ROOT="${HOME}/.dotfiles-backup"
BACKUP_DIR=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: bootstrap/bootstrap.sh --profile ha_host links [options]

Options:
  --dry-run             Print planned copy operations without changing files.
  -h, --help            Show this help.

The HA host profile is copy-only. It does not install Codex hooks, and it does
not sync host runtime config back to this repository.
EOF
}

log() {
  printf '[ha_host:links] %s\n' "$*"
}

die() {
  printf '[ha_host:links] error: %s\n' "$*" >&2
  exit 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)
        DRY_RUN=1
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown argument: $1"
        ;;
    esac
    shift
  done
}

init_backup_dir() {
  if [[ -z "$BACKUP_DIR" ]]; then
    BACKUP_DIR="$BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)"
    if [[ "$DRY_RUN" -eq 0 ]]; then
      mkdir -p "$BACKUP_DIR"
    fi
  fi
}

backup_target() {
  local target="$1"
  [[ -e "$target" || -L "$target" ]] || return 0

  init_backup_dir
  local relative="${target#$HOME/}"
  local backup_path="$BACKUP_DIR/$relative"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would back up $target to $backup_path"
    return 0
  fi

  mkdir -p "$(dirname "$backup_path")"
  log "Backing up $target to $backup_path"
  mv "$target" "$backup_path"
}

same_regular_file() {
  local source="$1"
  local target="$2"
  [[ -f "$target" && ! -L "$target" ]] || return 1
  cmp -s "$source" "$target"
}

copy_file() {
  local source="$1"
  local target="$2"
  [[ -f "$source" ]] || die "source missing: $source"

  if same_regular_file "$source" "$target"; then
    log "Already copied: $target"
    return 0
  fi

  backup_target "$target"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would copy $source -> $target"
    return 0
  fi

  mkdir -p "$(dirname "$target")"
  log "Copying $source -> $target"
  cp "$source" "$target"
}

same_directory() {
  local source="$1"
  local target="$2"
  [[ -d "$target" && ! -L "$target" ]] || return 1
  diff -qr "$source" "$target" >/dev/null 2>&1
}

copy_directory() {
  local source="$1"
  local target="$2"
  [[ -d "$source" ]] || die "source missing: $source"

  if same_directory "$source" "$target"; then
    log "Already copied: $target"
    return 0
  fi

  backup_target "$target"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would copy directory $source -> $target"
    return 0
  fi

  mkdir -p "$(dirname "$target")"
  log "Copying directory $source -> $target"
  cp -R "$source" "$target"
}

ensure_absent() {
  local target="$1"
  [[ -e "$target" || -L "$target" ]] || {
    log "Already absent: $target"
    return 0
  }

  backup_target "$target"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would disable by moving out of place: $target"
    return 0
  fi

  log "Disabled by moving out of place: $target"
}

copy_codex_runtime() {
  mkdir -p "$HOME/.codex"
  copy_file "$REPO_ROOT/agents/AGENTS.md" "$HOME/.codex/AGENTS.md"
  copy_file "$REPO_ROOT/agents/codex/config.toml" "$HOME/.codex/config.toml"
  copy_directory "$REPO_ROOT/agents/codex/rules" "$HOME/.codex/rules"
  ensure_absent "$HOME/.codex/hooks.json"

  mkdir -p "$HOME/.codex/skills"
  local skill_dir
  for skill_dir in "$REPO_ROOT"/agents/skills/*; do
    [[ -d "$skill_dir" ]] || continue
    copy_directory "$skill_dir" "$HOME/.codex/skills/$(basename "$skill_dir")"
  done
}

main() {
  parse_args "$@"
  copy_codex_runtime

  if [[ -n "$BACKUP_DIR" ]]; then
    if [[ "$DRY_RUN" -eq 1 ]]; then
      log "Would write backups under $BACKUP_DIR"
    else
      log "Backups written to $BACKUP_DIR"
    fi
  fi
}

main "$@"
