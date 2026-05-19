#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$BOOTSTRAP_DIR/.." && pwd)"
BACKUP_ROOT="${HOME}/.dotfiles-backup"
BACKUP_DIR=""
AGENT="codex"

usage() {
  cat <<'EOF'
Usage: bootstrap/scripts/links.sh [options]

Options:
  --agent <name>         Agent to link. Currently only "codex" is supported.
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

copy_path() {
  local source="$1"
  local target="$2"
  local required="${3:-required}"

  if [[ ! -f "$source" ]]; then
    if [[ "$required" == "required" ]]; then
      die "source missing: $source"
    fi
    warn "optional source missing, skipping: $source"
    return 0
  fi

  mkdir -p "$(dirname "$target")"

  if [[ -f "$target" && ! -L "$target" ]] && cmp -s "$source" "$target"; then
    log "Already copied: $target"
    return 0
  fi

  backup_target "$target"
  log "Copying $source -> $target"
  cp "$source" "$target"
}

escape_sed_replacement() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//&/\\&}"
  value="${value//|/\\|}"
  printf '%s' "$value"
}

copy_portable_toml() {
  local source="$1"
  local target="$2"
  local required="${3:-required}"

  if [[ ! -f "$source" ]]; then
    if [[ "$required" == "required" ]]; then
      die "source missing: $source"
    fi
    warn "optional source missing, skipping: $source"
    return 0
  fi

  mkdir -p "$(dirname "$target")"

  local escaped_home
  local expanded
  escaped_home="$(escape_sed_replacement "$HOME")"
  expanded="$(sed \
    -e "s|](~/|]($escaped_home/|g" \
    -e "s|\"~/|\"$escaped_home/|g" \
    "$source")"

  if [[ -f "$target" && ! -L "$target" && "$(cat "$target")" == "$expanded" ]]; then
    log "Already copied: $target"
    return 0
  fi

  backup_target "$target"
  log "Copying portable TOML $source -> $target"
  printf '%s\n' "$expanded" > "$target"
}

ensure_secret_local() {
  local example="$REPO_ROOT/dotfiles/secrets/secret.example"
  local local_secret="$REPO_ROOT/dotfiles/secrets/secret.local"

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
  link_path "$REPO_ROOT/agents/AGENTS.md" "$HOME/.codex/AGENTS.md"
  copy_path "$REPO_ROOT/agents/codex/config.toml" "$HOME/.codex/config.toml"
  link_path "$REPO_ROOT/agents/codex/hooks.json" "$HOME/.codex/hooks.json"
  link_path "$REPO_ROOT/agents/codex/memories" "$HOME/.codex/memories"
  link_path "$REPO_ROOT/agents/codex/rules" "$HOME/.codex/rules" optional

  mkdir -p "$HOME/.codex/skills"
  local skill_dir
  for skill_dir in "$REPO_ROOT"/agents/skills/*; do
    [[ -d "$skill_dir" ]] || continue
    link_path "$skill_dir" "$HOME/.codex/skills/$(basename "$skill_dir")"
  done
}

install_codex_automations() {
  local automations_dir="$REPO_ROOT/agents/codex/automations"
  local automation_dir
  [[ -d "$automations_dir" ]] || return 0

  mkdir -p "$HOME/.codex/automations"

  for automation_dir in "$automations_dir"/*; do
    [[ -d "$automation_dir" ]] || continue
    copy_portable_toml \
      "$automation_dir/automation.toml" \
      "$HOME/.codex/automations/$(basename "$automation_dir")/automation.toml"
  done
}

link_dotfiles() {
  link_path "$REPO_ROOT/dotfiles/zsh/zshrc" "$HOME/.zshrc" optional
  link_path "$REPO_ROOT/dotfiles/zsh/zprofile" "$HOME/.zprofile" optional
  link_path "$REPO_ROOT/dotfiles/git/gitconfig" "$HOME/.gitconfig" optional
  link_path "$REPO_ROOT/dotfiles/git/gitignore_global" "$HOME/.gitignore_global" optional

  if ensure_secret_local; then
    link_path "$REPO_ROOT/dotfiles/secrets/secret.local" "$HOME/.secret" optional
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

  link_codex
  install_codex_automations
  link_dotfiles
  configure_git_hooks

  if [[ -n "$BACKUP_DIR" ]]; then
    log "Backups written to $BACKUP_DIR"
  fi
}

main "$@"
