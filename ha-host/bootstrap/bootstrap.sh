#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: ha-host/bootstrap/bootstrap.sh <step> [options]

Steps:
  audit               Print the HA host bootstrap policy.
  install             Install HA host packages, runtimes, and power policy.
  links               Link profile-managed config into the home directory.
  verify              Check HA host readiness and orchestrator doctor.

Run a step with -h or --help for step-specific options.
EOF
}

die() {
  printf '[ha-host:bootstrap] error: %s\n' "$*" >&2
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
