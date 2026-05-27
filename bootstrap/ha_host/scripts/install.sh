#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
PACKAGE_DIR="$PROFILE_DIR/packages"
BREW_FILE="$PACKAGE_DIR/Brewfile.core"
UV_TOOLS_FILE="$PACKAGE_DIR/uv-tools.txt"
AGENT_PYTHON_FILE="$PACKAGE_DIR/agent-python.txt"
AGENT_PYTHON_VERSION="3.12"
AGENT_PYTHON_VENV="$HOME/.local/share/agent-dotfiles/python"

DRY_RUN=0
SKIP_UV_TOOLS=0
SKIP_AGENT_PYTHON=0

usage() {
  cat <<'EOF'
Usage: bootstrap/bootstrap.sh --profile ha_host install [options]

Options:
  --dry-run             Print what would run without installing packages.
  --skip-uv-tools       Skip uv tool installation.
  --skip-agent-python   Skip shared agent Python venv installation.
  -h, --help            Show this help.
EOF
}

log() {
  printf '[ha_host:install] %s\n' "$*"
}

die() {
  printf '[ha_host:install] error: %s\n' "$*" >&2
  exit 1
}

ensure_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    eval "$(brew shellenv)"
    return 0
  fi

  log "Homebrew not found. Installing Homebrew."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  else
    die "Homebrew installation finished but brew is still unavailable"
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)
        DRY_RUN=1
        ;;
      --skip-uv-tools)
        SKIP_UV_TOOLS=1
        ;;
      --skip-agent-python)
        SKIP_AGENT_PYTHON=1
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

has_package_entries() {
  local file="$1"
  local line
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="$(trim "$line")"
    [[ -n "$line" ]] && return 0
  done < "$file"
  return 1
}

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

install_uv_tools() {
  [[ "$SKIP_UV_TOOLS" -eq 0 ]] || {
    log "Skipping uv tools."
    return 0
  }
  [[ -f "$UV_TOOLS_FILE" ]] || die "missing package file: $UV_TOOLS_FILE"

  if ! has_package_entries "$UV_TOOLS_FILE"; then
    log "No uv tools listed."
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would install uv tools from $UV_TOOLS_FILE"
    return 0
  fi

  command -v uv >/dev/null 2>&1 || die "uv is required before installing uv tools"

  local tool
  while IFS= read -r tool || [[ -n "$tool" ]]; do
    tool="${tool%%#*}"
    tool="$(trim "$tool")"
    [[ -n "$tool" ]] || continue

    if [[ "$tool" == ./* ]]; then
      log "Installing uv tool from local path: $tool"
      uv tool install --force "$REPO_ROOT/${tool#./}"
    else
      log "Installing uv tool: $tool"
      uv tool install --force "$tool"
    fi
  done < "$UV_TOOLS_FILE"
}

install_agent_python() {
  [[ "$SKIP_AGENT_PYTHON" -eq 0 ]] || {
    log "Skipping shared agent Python environment."
    return 0
  }
  [[ -f "$AGENT_PYTHON_FILE" ]] || die "missing package file: $AGENT_PYTHON_FILE"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would install uv-managed Python $AGENT_PYTHON_VERSION"
    log "Would create shared agent Python venv: $AGENT_PYTHON_VENV"
    log "Would install shared agent Python packages from $AGENT_PYTHON_FILE"
    return 0
  fi

  command -v uv >/dev/null 2>&1 || die "uv is required before installing shared agent Python"

  log "Installing uv-managed Python $AGENT_PYTHON_VERSION"
  uv python install "$AGENT_PYTHON_VERSION"

  log "Creating shared agent Python venv: $AGENT_PYTHON_VENV"
  uv venv "$AGENT_PYTHON_VENV" --python "$AGENT_PYTHON_VERSION"

  if has_package_entries "$AGENT_PYTHON_FILE"; then
    log "Installing shared agent Python packages from $AGENT_PYTHON_FILE"
    uv pip install --python "$AGENT_PYTHON_VENV/bin/python" -r "$AGENT_PYTHON_FILE"
  else
    log "No shared agent Python packages listed."
  fi
}

main() {
  parse_args "$@"
  [[ -f "$BREW_FILE" ]] || die "missing package file: $BREW_FILE"

  if ! has_package_entries "$BREW_FILE"; then
    log "No HA host packages are enabled yet: $BREW_FILE"
    log "Edit the profile package policy before running a real install."
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would run: brew bundle --file $BREW_FILE"
  else
    ensure_homebrew
    log "Installing HA host packages from $BREW_FILE"
    brew bundle --file "$BREW_FILE"
  fi

  install_uv_tools
  install_agent_python
}

main "$@"
