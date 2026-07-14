#!/usr/bin/env bash
set -u

MODE="${1:-}"
HOSTNAME=""
ERRORS=0
WARNINGS=0

usage() {
  cat <<'USAGE'
Usage: miair_doctor.sh mac|linux [--hostname <lan-ip>]

Checks MiAir installation state without modifying files.
USAGE
}

if [ -z "$MODE" ] || [ "$MODE" = "-h" ] || [ "$MODE" = "--help" ]; then
  usage
  exit 0
fi

shift
while [ "$#" -gt 0 ]; do
  case "$1" in
    --hostname)
      HOSTNAME="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

ok() { printf '[OK] %s\n' "$*"; }
warn() { WARNINGS=$((WARNINGS + 1)); printf '[WARN] %s\n' "$*"; }
fail() { ERRORS=$((ERRORS + 1)); printf '[FAIL] %s\n' "$*"; }

plist_value() {
  plist="$1"
  key="$2"
  /usr/libexec/PlistBuddy -c "Print $key" "$plist" 2>/dev/null || true
}

check_port() {
  port="$1"
  if command -v lsof >/dev/null 2>&1; then
    if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      ok "TCP port $port is listening"
    else
      warn "TCP port $port is not listening"
    fi
  else
    warn "lsof is not available, skipped port $port check"
  fi
}

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

selected_mac_endpoint() {
  category="$1"
  while IFS="$(printf '\t')" read -r iface port; do
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
  done <<EOF_PORTS
$(hardware_ports)
EOF_PORTS
  return 1
}

preferred_mac_endpoint() {
  endpoint="$(selected_mac_endpoint wired || true)"
  if [ -n "$endpoint" ]; then
    printf '%s\n' "$endpoint"
    return 0
  fi

  endpoint="$(selected_mac_endpoint wifi || true)"
  if [ -n "$endpoint" ]; then
    printf '%s\n' "$endpoint"
    return 0
  fi

  return 1
}

describe_endpoint() {
  endpoint="$1"
  ip="${endpoint%%$(printf '\t')*}"
  rest="${endpoint#*$(printf '\t')}"
  iface="${rest%%$(printf '\t')*}"
  rest="${rest#*$(printf '\t')}"
  port="${rest%%$(printf '\t')*}"
  category="${rest##*$(printf '\t')}"
  printf '%s on %s (%s, %s)' "$ip" "$iface" "$port" "$category"
}

case "$MODE" in
  mac)
    SRC_DIR="${MIAIR_HOME:-$HOME/.local/share/miair}/src"
    VENV_DIR="${MIAIR_HOME:-$HOME/.local/share/miair}/venv"
    BIN_DIR="${MIAIR_HOME:-$HOME/.local/share/miair}/bin"
    SHARED_AGENT_PYTHON_BIN="$HOME/.local/share/agent-dotfiles/python/bin/python"
    CORE_BIN="$BIN_DIR/miair-core"
    WATCHER_BIN="$BIN_DIR/miair-watch"
    OLD_CORE_BIN="$BIN_DIR/MiAir"
    OLD_WATCHER_BIN="$BIN_DIR/miair-ip-watch"
    WRAPPER_BIN="$VENV_DIR/bin/miair-macos-wrapper"
    CONF_DIR="${MIAIR_CONF:-$HOME/.config/miair}"
    STATE_DIR="${MIAIR_STATE:-$HOME/.local/state/miair}"
    PLIST="$HOME/Library/LaunchAgents/com.user.miair-core.plist"
    WATCHER_PLIST="$HOME/Library/LaunchAgents/com.user.miair-watch.plist"
    OLD_PLIST="$HOME/Library/LaunchAgents/com.user.miair.plist"
    OLD_WATCHER_PLIST="$HOME/Library/LaunchAgents/com.user.miair-ip-watch.plist"

    [ "$(uname -s)" = "Darwin" ] && ok "running on macOS" || fail "not running on macOS"
    [ -n "$HOSTNAME" ] && ok "expected LAN IP: $HOSTNAME" || warn "no expected LAN IP provided"

    if command -v networksetup >/dev/null 2>&1 && command -v ipconfig >/dev/null 2>&1; then
      if endpoint="$(preferred_mac_endpoint || true)" && [ -n "$endpoint" ]; then
        ok "selected macOS LAN IP: $(describe_endpoint "$endpoint")"
      else
        warn "could not select a macOS LAN IP from hardware ports"
      fi
    else
      warn "networksetup or ipconfig is missing, skipped macOS LAN IP selection check"
    fi

    command -v brew >/dev/null 2>&1 && ok "Homebrew found" || fail "Homebrew missing"
    for formula in uv ffmpeg portaudio; do
      if command -v brew >/dev/null 2>&1 && brew list --formula "$formula" >/dev/null 2>&1; then
        ok "brew formula installed: $formula"
      else
        warn "brew formula missing: $formula"
      fi
    done
    command -v uv >/dev/null 2>&1 && ok "uv found on PATH" || warn "uv not found on PATH"
    [ -x "$SHARED_AGENT_PYTHON_BIN" ] && ok "shared agent Python exists: $SHARED_AGENT_PYTHON_BIN" || fail "shared agent Python missing: $SHARED_AGENT_PYTHON_BIN"

    [ -d "$SRC_DIR/.git" ] && ok "source exists: $SRC_DIR" || warn "source missing: $SRC_DIR"
    [ -x "$VENV_DIR/bin/python" ] && ok "venv python exists: $VENV_DIR/bin/python" || warn "venv missing: $VENV_DIR"
    if [ -x "$VENV_DIR/bin/python" ]; then
      VENV_REALPATH="$("$VENV_DIR/bin/python" - <<'PY'
