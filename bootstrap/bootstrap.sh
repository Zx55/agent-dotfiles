#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROFILE="master"
STEP=""
STEP_ARGS=()

usage() {
  cat <<'EOF'
Usage: bootstrap/bootstrap.sh [options] <step> [step options]

Options:
  --profile <name>      Bootstrap profile to run. Defaults to "master".
  -h, --help            Show this help.

Steps are resolved from bootstrap/<profile>/scripts/<step>.sh.

Examples:
  ./bootstrap/bootstrap.sh --profile master all --agent codex
  ./bootstrap/bootstrap.sh --profile master install --with-large-app
  ./bootstrap/bootstrap.sh --profile master links --agent codex
  ./bootstrap/bootstrap.sh --profile master verify --agent codex
  ./bootstrap/bootstrap.sh --profile ha_host audit
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
      --profile)
        [[ $# -ge 2 ]] || die "--profile requires a value"
        PROFILE="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      --)
        shift
        [[ $# -gt 0 ]] || die "missing step after --"
        STEP="$1"
        shift
        STEP_ARGS=("$@")
        return 0
        ;;
      -*)
        die "unknown bootstrap option before step: $1"
        ;;
      *)
        STEP="$1"
        shift
        STEP_ARGS=("$@")
        return 0
        ;;
    esac
  done
}

validate_args() {
  [[ -n "$STEP" ]] || die "missing step"

  case "$PROFILE" in
    *[!A-Za-z0-9_-]*|"")
      die "invalid profile: $PROFILE"
      ;;
  esac

  case "$STEP" in
    *[!A-Za-z0-9_-]*|"")
      die "invalid step: $STEP"
      ;;
  esac
}

main() {
  parse_args "$@"
  validate_args

  local profile_dir="$SCRIPT_DIR/$PROFILE"
  local step_script="$profile_dir/scripts/$STEP.sh"

  [[ -d "$profile_dir" ]] || die "unknown profile: $PROFILE"
  [[ -x "$step_script" ]] || die "profile '$PROFILE' does not support step '$STEP'"

  log "Running profile=$PROFILE step=$STEP"
  "$step_script" "${STEP_ARGS[@]+"${STEP_ARGS[@]}"}"
}

main "$@"
