#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROFILE_ROOT="$(cd "$PROFILE_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
BACKUP_ROOT="${HOME}/.dotfiles-backup"
BACKUP_DIR=""
AGENT="codex"

usage() {
  cat <<'EOF'
Usage: master/bootstrap/bootstrap.sh links [options]

Options:
  --agent <name>         Agent to link. Supported values: codex, cursor.
  -h, --help             Show this help.
EOF
}

log() {
  printf '[links] %s\n' "$*"
}

warn() {
  printf '[links] warning: %s\n' "$*" >&2
}

die() {
  printf '[links] error: %s\n' "$*" >&2
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
    codex|cursor)
      ;;
    *)
      die "unsupported agent: $AGENT"
      ;;
  esac
}

init_backup_dir() {
  if [[ -z "$BACKUP_DIR" ]]; then
    BACKUP_DIR="$BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
  fi
}

backup_target() {
  local target="$1"
  [[ -e "$target" || -L "$target" ]] || return 0

  init_backup_dir
  local relative="${target#$HOME/}"
  local backup_path="$BACKUP_DIR/$relative"
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

  mkdir -p "$(dirname "$target")"

  if same_symlink "$source" "$target"; then
    log "Already linked: $target"
    return 0
  fi

  backup_target "$target"
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
  local target="$HOME/.codex/skills/$category"

  if [[ -L "$target" || ( -e "$target" && ! -d "$target" ) ]]; then
    backup_target "$target"
  fi
  mkdir -p "$target"
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
    link_path "$source" "$HOME/.codex/skills/$relative"
  done < <(find "$skills_root" -mindepth 2 -maxdepth 2 -type l | sort)
}

ensure_secret_local() {
  local example="$PROFILE_ROOT/dotfiles/secrets/secret.example"
  local local_secret="$PROFILE_ROOT/dotfiles/secrets/secret.local"

  if [[ -f "$local_secret" ]]; then
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

link_codex() {
  command -v codex >/dev/null 2>&1 || warn "codex command not found. Install step should run before linking Codex files."

  mkdir -p "$HOME/.codex"
  link_path "$PROFILE_ROOT/agent/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
  link_path "$PROFILE_ROOT/agent/codex/config.toml" "$HOME/.codex/config.toml"
  link_path "$PROFILE_ROOT/agent/codex/hooks.json" "$HOME/.codex/hooks.json"
  link_path "$PROFILE_ROOT/agent/codex/rules" "$HOME/.codex/rules" optional
  link_path "$PROFILE_ROOT/agent/codex/automations" "$HOME/.codex/automations" optional

  mkdir -p "$HOME/.codex/skills"
  link_profile_skills
}

sync_live_cursor_settings() {
  local settings="$HOME/Library/Application Support/Cursor/User/settings.json"
  local output="$PROFILE_ROOT/agent/cursor/settings.json"
  local syncer="$REPO_ROOT/shared/hooks/cursor-sync-settings.py"
  local agent_python="$HOME/.local/share/agent-dotfiles/python/bin/python"

  [[ -f "$settings" ]] || return 0

  if [[ ! -f "$syncer" ]]; then
    warn "Cursor settings sync hook missing, skipping live snapshot: $syncer"
    return 0
  fi

  if [[ ! -x "$agent_python" ]]; then
    warn "shared agent Python missing, skipping live Cursor settings snapshot: $agent_python"
    return 0
  fi

  log "Snapshotting live Cursor settings from $settings"
  "$agent_python" "$syncer" \
    --settings "$settings" \
    --output "$output" \
    >/dev/null
}

link_cursor() {
  mkdir -p "$HOME/.cursor"

  link_path "$PROFILE_ROOT/agent/cursor/mcp.json" "$HOME/.cursor/mcp.json"
  link_path "$PROFILE_ROOT/agent/cursor/hooks.json" "$HOME/.cursor/hooks.json"
  link_path "$PROFILE_ROOT/agent/cursor/sandbox.json" "$HOME/.cursor/sandbox.json"
  warn "Cursor User Rules cannot be linked automatically. Manually copy $PROFILE_ROOT/agent/cursor/user-rules.md into Cursor Settings > Rules."
}

sync_live_codex_automations() {
  local runtime_dir="$HOME/.codex/automations"
  local automations_dir="$PROFILE_ROOT/agent/codex/automations"
  local syncer="$REPO_ROOT/shared/hooks/codex-sync-automations.py"
  local agent_python="$HOME/.local/share/agent-dotfiles/python/bin/python"

  [[ -d "$runtime_dir" ]] || return 0

  if [[ ! -f "$syncer" ]]; then
    warn "Codex automation sync hook missing, skipping live snapshot: $syncer"
    return 0
  fi

  if [[ ! -x "$agent_python" ]]; then
    warn "shared agent Python missing, skipping live Codex automation snapshot: $agent_python"
    return 0
  fi

  log "Snapshotting live Codex automations from $runtime_dir"
  "$agent_python" "$syncer" \
    --runtime-dir "$runtime_dir" \
    --output-dir "$automations_dir" \
    >/dev/null
}

link_dotfiles() {
  link_path "$PROFILE_ROOT/dotfiles/zsh/zshrc" "$HOME/.zshrc" optional
  link_path "$PROFILE_ROOT/dotfiles/zsh/zprofile" "$HOME/.zprofile" optional
  link_path "$PROFILE_ROOT/dotfiles/git/gitconfig" "$HOME/.gitconfig" optional
  link_path "$PROFILE_ROOT/dotfiles/git/gitignore_global" "$HOME/.gitignore_global" optional

  if ensure_secret_local; then
    link_path "$PROFILE_ROOT/dotfiles/secrets/secret.local" "$HOME/.secret" optional
  fi
}

configure_git_hooks() {
  if [[ -d "$REPO_ROOT/.git" && -d "$REPO_ROOT/.githooks" ]]; then
    log "Configuring git hooks path"
    git -C "$REPO_ROOT" config core.hooksPath .githooks
  fi
}

main() {
  parse_args "$@"
  validate_args

  case "$AGENT" in
    codex)
      sync_live_codex_automations
      link_codex
      ;;
    cursor)
      sync_live_cursor_settings
      link_cursor
      ;;
  esac

  link_dotfiles
  configure_git_hooks

  if [[ -n "$BACKUP_DIR" ]]; then
    log "Backups written to $BACKUP_DIR"
  fi
}

main "$@"
