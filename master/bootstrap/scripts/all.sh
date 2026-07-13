#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_SCRIPT="$SCRIPT_DIR/install.sh"
LINKS_SCRIPT="$SCRIPT_DIR/links.sh"
VERIFY_SCRIPT="$SCRIPT_DIR/verify.sh"

AGENT="codex"
WITH_LARGE_APP=0
SKIP_UV_TOOLS=0
SKIP_AGENT_PYTHON=0
SKIP_NPM_GLOBAL=0
SKIP_MAS=0
WARM_ML_MODELS=0

usage() {
  cat <<'EOF'
Usage: master/bootstrap/bootstrap.sh all [options]

Options:
  --agent <name>         Agent to link and verify. Supported values: codex, cursor.
  --with-large-app       Install large GUI apps in the background during install.
  --skip-uv-tools        Skip uv tool installation.
  --skip-agent-python    Skip shared agent Python venv installation.
  --skip-npm-global      Skip global npm package installation.
  --skip-mas             Skip Mac App Store package installation.
  --warm-ml-models        Pre-download optional machine learning models during install.
  -h, --help             Show this help.
EOF
}

log() {
  printf '[master:all] %s\n' "$*"
}

die() {
  printf '[master:all] error: %s\n' "$*" >&2
  exit 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agent)
        [[ $# -ge 2 ]] || die "--agent requires a value"
        AGENT="$2"
        shift 2
        ;;
      --with-large-app)
        WITH_LARGE_APP=1
        shift
        ;;
      --skip-uv-tools)
        SKIP_UV_TOOLS=1
        shift
        ;;
      --skip-agent-python)
        SKIP_AGENT_PYTHON=1
        shift
        ;;
      --skip-npm-global)
        SKIP_NPM_GLOBAL=1
        shift
        ;;
      --skip-mas)
        SKIP_MAS=1
        shift
        ;;
      --warm-ml-models)
        WARM_ML_MODELS=1
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

require_script() {
  [[ -x "$1" ]] || die "missing executable script: $1"
}

run_install() {
  require_script "$INSTALL_SCRIPT"
  local args=()

  if [[ "$WITH_LARGE_APP" -eq 1 ]]; then
    args+=(--with-large-app)
  fi
  if [[ "$SKIP_UV_TOOLS" -eq 1 ]]; then
    args+=(--skip-uv-tools)
  fi
  if [[ "$SKIP_AGENT_PYTHON" -eq 1 ]]; then
    args+=(--skip-agent-python)
  fi
  if [[ "$SKIP_NPM_GLOBAL" -eq 1 ]]; then
    args+=(--skip-npm-global)
  fi
  if [[ "$SKIP_MAS" -eq 1 ]]; then
    args+=(--skip-mas)
  fi
  if [[ "$WARM_ML_MODELS" -eq 1 ]]; then
    args+=(--warm-ml-models)
  fi

  log "Running install"
  if [[ "${#args[@]}" -gt 0 ]]; then
    "$INSTALL_SCRIPT" "${args[@]}"
  else
    "$INSTALL_SCRIPT"
  fi
}

run_links() {
  require_script "$LINKS_SCRIPT"
  log "Running links for agent=$AGENT"
  "$LINKS_SCRIPT" --agent "$AGENT"
}

run_verify() {
  require_script "$VERIFY_SCRIPT"
  log "Running verify for agent=$AGENT"
  "$VERIFY_SCRIPT" --agent "$AGENT"
}

main() {
  parse_args "$@"
  validate_args
  run_install
  run_links
  run_verify
}

main "$@"
