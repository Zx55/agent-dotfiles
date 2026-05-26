#!/usr/bin/env bash
set -u

MODE="${1:-}"
HOSTNAME=""

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
warn() { printf '[WARN] %s\n' "$*"; }
fail() { printf '[FAIL] %s\n' "$*"; }

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

case "$MODE" in
  mac)
    SRC_DIR="${MIAIR_HOME:-$HOME/.local/share/miair}/src"
    VENV_DIR="${MIAIR_HOME:-$HOME/.local/share/miair}/venv"
    WRAPPER_BIN="$VENV_DIR/bin/miair-macos-wrapper"
    CONF_DIR="${MIAIR_CONF:-$HOME/.config/miair}"
    STATE_DIR="${MIAIR_STATE:-$HOME/.local/state/miair}"
    PLIST="$HOME/Library/LaunchAgents/com.user.miair.plist"

    [ "$(uname -s)" = "Darwin" ] && ok "running on macOS" || fail "not running on macOS"
    [ -n "$HOSTNAME" ] && ok "expected LAN IP: $HOSTNAME" || warn "no expected LAN IP provided"

    if command -v ipconfig >/dev/null 2>&1; then
      CURRENT_IP="$(ipconfig getifaddr en0 2>/dev/null || true)"
      [ -n "$CURRENT_IP" ] && ok "en0 IP: $CURRENT_IP" || warn "could not read en0 IP"
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

    [ -d "$SRC_DIR/.git" ] && ok "source exists: $SRC_DIR" || warn "source missing: $SRC_DIR"
    [ -x "$VENV_DIR/bin/python" ] && ok "venv python exists: $VENV_DIR/bin/python" || warn "venv missing: $VENV_DIR"
    [ -x "$WRAPPER_BIN" ] && ok "MiAir macOS wrapper exists: $WRAPPER_BIN" || warn "MiAir macOS wrapper missing: $WRAPPER_BIN"
    [ -d "$CONF_DIR" ] && ok "config dir exists: $CONF_DIR" || warn "config dir missing: $CONF_DIR"
    [ -d "$STATE_DIR" ] && ok "state dir exists: $STATE_DIR" || warn "state dir missing: $STATE_DIR"
    [ -f "$PLIST" ] && ok "launchd plist exists: $PLIST" || warn "launchd plist missing: $PLIST"

    if launchctl print "gui/$(id -u)/com.user.miair" >/dev/null 2>&1; then
      ok "launchd job is loaded"
    else
      warn "launchd job is not loaded"
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