import os
import sys

print(os.path.realpath(sys.executable))
PY
)"
      EXPECTED_VENV_PYTHON="$(VENV_DIR="$VENV_DIR" "$VENV_DIR/bin/python" - <<'PY'
import os
from pathlib import Path

print(Path(os.environ["VENV_DIR"]).joinpath("bin", "python").absolute())
PY
)"
      if [ -x "$SHARED_AGENT_PYTHON_BIN" ]; then
        if [ "$VENV_REALPATH" = "$EXPECTED_VENV_PYTHON" ]; then
          ok "MiAir venv Python is copied from shared agent Python: $VENV_REALPATH"
        else
          warn "MiAir venv Python resolves outside the venv: $VENV_REALPATH"
        fi
      else
        fail "shared agent Python missing: $SHARED_AGENT_PYTHON_BIN"
      fi
    fi
    [ -x "$CORE_BIN" ] && ok "launchd-visible core executable exists: $CORE_BIN" || warn "launchd-visible core executable missing: $CORE_BIN"
    [ -x "$WATCHER_BIN" ] && ok "launchd-visible watcher executable exists: $WATCHER_BIN" || warn "launchd-visible watcher executable missing: $WATCHER_BIN"
    [ -x "$WRAPPER_BIN" ] && ok "MiAir macOS wrapper exists: $WRAPPER_BIN" || warn "MiAir macOS wrapper missing: $WRAPPER_BIN"
    [ -d "$CONF_DIR" ] && ok "config dir exists: $CONF_DIR" || warn "config dir missing: $CONF_DIR"
    [ -d "$STATE_DIR" ] && ok "state dir exists: $STATE_DIR" || warn "state dir missing: $STATE_DIR"
    [ -f "$PLIST" ] && ok "launchd plist exists: $PLIST" || warn "launchd plist missing: $PLIST"
    [ -f "$WATCHER_PLIST" ] && ok "IP watcher launchd plist exists: $WATCHER_PLIST" || warn "IP watcher launchd plist missing: $WATCHER_PLIST"
    [ ! -f "$OLD_PLIST" ] && ok "legacy core plist absent" || warn "legacy core plist still exists: $OLD_PLIST"
    [ ! -f "$OLD_WATCHER_PLIST" ] && ok "legacy watcher plist absent" || warn "legacy watcher plist still exists: $OLD_WATCHER_PLIST"
    [ ! -e "$OLD_CORE_BIN" ] && ok "legacy core executable absent" || warn "legacy core executable still exists: $OLD_CORE_BIN"
    [ ! -e "$OLD_WATCHER_BIN" ] && ok "legacy watcher executable absent" || warn "legacy watcher executable still exists: $OLD_WATCHER_BIN"

    if [ -f "$PLIST" ]; then
      PLIST_HOSTNAME="$(plist_value "$PLIST" ':ProgramArguments:4')"
      PLIST_ENV_HOSTNAME="$(plist_value "$PLIST" ':EnvironmentVariables:MIAIR_HOSTNAME')"
      [ -n "$PLIST_HOSTNAME" ] && ok "plist --hostname: $PLIST_HOSTNAME" || warn "plist --hostname missing"
      [ -n "$PLIST_ENV_HOSTNAME" ] && ok "plist MIAIR_HOSTNAME: $PLIST_ENV_HOSTNAME" || warn "plist MIAIR_HOSTNAME missing"
    fi

    if launchctl print "gui/$(id -u)/com.user.miair-core" >/dev/null 2>&1; then
      ok "launchd core job is loaded"
    else
      warn "launchd core job is not loaded"
    fi
    if launchctl print "gui/$(id -u)/com.user.miair-watch" >/dev/null 2>&1; then
      ok "IP watcher launchd job is loaded"
    else
      warn "IP watcher launchd job is not loaded"
    fi
    if launchctl print "gui/$(id -u)/com.user.miair" >/dev/null 2>&1; then
      warn "legacy core launchd job is still loaded"
    else
      ok "legacy core launchd job is not loaded"
    fi
    if launchctl print "gui/$(id -u)/com.user.miair-ip-watch" >/dev/null 2>&1; then
      warn "legacy IP watcher launchd job is still loaded"
    else
      ok "legacy IP watcher launchd job is not loaded"
    fi
    check_port 8300
    ;;

  linux)
    SRC_DIR="/opt/miair/src"
    CONF_DIR="/opt/miair/conf"
    [ "$(uname -s)" = "Linux" ] && ok "running on Linux" || fail "not running on Linux"
    [ -n "$HOSTNAME" ] && ok "expected LAN IP: $HOSTNAME" || warn "no expected LAN IP provided"
    command -v docker >/dev/null 2>&1 && ok "Docker found" || fail "Docker missing"
    [ -d "$SRC_DIR/.git" ] && ok "source exists: $SRC_DIR" || warn "source missing: $SRC_DIR"
    [ -d "$CONF_DIR" ] && ok "config dir exists: $CONF_DIR" || warn "config dir missing: $CONF_DIR"
    if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qx 'miair'; then
      ok "container miair is running"
    else
      warn "container miair is not running"
    fi
    check_port 8300
    ;;

  *)
    echo "Unknown mode: $MODE" >&2
    usage >&2
    exit 2
    ;;
esac

if [ "$ERRORS" -gt 0 ]; then
  printf '[FAIL] MiAir doctor failed with %s error(s), %s warning(s)\n' "$ERRORS" "$WARNINGS" >&2
  exit 1
fi

printf '[OK] MiAir doctor passed with %s warning(s)\n' "$WARNINGS"
