#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-/usr/bin/python3}"
ORCHESTRATOR_SRC="${ORCHESTRATOR_SRC:-/usr/local/libexec/agent-dotfiles/orchestrator/src}"
HA_HOST_DIR="${HA_HOST_DIR:-$HOME/.ha_host}"
VM_NAME="${VM_NAME:-HAOS-17.3}"
WAIT_SECONDS="${WAIT_SECONDS:-180}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"

mkdir -p "$HA_HOST_DIR"

export PYTHONPATH="$ORCHESTRATOR_SRC${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" -m ha_host_orchestrator.entrypoints.haos_start \
  --vm-name "$VM_NAME" \
  --wait-seconds "$WAIT_SECONDS" \
  --sleep-seconds "$SLEEP_SECONDS" \
  --state-path "$HA_HOST_DIR/state.json"
