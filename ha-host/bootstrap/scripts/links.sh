#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROFILE_ROOT="$(cd "$PROFILE_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
BACKUP_ROOT="${HOME}/.dotfiles-backup"
BACKUP_DIR=""
DRY_RUN=0
AGENT="codex"

usage() {
  cat <<'EOF'
Usage: ha-host/bootstrap/bootstrap.sh links [options]

Options:
  --agent <name>        Agent to link. Currently only "codex" is supported.
  --dry-run             Print planned link operations without changing files.
  -h, --help            Show this help.

The HA host profile installs profile-managed Codex config, hook config, shared
Agent Skills, and dotfiles as symlinks. Hook implementation scripts are exposed
through profile-local symlinks to shared/hooks.
EOF
}

log() {
  printf '[ha-host:links] %s\n' "$*"
}

warn() {
  printf '[ha-host:links] warning: %s\n' "$*" >&2
}

die() {
  printf '[ha-host:links] error: %s\n' "$*" >&2
  exit 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agent)
        [[ $# -ge 2 ]] || die "--agent requires a value"
        AGENT="$2"
        shift
        ;;
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

validate_args() {
  case "$AGENT" in
    codex)
      ;;
    *)
      die "unsupported agent: $AGENT"
      ;;
  esac
}

init_backup_dir() {
  if [[ -z "$BACKUP_DIR" ]]; then
    BACKUP_DIR="$BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)"
    [[ "$DRY_RUN" -eq 1 ]] || mkdir -p "$BACKUP_DIR"
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

same_symlink() {
  local source="$1"
  local target="$2"
  [[ -L "$target" ]] || return 1
  [[ "$(readlink "$target")" == "$source" ]]
}

link_path() {
  local source="$1"
  local target="$2"
  local required="${3:-required}"

  if [[ ! -e "$source" ]]; then
    if [[ "$required" == "required" ]]; then
      die "source missing: $source"
    fi
    warn "optional source missing, skipping: $source"
    return 0
  fi

  if same_symlink "$source" "$target"; then
    log "Already linked: $target"
    return 0
  fi

  backup_target "$target"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would link $target -> $source"
    return 0
  fi

  mkdir -p "$(dirname "$target")"
  log "Linking $target -> $source"
  ln -s "$source" "$target"
}

resolve_link_target() {
  local link_path="$1"
  local target
  target="$(readlink "$link_path")"
  case "$target" in
    /*)
      printf '%s\n' "$target"
      ;;
    *)
      local target_dir
      local target_base
      target_dir="$(dirname "$target")"
      target_base="$(basename "$target")"
      printf '%s/%s\n' "$(cd "$(dirname "$link_path")/$target_dir" && pwd)" "$target_base"
      ;;
  esac
}

ensure_skill_category_dir() {
  local category="$1"
  local target="$HOME/.agents/skills/$category"

  if [[ -L "$target" || ( -e "$target" && ! -d "$target" ) ]]; then
    die "runtime skill category path is occupied: $target"
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would ensure skill category directory: $target"
    return 0
  fi
  mkdir -p "$target"
}

link_skill_path() {
  local source="$1"
  local target="$2"

  if same_symlink "$source" "$target"; then
    log "Already linked: $target"
    return 0
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    die "runtime skill path is occupied: $target"
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would link $target -> $source"
    return 0
  fi

  log "Linking $target -> $source"
  ln -s "$source" "$target"
}

link_profile_skills() {
  local skills_root="$PROFILE_ROOT/agent/skills"
  [[ -d "$skills_root" ]] || return 0

  local category
  for category in "$skills_root"/*; do
    [[ -d "$category" ]] || continue
    ensure_skill_category_dir "$(basename "$category")"
  done

  local skill_link
  while IFS= read -r skill_link; do
    local relative
    local source
    relative="${skill_link#$skills_root/}"
    source="$(resolve_link_target "$skill_link")"
    [[ -d "$source" ]] || die "profile skill link target missing: $skill_link -> $source"
    [[ -f "$source/SKILL.md" ]] || die "profile skill is missing SKILL.md: $skill_link -> $source"
    link_skill_path "$source" "$HOME/.agents/skills/$relative"
  done < <(find "$skills_root" -mindepth 2 -maxdepth 2 -type l | sort)
}

ensure_secret_local() {
  local example="$PROFILE_ROOT/dotfiles/secrets/secret.example"
  local local_secret="$PROFILE_ROOT/dotfiles/secrets/secret.local"

  if [[ -f "$local_secret" ]]; then
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would create $local_secret from $example"
    return 0
  fi

  if [[ -f "$example" ]]; then
    mkdir -p "$(dirname "$local_secret")"
    cp "$example" "$local_secret"
    chmod 0600 "$local_secret"
    warn "created $local_secret from example. Fill it manually before relying on secrets."
    return 0
  fi

  warn "secret.example is missing. Skipping ~/.secret link."
  return 1
}

sync_live_codex_automations() {
  local runtime_dir="$HOME/.codex/automations"
  local automations_dir="$PROFILE_ROOT/agent/codex/automations"
  local syncer="$REPO_ROOT/shared/hooks/codex-sync-automations.py"
  local agent_python="$HOME/.local/share/agent-dotfiles/python/bin/python"

  [[ -d "$runtime_dir" && ! -L "$runtime_dir" ]] || return 0

  if [[ ! -f "$syncer" ]]; then
    warn "Codex automation sync hook missing, skipping live snapshot: $syncer"
    return 0
  fi

  if [[ ! -x "$agent_python" ]]; then
    warn "shared agent Python missing, skipping live Codex automation snapshot: $agent_python"
    return 0
  fi

  log "Snapshotting live Codex automations from $runtime_dir"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would run $agent_python $syncer --runtime-dir $runtime_dir --output-dir $automations_dir"
    return 0
  fi

  "$agent_python" "$syncer" \
    --runtime-dir "$runtime_dir" \
    --output-dir "$automations_dir" \
    >/dev/null
}

link_codex() {
  command -v codex >/dev/null 2>&1 || warn "codex command not found. Install step should run before linking Codex files."

  mkdir -p "$HOME/.codex"
  link_path "$PROFILE_ROOT/agent/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
  link_path "$PROFILE_ROOT/agent/codex/config.toml" "$HOME/.codex/config.toml"
  link_path "$PROFILE_ROOT/agent/codex/hooks.json" "$HOME/.codex/hooks.json"
  link_path "$PROFILE_ROOT/agent/codex/rules" "$HOME/.codex/rules" optional
  link_path "$PROFILE_ROOT/agent/codex/automations" "$HOME/.codex/automations" optional

  mkdir -p "$HOME/.agents/skills"
  link_profile_skills
}

link_dotfiles() {
  link_path "$PROFILE_ROOT/dotfiles/zsh/zshrc" "$HOME/.zshrc" optional
  link_path "$PROFILE_ROOT/dotfiles/zsh/zprofile" "$HOME/.zprofile" optional
  link_path "$PROFILE_ROOT/dotfiles/git/gitconfig" "$HOME/.gitconfig" optional
  link_path "$PROFILE_ROOT/dotfiles/git/gitignore_global" "$HOME/.gitignore_global" optional

  if ensure_secret_local; then
    local local_secret="$PROFILE_ROOT/dotfiles/secrets/secret.local"
    if [[ "$DRY_RUN" -eq 1 && ! -e "$local_secret" ]]; then
      log "Would link $HOME/.secret -> $local_secret"
    else
      link_path "$local_secret" "$HOME/.secret" optional
    fi
  fi
}

main() {
  parse_args "$@"
  validate_args

  sync_live_codex_automations
  link_codex
  link_dotfiles

  if [[ -n "$BACKUP_DIR" ]]; then
    if [[ "$DRY_RUN" -eq 1 ]]; then
      log "Would write backups under $BACKUP_DIR"
    else
      log "Backups written to $BACKUP_DIR"
    fi
  fi
}

main "$@"
