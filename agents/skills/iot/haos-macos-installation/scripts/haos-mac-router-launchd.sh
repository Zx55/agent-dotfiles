#!/usr/bin/env bash
set -euo pipefail

TOOL_PATH="${TOOL_PATH:-/usr/local/libexec/agent-dotfiles/haos-mac-router/haos-mac-router.sh}"
ROUTE_TARGET="${ROUTE_TARGET:-1.1.1.1}"
REQUIRE_UTUN="${REQUIRE_UTUN:-1}"
WAIT_SECONDS="${WAIT_SECONDS:-120}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"

log() {
  printf '[haos-mac-router-launchd] %s\n' "$*"
}

route_interface() {
  route -n get "$ROUTE_TARGET" 2>/dev/null | awk '/interface: / {print $2; exit}'
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    log "missing required environment variable: $name"
    exit 1
  fi
}

if [[ "$(id -u)" -ne 0 ]]; then
  log "must run as root"
  exit 1
fi

if [[ ! -x "$TOOL_PATH" ]]; then
  log "router tool is not executable: $TOOL_PATH"
  exit 1
fi

require_env HAOS_IP
require_env HAOS_PREFIX
require_env HAOS_INTERFACE
require_env LAN_INTERFACE
require_env MAC_LAN_IP
require_env DNS_SERVER

deadline=$((SECONDS + WAIT_SECONDS))
egress_interface=""

while true; do
  egress_interface="$(route_interface || true)"

  if [[ "$REQUIRE_UTUN" != "1" ]]; then
    [[ -n "$egress_interface" ]] && break
  elif [[ "$egress_interface" == utun* ]]; then
    break
  fi

  if (( SECONDS >= deadline )); then
    log "route to $ROUTE_TARGET is '${egress_interface:-unavailable}', expected utun; retry later"
    exit 75
  fi

  sleep "$SLEEP_SECONDS"
done

log "applying HAOS Mac router with egress $egress_interface"
exec "$TOOL_PATH" apply \
  --haos-ip "$HAOS_IP" \
  --haos-prefix "$HAOS_PREFIX" \
  --haos-interface "$HAOS_INTERFACE" \
  --lan-interface "$LAN_INTERFACE" \
  --mac-lan-ip "$MAC_LAN_IP" \
  --egress-interface "$egress_interface" \
  --dns "$DNS_SERVER" \
  --yes
