#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_SCRIPT="$SCRIPT_DIR/scripts/install.sh"
LINKS_SCRIPT="$SCRIPT_DIR/scripts/links.sh"
VERIFY_SCRIPT="$SCRIPT_DIR/scripts/verify.sh"

AGENT="codex"
ONLY="all"
WITH_LARGE_APP=0
SKIP_UV_TOOLS=0
SKIP_AGENT_PYTHON=0
SKIP_NPM_GLOBAL=0
SKIP_MAS=0
WARM_ML_MODELS=0

usage() {
  cat <<'EOF'
Usage: bootstrap/bootstrap.sh [options]

Options:
  --agent <name>         Agent to bootstrap. Currently only "codex" is supported.
  --only <step>          Run only one step: install, links, or verify.
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
  printf '[bootstrap] %s\n' "$*"
}

die() {
  printf '[bootstrap] error: %s\n' "$*" >&2
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
      --only)
        [[ $# -ge 2 ]] || die "--only requires a value"
        ONLY="$2"
        shift
        ;;
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

validate_args() {
  case "$AGENT" in
    codex)
      ;;
    *)
      die "unsupported agent: $AGENT"
      ;;
  esac

  case "$ONLY" in
    all|install|links|verify)
      ;;
    *)
      die "unsupported --only value: $ONLY"
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

  log "Running install step for agent=$AGENT"
  "$INSTALL_SCRIPT" "${args[@]}"
}

run_links() {
  require_script "$LINKS_SCRIPT"
  log "Running links step for agent=$AGENT"
  "$LINKS_SCRIPT" --agent "$AGENT"
}

run_verify() {
  require_script "$VERIFY_SCRIPT"
  log "Running verify step for agent=$AGENT"
  "$VERIFY_SCRIPT" --agent "$AGENT"
}

main() {
  parse_args "$@"
  validate_args

  case "$ONLY" in
    all)
      run_install
      run_links
      run_verify
      ;;
    install)
      run_install
      ;;
    links)
      run_links
      ;;
    verify)
      run_verify
      ;;
  esac
}

main "$@"
