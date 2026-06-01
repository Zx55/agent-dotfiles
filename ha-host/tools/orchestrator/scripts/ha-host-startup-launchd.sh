#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-/usr/bin/python3}"
ORCHESTRATOR_SRC="${ORCHESTRATOR_SRC:-/usr/local/libexec/agent-dotfiles/orchestrator/src}"
HA_HOST_DIR="${HA_HOST_DIR:-$HOME/.ha_host}"
REGISTRY_PATH="${MAC_ROUTER_REGISTRY:-$HOME/.router/device.json}"
ROUTE_TARGET="${ROUTE_TARGET:-1.1.1.1}"
WAIT_SECONDS="${WAIT_SECONDS:-600}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"
SCAN="${SCAN:-1}"
NO_REQUIRE_UTUN="${NO_REQUIRE_UTUN:-0}"

mkdir -p "$HA_HOST_DIR"

args=(--registry "$REGISTRY_PATH"
  --route-target "$ROUTE_TARGET"
  --wait-seconds "$WAIT_SECONDS"
  --sleep-seconds "$SLEEP_SECONDS"
  --state-path "$HA_HOST_DIR/state.json"
)

if [[ "$SCAN" == "1" ]]; then
  args+=(--scan)
fi

if [[ "$NO_REQUIRE_UTUN" == "1" ]]; then
  args+=(--no-require-utun)
fi

export PYTHONPATH="$ORCHESTRATOR_SRC${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" -m ha_host_orchestrator.entrypoints.host_startup "${args[@]}"
