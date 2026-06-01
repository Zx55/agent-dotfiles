#!/usr/bin/env bash
set -u

TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="/usr/local/libexec/agent-dotfiles/orchestrator"
HA_HOST_DIR="${HA_HOST_DIR:-$HOME/.ha_host}"
PYTHON_BIN="${PYTHON:-}"
ROOT_SERVICE_PYTHON="/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python"
VM_NAME="${VM_NAME:-HAOS-17.3}"
UTM_CONFIG_PATH="${UTM_CONFIG_PATH:-}"
ERRORS=0
WARNINGS=0

ok() { printf '[orchestrator-doctor] ok: %s\n' "$*"; }
warn() { WARNINGS=$((WARNINGS + 1)); printf '[orchestrator-doctor] warning: %s\n' "$*" >&2; }
fail() { ERRORS=$((ERRORS + 1)); printf '[orchestrator-doctor] error: %s\n' "$*" >&2; }

check_file() {
  [ -f "$1" ] && ok "file exists: $1" || fail "file missing: $1"
}

check_executable() {
  [ -x "$1" ] && ok "executable exists: $1" || fail "executable missing: $1"
}

check_plist() {
  local plist="$1"
  if [ -f "$plist" ]; then
    if plutil -lint "$plist" >/dev/null 2>&1; then
      ok "plist valid: $plist"
    else
      fail "plist invalid: $plist"
    fi
  else
    warn "plist not installed: $plist"
  fi
}

check_launchctl() {
  local domain="$1"
  local label="$2"
  if launchctl print "$domain/$label" >/dev/null 2>&1; then
    ok "launchd job loaded: $domain/$label"
  else
    warn "launchd job not loaded: $domain/$label"
  fi
}

check_file "$TOOL_DIR/pyproject.toml"
check_executable "$TOOL_DIR/scripts/ha-host-startup-launchd.sh"
check_executable "$TOOL_DIR/scripts/ha-host-watch-launchd.sh"
check_executable "$TOOL_DIR/scripts/haos-start-launchd.sh"
check_executable "$TOOL_DIR/scripts/haos-watch-launchd.sh"

if [ -z "$PYTHON_BIN" ]; then
  PYTHON_BIN="$ROOT_SERVICE_PYTHON"
fi

ok "orchestrator Python: $PYTHON_BIN"
if [ "$PYTHON_BIN" = "$ROOT_SERVICE_PYTHON" ]; then
  if [ -x "$PYTHON_BIN" ]; then
    ok "root-owned HA host service Python in use"
  else
    fail "root-owned HA host service Python missing or not executable: $PYTHON_BIN"
  fi
else
  warn "orchestrator Python is not the HA host service Python: $PYTHON_BIN"
fi

if [ -x "$PYTHON_BIN" ] && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$TOOL_DIR/src" "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import ha_host_orchestrator.network
import ha_host_orchestrator.host
import ha_host_orchestrator.haos
PY
then
  ok "source package imports"
else
  fail "source package import failed"
fi

if [ -z "$UTM_CONFIG_PATH" ]; then
  UTM_CONFIG_PATH="$HOME/Library/Containers/com.utmapp.UTM/Data/Documents/$VM_NAME.utm/config.plist"
fi
if [ -f "$UTM_CONFIG_PATH" ]; then
  if [ -x "$PYTHON_BIN" ] && UTM_CONFIG_PATH="$UTM_CONFIG_PATH" "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import os
from pathlib import Path

config = Path(os.environ["UTM_CONFIG_PATH"])
probe = config.parent / ".orchestrator-permission-test"
try:
    config.read_bytes()
    probe.write_text("ok\n", encoding="utf-8")
finally:
    try:
        probe.unlink()
    except FileNotFoundError:
        pass
PY
  then
    ok "UTM config package readable/writable by orchestrator Python: $UTM_CONFIG_PATH"
  else
    warn "UTM config package is not readable/writable by orchestrator Python: $UTM_CONFIG_PATH"
    warn "automatic HAOS bridge repair may prompt for App Data access; run install or doctor interactively and allow the HA host service Python, or grant it Full Disk Access before relying on unattended recovery"
  fi
else
  warn "UTM config not found for permission preflight: $UTM_CONFIG_PATH"
fi

if [ -d "$INSTALL_DIR" ]; then
  ok "runtime copy exists: $INSTALL_DIR"
else
  warn "runtime copy missing: $INSTALL_DIR"
fi

check_plist "/Library/LaunchDaemons/com.user.ha-host-startup.plist"
check_plist "/Library/LaunchDaemons/com.user.ha-host-watch.plist"
check_plist "$HOME/Library/LaunchAgents/com.user.haos-start.plist"
check_plist "$HOME/Library/LaunchAgents/com.user.haos-watch.plist"

check_launchctl system com.user.ha-host-startup
check_launchctl system com.user.ha-host-watch
check_launchctl "gui/$(id -u)" com.user.haos-start
check_launchctl "gui/$(id -u)" com.user.haos-watch

if [ -f "$HA_HOST_DIR/state.json" ]; then
  ok "state file exists: $HA_HOST_DIR/state.json"
else
  warn "state file missing: $HA_HOST_DIR/state.json"
fi

if [ "$ERRORS" -gt 0 ]; then
  printf '[orchestrator-doctor] failed with %s error(s), %s warning(s)\n' "$ERRORS" "$WARNINGS" >&2
  exit 1
fi

printf '[orchestrator-doctor] passed with %s warning(s)\n' "$WARNINGS"
