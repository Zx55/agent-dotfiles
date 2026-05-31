#!/usr/bin/env bash
set -euo pipefail

LABEL="com.user.miair-core"
PLIST="$HOME/Library/LaunchAgents/com.user.miair-core.plist"
RESTART_SERVICE=1
VERBOSE=0

usage() {
  cat <<'USAGE'
Usage: miair_macos_ip_watch.sh [options]

Checks the preferred macOS LAN IP for MiAir and restarts the launchd service
when the plist hostname no longer matches.

Options:
  --plist <path>              MiAir launchd plist path
  --label <launchd-label>     MiAir launchd label
  --no-restart                Update plist only
  --verbose                   Print no-change status
USAGE
}

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --plist)
      PLIST="${2:-}"
      shift 2
      ;;
    --label)
      LABEL="${2:-}"
      shift 2
      ;;
    --no-restart)
      RESTART_SERVICE=0
      shift
      ;;
    --verbose)
      VERBOSE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

valid_lan_ip() {
  case "${1:-}" in
    ""|0.0.0.0|127.*|169.254.*)
      return 1
      ;;
    *)
      return 0
      ;;
  esac
}

interface_ip() {
  ipconfig getifaddr "$1" 2>/dev/null || true
}

hardware_ports() {
  networksetup -listallhardwareports 2>/dev/null | awk '
    /^Hardware Port: / { port = substr($0, 16) }
    /^Device: / {
      device = substr($0, 9)
      if (device != "") {
        printf "%s\t%s\n", device, port
      }
    }
  '
}

lowercase() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

is_wifi_port() {
  case "$(lowercase "$1")" in
    *wi-fi*|*wifi*|*airport*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_ignored_wired_port() {
  local iface port_lower
  iface="$1"
  port_lower="$(lowercase "$2")"

  case "$iface" in
    lo*|bridge*|awdl*|llw*|utun*|vmenet*|gif*|stf*|ap*)
      return 0
      ;;
  esac

  case "$port_lower" in
    *bridge*|thunderbolt\ [0-9]*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

preferred_endpoint() {
  local category iface port ip
  for category in wired wifi; do
    while IFS=$'\t' read -r iface port; do
      [ -n "$iface" ] || continue
      ip="$(interface_ip "$iface")"
      valid_lan_ip "$ip" || continue

      case "$category" in
        wired)
          is_wifi_port "$port" && continue
          is_ignored_wired_port "$iface" "$port" && continue
          ;;
        wifi)
          is_wifi_port "$port" || continue
          ;;
      esac

      printf '%s\t%s\t%s\t%s\n' "$ip" "$iface" "$port" "$category"
      return 0
    done < <(hardware_ports)
  done
  return 1
}

plist_value() {
  /usr/libexec/PlistBuddy -c "Print $1" "$PLIST" 2>/dev/null || true
}

set_plist_value() {
  /usr/libexec/PlistBuddy -c "Set $1 $2" "$PLIST"
}

restart_launchd_service() {
  local domain
  domain="gui/$(id -u)"
  launchctl bootout "$domain" "$PLIST" >/dev/null 2>&1 || true
  launchctl bootstrap "$domain" "$PLIST"
  launchctl enable "$domain/$LABEL" >/dev/null 2>&1 || true
  launchctl kickstart -k "$domain/$LABEL" >/dev/null 2>&1 || true
}

if [ "$(uname -s)" != "Darwin" ]; then
  log "not macOS, skipping MiAir IP watch"
  exit 0
fi

if [ ! -f "$PLIST" ]; then
  log "MiAir plist missing: $PLIST"
  exit 0
fi

if ! command -v networksetup >/dev/null 2>&1; then
  log "networksetup is unavailable, skipping MiAir IP watch"
  exit 0
fi

if ! command -v ipconfig >/dev/null 2>&1; then
  log "ipconfig is unavailable, skipping MiAir IP watch"
  exit 0
fi

endpoint="$(preferred_endpoint || true)"
if [ -z "$endpoint" ]; then
  log "no usable LAN IP found on macOS hardware ports"
  exit 0
fi

desired_ip="${endpoint%%$'\t'*}"
rest="${endpoint#*$'\t'}"
selected_iface="${rest%%$'\t'*}"
rest="${rest#*$'\t'}"
selected_port="${rest%%$'\t'*}"
selected_kind="${rest##*$'\t'}"
selected_label="$desired_ip on $selected_iface ($selected_port, $selected_kind)"

current_arg_ip="$(plist_value ':ProgramArguments:4')"
current_env_ip="$(plist_value ':EnvironmentVariables:MIAIR_HOSTNAME')"

if [ "$current_arg_ip" = "$desired_ip" ] && [ "$current_env_ip" = "$desired_ip" ]; then
  if [ "$VERBOSE" -eq 1 ]; then
    log "MiAir hostname already matches $selected_label"
  fi
  exit 0
fi

set_plist_value ':ProgramArguments:4' "$desired_ip"
set_plist_value ':EnvironmentVariables:MIAIR_HOSTNAME' "$desired_ip"
plutil -lint "$PLIST" >/dev/null

log "updated MiAir hostname from arg=$current_arg_ip env=$current_env_ip to $selected_label"

if [ "$RESTART_SERVICE" -eq 1 ]; then
  restart_launchd_service
  log "restarted $LABEL with hostname $desired_ip"
fi
