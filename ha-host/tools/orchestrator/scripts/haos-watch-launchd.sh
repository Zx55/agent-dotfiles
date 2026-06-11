#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-/usr/bin/python3}"
ORCHESTRATOR_SRC="${ORCHESTRATOR_SRC:-/usr/local/libexec/agent-dotfiles/orchestrator/src}"
HA_HOST_DIR="${HA_HOST_DIR:-$HOME/.ha_host}"
VM_NAME="${VM_NAME:-HAOS-17.3}"
HAOS_HOST_ALIAS="${HAOS_HOST_ALIAS:-haos}"
HAOS_INTERFACE="${HAOS_INTERFACE:-default}"
GUEST_DEVICE="${GUEST_DEVICE:-enp0s1}"
APPLY_GATEWAY="${APPLY_GATEWAY:-1}"
APPLY_BRIDGE="${APPLY_BRIDGE:-1}"
HA_WATCH_APPLY_VM_RESTART="${HA_WATCH_APPLY_VM_RESTART:-1}"
HA_WATCH_ALLOW_UTM_APP_RESTART="${HA_WATCH_ALLOW_UTM_APP_RESTART:-0}"
HA_WATCH_RESTART_AFTER_FAILURES="${HA_WATCH_RESTART_AFTER_FAILURES:-3}"
HA_WATCH_RESTART_COOLDOWN_SECONDS="${HA_WATCH_RESTART_COOLDOWN_SECONDS:-1800}"
FORCE_BRIDGE_RESTART="${FORCE_BRIDGE_RESTART:-1}"
UTM_CONFIG_PATH="${UTM_CONFIG_PATH:-}"
WAIT_SECONDS="${WAIT_SECONDS:-60}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"

mkdir -p "$HA_HOST_DIR"

export PYTHONPATH="$ORCHESTRATOR_SRC${PYTHONPATH:+:$PYTHONPATH}"
args=(--vm-name "$VM_NAME"
  --host-alias "$HAOS_HOST_ALIAS"
  --haos-interface "$HAOS_INTERFACE"
  --guest-device "$GUEST_DEVICE"
  --wait-seconds "$WAIT_SECONDS"
  --sleep-seconds "$SLEEP_SECONDS"
  --state-path "$HA_HOST_DIR/state.json"
)

if [[ -n "$UTM_CONFIG_PATH" ]]; then
  args+=(--utm-config-path "$UTM_CONFIG_PATH")
fi

if [[ "$APPLY_GATEWAY" == "1" ]]; then
  args+=(--apply-gateway)
else
  args+=(--no-apply-gateway)
fi

if [[ "$APPLY_BRIDGE" == "1" ]]; then
  args+=(--apply-bridge)
else
  args+=(--no-apply-bridge)
fi

if [[ "$HA_WATCH_APPLY_VM_RESTART" == "1" ]]; then
  args+=(--apply-vm-restart)
else
  args+=(--no-apply-vm-restart)
fi

if [[ "$HA_WATCH_ALLOW_UTM_APP_RESTART" == "1" ]]; then
  args+=(--allow-utm-app-restart)
else
  args+=(--no-allow-utm-app-restart)
fi

args+=(--restart-after-failures "$HA_WATCH_RESTART_AFTER_FAILURES"
  --restart-cooldown-seconds "$HA_WATCH_RESTART_COOLDOWN_SECONDS"
)

if [[ "$FORCE_BRIDGE_RESTART" == "1" ]]; then
  args+=(--force-bridge-restart)
else
  args+=(--no-force-bridge-restart)
fi

exec "$PYTHON" -m ha_host_orchestrator.entrypoints.haos_watch "${args[@]}"
