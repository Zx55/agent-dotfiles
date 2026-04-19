#!/usr/bin/env bash

set -euo pipefail

REPO_API_BASE="https://api.github.com/repos/noho/dayu-agent/releases"
DAYU_PACKAGE_NAME="dayu-agent"
DEFAULT_WORKSPACE="$HOME/.dayu/workspace"
TEMP_UV_CACHE_DIR=0

usage() {
  cat <<'EOF'
Install or update Dayu CLI with uv-managed Python, then optionally run dayu-cli init.

Usage:
  dayu_install_or_update.sh [--workspace PATH] [--version latest|TAG] [--skip-init] [--overwrite-init]

Options:
  --workspace PATH   Workspace to initialize with dayu-cli init. Default: ~/.dayu/workspace
  --version VALUE    Release tag such as v0.1.1, or latest. Default: latest
  --skip-init        Install or update Dayu without running dayu-cli init
  --overwrite-init   Pass --overwrite to dayu-cli init
  -h, --help         Show this help text
EOF
}

log() {
  printf '[dayu-install] %s\n' "$*"
}

warn() {
  printf '[dayu-install][warn] %s\n' "$*" >&2
}

die() {
  printf '[dayu-install][error] %s\n' "$*" >&2
  exit 1
}

cleanup() {
  if [[ "${TEMP_UV_CACHE_DIR:-0}" -eq 1 ]] && [[ -n "${UV_CACHE_DIR:-}" ]]; then
    rm -rf "$UV_CACHE_DIR"
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

setup_uv_cache_dir() {
  if [[ -n "${UV_CACHE_DIR:-}" ]]; then
    return
  fi

  if mkdir -p "$HOME/.cache/uv" >/dev/null 2>&1 && [[ -w "$HOME/.cache/uv" ]]; then
    return
  fi

  UV_CACHE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dayu-uv-cache.XXXXXX")"
  export UV_CACHE_DIR
  TEMP_UV_CACHE_DIR=1
  warn "uv cache directory is not writable; using temporary UV_CACHE_DIR=$UV_CACHE_DIR"
}

parse_args() {
  WORKSPACE="$DEFAULT_WORKSPACE"
  RELEASE_TAG="latest"
  SKIP_INIT=0
  OVERWRITE_INIT=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --workspace)
        [[ $# -ge 2 ]] || die "--workspace requires a value"
        WORKSPACE="$2"
        shift 2
        ;;
      --version)
        [[ $# -ge 2 ]] || die "--version requires a value"
        RELEASE_TAG="$2"
        shift 2
        ;;
      --skip-init)
        SKIP_INIT=1
        shift
        ;;
      --overwrite-init)
        OVERWRITE_INIT=1
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown argument: $1"
        ;;
    esac
  done

  case "$WORKSPACE" in
    "~")
      WORKSPACE="$HOME"
      ;;
    "~/"*)
      WORKSPACE="$HOME/${WORKSPACE#~/}"
      ;;
  esac
}

detect_uv() {
  if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
    return
  fi

  log "uv not found; installing it with the official standalone installer"
  require_cmd curl

  if ! curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh; then
    die "Failed to install uv. Check network settings, and if this environment requires a proxy, configure it before retrying."
  fi

  if [[ -x "$HOME/.local/bin/uv" ]]; then
    UV_BIN="$HOME/.local/bin/uv"
  elif [[ -x "$HOME/.cargo/bin/uv" ]]; then
    UV_BIN="$HOME/.cargo/bin/uv"
  else
    die "uv installer finished but uv was not found in ~/.local/bin or ~/.cargo/bin"
  fi
}

ensure_managed_python() {
  if "$UV_BIN" python find --managed-python 3.11 >/dev/null 2>&1; then
    PYTHON_REQUEST="3.11"
    return
  fi

  log "Installing uv-managed Python 3.11"
  "$UV_BIN" python install --managed-python 3.11 || die "Failed to install uv-managed Python 3.11"
  "$UV_BIN" python find --managed-python 3.11 >/dev/null 2>&1 || die "uv-managed Python 3.11 is still unavailable after install"
  PYTHON_REQUEST="3.11"
}

resolve_release_metadata() {
  local api_url
  local release_json

  if [[ "$RELEASE_TAG" == "latest" ]]; then
    api_url="$REPO_API_BASE/latest"
  else
    api_url="$REPO_API_BASE/tags/$RELEASE_TAG"
  fi

  release_json="$(curl --fail --silent --show-error --location --retry 2 --retry-delay 1 "$api_url")" \
    || die "Failed to resolve Dayu release metadata from GitHub. Check network settings, and if this environment requires a proxy, configure it before retrying."

  RESOLVED_TAG="$(printf '%s\n' "$release_json" | sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
  WHEEL_URL="$(printf '%s\n' "$release_json" | sed -n 's/.*"browser_download_url":[[:space:]]*"\([^"]*dayu_agent-[^"]*\.whl\)".*/\1/p' | head -n1)"

  [[ -n "$RESOLVED_TAG" ]] || die "Could not parse the Dayu release tag from GitHub metadata"
  [[ -n "$WHEEL_URL" ]] || die "Could not find a Dayu wheel asset in GitHub release metadata"
}

