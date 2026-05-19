#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$BOOTSTRAP_DIR/.." && pwd)"
PACKAGE_DIR="$BOOTSTRAP_DIR/packages"
LOG_DIR="${HOME}/.dotfiles-bootstrap/logs"

WITH_LARGE_APP=0
SKIP_UV_TOOLS=0
SKIP_AGENT_PYTHON=0
SKIP_NPM_GLOBAL=0
SKIP_MAS=0
WARM_ML_MODELS=0
LARGE_APP_PID=""
LARGE_APP_LOG=""
AGENT_PYTHON_VERSION="3.12"
AGENT_PYTHON_VENV="$HOME/.local/share/agent-dotfiles/python"

usage() {
  cat <<'EOF'
Usage: bootstrap/scripts/install.sh [options]

Options:
  --with-large-app       Install large GUI apps in the background after core brew packages.
  --skip-uv-tools        Skip uv tool installation.
  --skip-agent-python    Skip shared agent Python venv installation.
  --skip-npm-global      Skip global npm package installation.
  --skip-mas             Skip Mac App Store package installation.
  --warm-ml-models        Pre-download optional machine learning models.
  -h, --help             Show this help.
EOF
}

log() {
  printf '[install] %s\n' "$*"
}

warn() {
  printf '[install] warning: %s\n' "$*" >&2
}

die() {
  printf '[install] error: %s\n' "$*" >&2
  exit 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --with-large-app)
        WITH_LARGE_APP=1
        ;;
      --skip-uv-tools)
        SKIP_UV_TOOLS=1
        ;;
      --skip-agent-python)
        SKIP_AGENT_PYTHON=1
        ;;
      --skip-npm-global)
        SKIP_NPM_GLOBAL=1
        ;;
      --skip-mas)
        SKIP_MAS=1
        ;;
      --warm-ml-models)
        WARM_ML_MODELS=1
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

ensure_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    eval "$(brew shellenv)"
    return
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

require_file() {
  [[ -f "$1" ]] || die "missing package file: $1"
}

run_brew_bundle_core() {
  local file="$PACKAGE_DIR/Brewfile.core"
  require_file "$file"
  log "Installing core Homebrew packages from $file"
  brew bundle --file "$file"
}

start_large_app_install() {
  local file="$PACKAGE_DIR/Brewfile.large-app"
  require_file "$file"
  mkdir -p "$LOG_DIR"
  LARGE_APP_LOG="$LOG_DIR/large-app-$(date +%Y%m%d-%H%M%S).log"

  log "Starting large app installation in the background. log=$LARGE_APP_LOG"
  (
    set -euo pipefail
    cd "$REPO_ROOT"
    brew bundle --file "$file"
  ) >"$LARGE_APP_LOG" 2>&1 &
  LARGE_APP_PID="$!"
}

report_large_app_status() {
  [[ -n "$LARGE_APP_PID" ]] || return 0

  if jobs -r -p | grep -qx "$LARGE_APP_PID"; then
    warn "large app installation is still running. pid=$LARGE_APP_PID log=$LARGE_APP_LOG"
    return 0
  fi

  if wait "$LARGE_APP_PID"; then
    log "Large app installation completed."
  else
    warn "large app installation failed. Core install completed. See $LARGE_APP_LOG"
  fi
}

install_uv_tools() {
  local file="$PACKAGE_DIR/uv-tools.txt"
  [[ "$SKIP_UV_TOOLS" -eq 0 ]] || {
    log "Skipping uv tools."
    return 0
  }
  require_file "$file"
  command -v uv >/dev/null 2>&1 || die "uv is required before installing uv tools"

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
  done < "$file"
}

warm_ml_models() {
  [[ "$WARM_ML_MODELS" -eq 1 ]] || return 0
  local script="$BOOTSTRAP_DIR/scripts/warm_ml_models.sh"
  [[ -x "$script" ]] || die "missing executable script: $script"
  log "Pre-downloading machine learning models from $PACKAGE_DIR/ml-models.tsv"
  "$script"
}

