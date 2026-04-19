#!/usr/bin/env bash

set -euo pipefail

DEFAULT_WORKSPACE="$HOME/.dayu/workspace"

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
  if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
    note "uv: $UV_BIN ($("$UV_BIN" --version))"
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
    tool_list="$("$UV_BIN" tool list --show-version-specifiers --show-python 2>/dev/null || true)"
    if printf '%s\n' "$tool_list" | grep -q 'dayu-agent'; then
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
    note "dayu-render: $render_bin"
    if ! "$render_bin" --help >/dev/null 2>&1; then
      fail "dayu-render exists but --help failed"
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
