#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: master/bootstrap/bootstrap.sh <step> [options]

Steps:
  all                 Run install, links, then verify.
  install             Install packages and managed runtimes.
  links               Link profile-managed config into the home directory.
  verify              Check profile package files, links, and runtime tools.

Run a step with -h or --help for step-specific options.
EOF
}

die() {
  printf '[master:bootstrap] error: %s\n' "$*" >&2
  exit 1
}

case "${1:-}" in
  -h|--help|"")
    usage
    [[ "${1:-}" == "" ]] && exit 1 || exit 0
    ;;
esac

STEP="$1"
shift
SCRIPT="$SCRIPT_DIR/scripts/$STEP.sh"
[[ -x "$SCRIPT" ]] || die "unknown or non-executable step: $STEP"
exec "$SCRIPT" "$@"