install_agent_python() {
  local file="$PACKAGE_DIR/agent-python.txt"
  [[ "$SKIP_AGENT_PYTHON" -eq 0 ]] || {
    log "Skipping shared agent Python environment."
    return 0
  }
  require_file "$file"
  command -v uv >/dev/null 2>&1 || die "uv is required before installing shared agent Python"

  log "Installing uv-managed Python $AGENT_PYTHON_VERSION"
  uv python install "$AGENT_PYTHON_VERSION"

  log "Creating shared agent Python venv: $AGENT_PYTHON_VENV"
  uv venv "$AGENT_PYTHON_VENV" --python "$AGENT_PYTHON_VERSION"

  if has_package_entries "$file"; then
    log "Installing shared agent Python packages from $file"
    uv pip install --python "$AGENT_PYTHON_VENV/bin/python" -r "$file"
  else
    log "No shared agent Python packages listed."
  fi
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

install_npm_globals() {
  local file="$PACKAGE_DIR/npm-global.txt"
  [[ "$SKIP_NPM_GLOBAL" -eq 0 ]] || {
    log "Skipping npm global packages."
    return 0
  }
  require_file "$file"
  [[ -s "$file" ]] || {
    log "No npm global packages listed."
    return 0
  }
  command -v npm >/dev/null 2>&1 || die "npm is required before installing global npm packages"

  while IFS= read -r package || [[ -n "$package" ]]; do
    package="${package%%#*}"
    package="$(trim "$package")"
    [[ -n "$package" ]] || continue
    log "Installing npm global package: $package"
    npm install -g "$package"
  done < "$file"
}

install_local_tools() {
  local file="$PACKAGE_DIR/local-tools.txt"
  require_file "$file"
  mkdir -p "$HOME/.local/bin"

  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="$(trim "$line")"
    [[ -n "$line" ]] || continue

    local source_path="${line%%|*}"
    local dest_path="${line#*|}"
    source_path="$(trim "$source_path")"
    dest_path="$(trim "$dest_path")"
    [[ "$source_path" != "$dest_path" ]] || die "invalid local tool mapping: $line"

    source_path="$(expand_path "$source_path")"
    dest_path="$(expand_path "$dest_path")"
    [[ -f "$source_path" ]] || die "local tool source missing: $source_path"

    log "Installing local tool: $dest_path"
    mkdir -p "$(dirname "$dest_path")"
    install -m 0755 "$source_path" "$dest_path"
  done < "$file"
}

install_mas_apps() {
  local file="$PACKAGE_DIR/mas-apps.txt"
  [[ "$SKIP_MAS" -eq 0 ]] || {
    log "Skipping Mac App Store apps."
    return 0
  }
  require_file "$file"
  [[ -s "$file" ]] || {
    log "No Mac App Store apps listed."
    return 0
  }
  command -v mas >/dev/null 2>&1 || {
    warn "mas is unavailable. Skipping Mac App Store apps."
    return 0
  }
  if ! mas account >/dev/null 2>&1; then
    warn "not signed in to the Mac App Store. Skipping mas apps."
    return 0
  fi

  while IFS= read -r line || [[ -n "$line" ]]; do
    line="$(trim "$line")"
    [[ -n "$line" ]] || continue
    [[ "$line" != \#* ]] || continue

    local app_id="${line%%[[:space:]]*}"
    if [[ ! "$app_id" =~ ^[0-9]+$ ]]; then
      warn "skipping invalid mas app line: $line"
      continue
    fi

    log "Installing Mac App Store app: $app_id"
    if ! mas install "$app_id"; then
      warn "failed to install Mac App Store app: $app_id"
    fi
  done < "$file"
}

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

expand_path() {
  local value="$1"
  case "$value" in
    "~")
      printf '%s\n' "$HOME"
      ;;
    "~/"*)
      printf '%s\n' "$HOME/${value#~/}"
      ;;
    /*)
      printf '%s\n' "$value"
      ;;
    *)
      printf '%s\n' "$REPO_ROOT/$value"
      ;;
  esac
}

main() {
  parse_args "$@"
  cd "$REPO_ROOT"

  ensure_homebrew
  run_brew_bundle_core

  if [[ "$WITH_LARGE_APP" -eq 1 ]]; then
    start_large_app_install
  fi

  install_uv_tools
  warm_ml_models
  install_agent_python
  install_npm_globals
  install_local_tools
  install_mas_apps
  report_large_app_status
}

main "$@"
