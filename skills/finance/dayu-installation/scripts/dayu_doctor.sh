#!/usr/bin/env bash

set -euo pipefail

DEFAULT_WORKSPACE="$HOME/.dayu/workspace"
TEMP_UV_CACHE_DIR=0

usage() {
  cat <<'EOF'
Inspect the local Dayu installation state.

Usage:
  dayu_doctor.sh [--workspace PATH]

Options:
  --workspace PATH   Workspace to inspect. Default: ~/.dayu/workspace
  -h, --help         Show this help text
EOF
}

note() {
  printf '[dayu-doctor] %s\n' "$*"
}

warn() {
  printf '[dayu-doctor][warn] %s\n' "$*" >&2
}

fail() {
  printf '[dayu-doctor][error] %s\n' "$*" >&2
  STATUS=1
}

cleanup() {
  if [[ "${TEMP_UV_CACHE_DIR:-0}" -eq 1 ]] && [[ -n "${UV_CACHE_DIR:-}" ]]; then
    rm -rf "$UV_CACHE_DIR"
  fi
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

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --workspace)
        [[ $# -ge 2 ]] || {
          printf '[dayu-doctor][error] --workspace requires a value\n' >&2
          exit 1
        }
        WORKSPACE="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        printf '[dayu-doctor][error] Unknown argument: %s\n' "$1" >&2
        exit 1
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

resolve_tool_bin_dir() {
  if [[ -n "${UV_BIN:-}" ]]; then
    TOOL_BIN_DIR="$("$UV_BIN" tool dir --bin 2>/dev/null || true)"
  fi
}

resolve_executable() {
  local name="$1"

  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi

  if [[ -n "${TOOL_BIN_DIR:-}" ]] && [[ -x "$TOOL_BIN_DIR/$name" ]]; then
    printf '%s\n' "$TOOL_BIN_DIR/$name"
    return 0
  fi

  return 1
}

check_uv() {
  setup_uv_cache_dir

  if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
    note "uv: $UV_BIN ($("$UV_BIN" --version 2>/dev/null))"
  elif [[ -x "$HOME/.local/bin/uv" ]]; then
    UV_BIN="$HOME/.local/bin/uv"
    warn "uv is installed at $UV_BIN but is not on PATH"
  else
    fail "uv is not installed"
    return
  fi

  if "$UV_BIN" python find --managed-python 3.11 >/dev/null 2>&1; then
    note "uv-managed Python 3.11+: $("$UV_BIN" python find --managed-python 3.11)"
  else
    fail "uv-managed Python 3.11+ is not installed"
  fi

  resolve_tool_bin_dir
}

check_dayu_install() {
  local cli_bin render_bin

  if [[ -n "${UV_BIN:-}" ]]; then
    local tool_list
    local tool_list_status
    set +e
    tool_list="$("$UV_BIN" tool list --show-version-specifiers --show-python 2>&1)"
    tool_list_status=$?
    set -e
    if [[ "$tool_list_status" -ne 0 ]]; then
      warn "could not inspect uv tool list; continuing with executable checks"
    elif printf '%s\n' "$tool_list" | grep -q 'dayu-agent'; then
      note "uv tool list contains dayu-agent"
    else
      warn "uv tool list does not show dayu-agent"
    fi
  fi

  if cli_bin="$(resolve_executable dayu-cli)"; then
    note "dayu-cli: $cli_bin"
    if ! "$cli_bin" --help >/dev/null 2>&1; then
      fail "dayu-cli exists but --help failed"
    fi
  else
    fail "dayu-cli is not available"
  fi

  if render_bin="$(resolve_executable dayu-render)"; then
    local render_output render_status
    note "dayu-render: $render_bin"
    set +e
    render_output="$("$render_bin" 2>&1)"
    render_status=$?
    set -e
    if [[ "$render_status" -eq 0 ]]; then
      note "dayu-render invocation succeeded"
    elif printf '%s\n' "$render_output" | grep -q 'Usage:' \
      && printf '%s\n' "$render_output" | grep -Eq 'input_markdown|dayu-render'; then
      note "dayu-render responds with usage text"
    else
      fail "dayu-render exists but did not return expected usage text"
    fi
  else
    fail "dayu-render is not available"
  fi
}

check_workspace() {
  if [[ -d "$WORKSPACE/config" ]]; then
    note "workspace config directory exists: $WORKSPACE/config"
    if find "$WORKSPACE/config" -mindepth 1 -maxdepth 2 -type f | grep -q .; then
      note "workspace config appears populated"
    else
      warn "workspace config directory exists but appears empty"
    fi
  else
    warn "workspace is not initialized: missing $WORKSPACE/config"
  fi
}

check_optional_dependencies() {
  if command -v pandoc >/dev/null 2>&1; then
    note "pandoc: $(command -v pandoc)"
  else
    warn "pandoc is not installed; PDF rendering may be unavailable"
  fi

  if [[ "$(uname -s)" == "Darwin" ]]; then
    if [[ -d "/Applications/Google Chrome.app" ]] || [[ -d "$HOME/Applications/Google Chrome.app" ]]; then
      note "Google Chrome: found"
    else
      warn "Google Chrome not found in standard macOS locations"
    fi
  fi
}

main() {
  STATUS=0
  trap cleanup EXIT
  parse_args "$@"

  note "workspace target: $WORKSPACE"
  check_uv
  check_dayu_install
  check_workspace
  check_optional_dependencies

  if [[ "$STATUS" -ne 0 ]]; then
    exit "$STATUS"
  fi
}

main "$@"