install_dayu_tool() {
  local requirement
  requirement="$DAYU_PACKAGE_NAME @ $WHEEL_URL"

  log "Installing Dayu from $RESOLVED_TAG"
  "$UV_BIN" tool install \
    --managed-python \
    --python "$PYTHON_REQUEST" \
    --force \
    "$requirement" \
    || die "uv tool install failed for $requirement"

  TOOL_BIN_DIR="$("$UV_BIN" tool dir --bin)"
  [[ -n "$TOOL_BIN_DIR" ]] || die "Could not determine uv tool bin directory"
}

resolve_executable() {
  local name="$1"

  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi

  if [[ -x "$TOOL_BIN_DIR/$name" ]]; then
    printf '%s\n' "$TOOL_BIN_DIR/$name"
    return 0
  fi

  return 1
}

verify_dayu_commands() {
  DAYU_CLI_BIN="$(resolve_executable dayu-cli)" || die "dayu-cli was not found after installation"
  DAYU_RENDER_BIN="$(resolve_executable dayu-render)" || die "dayu-render was not found after installation"
  local render_output render_status

  "$DAYU_CLI_BIN" --help >/dev/null || die "dayu-cli --help failed after installation"
  set +e
  render_output="$("$DAYU_RENDER_BIN" 2>&1)"
  render_status=$?
  set -e
  if [[ "$render_status" -eq 0 ]]; then
    return
  fi
  printf '%s\n' "$render_output" | grep -q 'Usage:' \
    && printf '%s\n' "$render_output" | grep -Eq 'input_markdown|dayu-render' \
    || die "dayu-render did not return expected usage text after installation"
}

run_init_if_requested() {
  if [[ "$SKIP_INIT" -eq 1 ]]; then
    log "Skipping dayu-cli init as requested"
    return
  fi

  if [[ ! -t 0 || ! -t 1 ]]; then
    die "dayu-cli init is interactive and requires a TTY. Re-run this script in an interactive terminal or pass --skip-init."
  fi

  mkdir -p "$WORKSPACE"

  local init_cmd=("$DAYU_CLI_BIN" init --base "$WORKSPACE")
  if [[ "$OVERWRITE_INIT" -eq 1 ]]; then
    init_cmd+=(--overwrite)
  fi

  log "Running ${init_cmd[*]}"
  "${init_cmd[@]}"
}

verify_workspace_if_initialized() {
  if [[ "$SKIP_INIT" -eq 1 ]]; then
    return
  fi

  [[ -d "$WORKSPACE/config" ]] || die "Expected $WORKSPACE/config to exist after dayu-cli init"

  if ! find "$WORKSPACE/config" -mindepth 1 -maxdepth 2 -type f | grep -q .; then
    die "Expected $WORKSPACE/config to contain initialized config files"
  fi
}

warn_optional_render_dependencies() {
  if ! command -v pandoc >/dev/null 2>&1; then
    warn "pandoc is not installed; PDF rendering may be unavailable until it is installed"
  fi

  if [[ "$(uname -s)" == "Darwin" ]] && [[ ! -d "/Applications/Google Chrome.app" ]] && [[ ! -d "$HOME/Applications/Google Chrome.app" ]]; then
    warn "Google Chrome was not found in standard macOS locations; some render flows may need it"
  fi
}

print_summary() {
  log "Setup complete"
  printf '  uv: %s\n' "$UV_BIN"
  printf '  release: %s\n' "$RESOLVED_TAG"
  printf '  tool bin: %s\n' "$TOOL_BIN_DIR"
  printf '  dayu-cli: %s\n' "$DAYU_CLI_BIN"
  printf '  dayu-render: %s\n' "$DAYU_RENDER_BIN"

  if [[ "$SKIP_INIT" -eq 1 ]]; then
    printf '  workspace init: skipped\n'
  else
    printf '  workspace init: %s\n' "$WORKSPACE"
  fi

  if ! command -v dayu-cli >/dev/null 2>&1; then
    warn "dayu-cli is installed but not on PATH in this shell. You may need to add $TOOL_BIN_DIR to PATH."
  fi
}

main() {
  trap cleanup EXIT
  parse_args "$@"
  detect_uv
  setup_uv_cache_dir
  ensure_managed_python
  resolve_release_metadata
  install_dayu_tool
  verify_dayu_commands
  run_init_if_requested
  verify_workspace_if_initialized
  warn_optional_render_dependencies
  print_summary
}

main "$@"
