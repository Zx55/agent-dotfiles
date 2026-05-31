#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALL_DIR="/usr/local/libexec/agent-dotfiles/orchestrator"
ROOT_START_TEMPLATE="$TOOL_DIR/templates/com.user.ha-host-startup.plist"
ROOT_WATCH_TEMPLATE="$TOOL_DIR/templates/com.user.ha-host-watch.plist"
USER_START_TEMPLATE="$TOOL_DIR/templates/com.user.haos-start.plist"
USER_WATCH_TEMPLATE="$TOOL_DIR/templates/com.user.haos-watch.plist"
ROOT_START_PLIST="/Library/LaunchDaemons/com.user.ha-host-startup.plist"
ROOT_WATCH_PLIST="/Library/LaunchDaemons/com.user.ha-host-watch.plist"
USER_START_PLIST="$HOME/Library/LaunchAgents/com.user.haos-start.plist"
USER_WATCH_PLIST="$HOME/Library/LaunchAgents/com.user.haos-watch.plist"

ROUTE_TARGET="1.1.1.1"
WAIT_SECONDS="600"
USER_WAIT_SECONDS="180"
WATCH_WAIT_SECONDS="60"
WATCH_INTERVAL="300"
SLEEP_SECONDS="5"
SCAN="1"
NO_REQUIRE_UTUN="0"
VM_NAME="HAOS-17.3"
HAOS_HOST_ALIAS="haos"
HAOS_INTERFACE="default"
GUEST_DEVICE="enp0s1"
APPLY_GATEWAY="1"
APPLY_BRIDGE="1"
FORCE_BRIDGE_RESTART="1"
UTM_CONFIG_PATH=""
PYTHON_BIN="${PYTHON:-}"
DRY_RUN="0"
LOAD_NOW="0"
HA_HOST_DIR="${HA_HOST_DIR:-$HOME/.ha_host}"
REGISTRY_PATH="${MAC_ROUTER_REGISTRY:-$HOME/.router/device.json}"
ROOT_SERVICE_PYTHON_BIN="/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python"
SERVICE_PYTHON_BIN="${HA_HOST_SERVICE_PYTHON:-}"
UTM_PERMISSION_PREFLIGHT="1"

log() {
  printf '[orchestrator-install] %s\n' "$*"
}

die() {
  printf '[orchestrator-install] error: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  install-launchd.sh [options]

Options:
  --route-target IP       Egress route probe target. Default: 1.1.1.1.
  --wait-seconds N        Root startup wait timeout. Default: 600.
  --user-wait-seconds N   User HAOS startup wait timeout. Default: 180.
  --watch-wait-seconds N  Watch entrypoint wait timeout. Default: 60.
  --watch-interval N      Watch launchd interval. Default: 300.
  --sleep-seconds N       Poll interval. Default: 5.
  --vm-name NAME          UTM VM name. Default: HAOS-17.3.
  --haos-host-alias NAME  SSH host alias for HAOS. Default: haos.
  --haos-interface NAME   HAOS network connection/interface for gateway updates. Default: default.
  --guest-device NAME     HAOS Linux network device for runtime route repair. Default: enp0s1.
  --no-haos-gateway-apply Only report HAOS gateway drift instead of applying it.
  --no-utm-bridge-apply   Only report UTM bridge drift instead of applying it.
  --no-force-bridge-restart
                          Do not use UTM force stop if graceful bridge restart times out.
  --utm-config-path PATH  UTM config.plist path. Default: ~/Library/.../<vm-name>.utm/config.plist.
  --python PATH           Explicit Python 3.11+ binary for launchd jobs. Default: root-owned HA host service Python.
  --no-scan               Do not scan registry targets during host router apply.
  --no-require-utun       Do not require route target to use utun.
  --load-now              Bootstrap all launchd jobs after installing.
  --registry PATH         Device registry path. Default: ~/.router/device.json.
  --ha-host-dir PATH      Log and state dir. Default: ~/.ha_host.
  --skip-utm-permission-preflight
                          Do not preflight read/write access to the UTM VM config package.
  --dry-run               Render and validate files without installing.
  -h, --help              Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --route-target)
      ROUTE_TARGET="${2:-}"
      shift 2
      ;;
    --wait-seconds)
      WAIT_SECONDS="${2:-}"
      shift 2
      ;;
    --user-wait-seconds)
      USER_WAIT_SECONDS="${2:-}"
      shift 2
      ;;
    --watch-wait-seconds)
      WATCH_WAIT_SECONDS="${2:-}"
      shift 2
      ;;
    --watch-interval)
      WATCH_INTERVAL="${2:-}"
      shift 2
      ;;
    --sleep-seconds)
      SLEEP_SECONDS="${2:-}"
      shift 2
      ;;
    --vm-name)
      VM_NAME="${2:-}"
      shift 2
      ;;
    --haos-host-alias)
      HAOS_HOST_ALIAS="${2:-}"
      shift 2
      ;;
    --haos-interface)
      HAOS_INTERFACE="${2:-}"
      shift 2
      ;;
    --guest-device)
      GUEST_DEVICE="${2:-}"
      shift 2
      ;;
    --no-haos-gateway-apply)
      APPLY_GATEWAY="0"
      shift
      ;;
    --no-utm-bridge-apply)
      APPLY_BRIDGE="0"
      shift
      ;;
    --no-force-bridge-restart)
      FORCE_BRIDGE_RESTART="0"
      shift
      ;;
    --utm-config-path)
      UTM_CONFIG_PATH="${2:-}"
      shift 2
      ;;
    --python)
      PYTHON_BIN="${2:-}"
      shift 2
      ;;
    --no-scan)
      SCAN="0"
      shift
      ;;
    --no-require-utun)
      NO_REQUIRE_UTUN="1"
      shift
      ;;
    --load-now)
      LOAD_NOW="1"
      shift
      ;;
    --registry)
      REGISTRY_PATH="${2:-}"
      shift 2
      ;;
    --ha-host-dir)
      HA_HOST_DIR="${2:-}"
      shift 2
      ;;
    --skip-utm-permission-preflight)
      UTM_PERMISSION_PREFLIGHT="0"
      shift
      ;;
    --dry-run)
      DRY_RUN="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -n "$SERVICE_PYTHON_BIN" ]]; then
    if [[ -x "$SERVICE_PYTHON_BIN" ]]; then
      PYTHON_BIN="$SERVICE_PYTHON_BIN"
    else
      die "explicit HA_HOST_SERVICE_PYTHON is not executable: $SERVICE_PYTHON_BIN"
    fi
  elif [[ -x "$ROOT_SERVICE_PYTHON_BIN" ]]; then
    PYTHON_BIN="$ROOT_SERVICE_PYTHON_BIN"
  else
    die "root-owned HA host service Python missing: $ROOT_SERVICE_PYTHON_BIN. Run bootstrap/bootstrap.sh --profile ha_host install first."
  fi
fi

if ! "$PYTHON_BIN" - <<'PY' >/dev/null
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
then
  die "Python 3.11+ is required: $PYTHON_BIN"
fi

utm_config_path() {
  if [[ -n "$UTM_CONFIG_PATH" ]]; then
    printf '%s\n' "$UTM_CONFIG_PATH"
  else
    printf '%s\n' "$HOME/Library/Containers/com.utmapp.UTM/Data/Documents/$VM_NAME.utm/config.plist"
  fi
}

preflight_utm_permission() {
  [[ "$UTM_PERMISSION_PREFLIGHT" == "1" ]] || return 0

  local config_path vm_dir
  config_path="$(utm_config_path)"
  vm_dir="$(dirname "$config_path")"
  if [[ ! -e "$config_path" ]]; then
    log "UTM config not found, skipping permission preflight: $config_path"
    return 0
  fi

  log "preflighting UTM app-data read/write access with: $PYTHON_BIN"
  if UTM_CONFIG_PATH="$config_path" "$PYTHON_BIN" - <<'PY'
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
    log "UTM app-data read/write preflight passed: $vm_dir"
  else
    die "UTM app-data preflight failed for $vm_dir. Allow the macOS prompt for the HA host service Python, or grant it Full Disk Access, then rerun install."
  fi
}

render_template() {
  local src="$1"
  local dst="$2"
  cp "$src" "$dst"

  local name value
  for name in ROUTE_TARGET WAIT_SECONDS USER_WAIT_SECONDS WATCH_WAIT_SECONDS WATCH_INTERVAL SLEEP_SECONDS SCAN NO_REQUIRE_UTUN VM_NAME HAOS_HOST_ALIAS HAOS_INTERFACE GUEST_DEVICE APPLY_GATEWAY APPLY_BRIDGE FORCE_BRIDGE_RESTART UTM_CONFIG_PATH PYTHON_BIN HA_HOST_DIR REGISTRY_PATH; do
    value="${!name}"
    PLACEHOLDER="__${name}__" VALUE="$value" perl -0pi -e 's/\Q$ENV{PLACEHOLDER}\E/$ENV{VALUE}/g' "$dst"
  done

  if grep -q '__[A-Z0-9_][A-Z0-9_]*__' "$dst"; then
    die "unresolved placeholders in $dst"
  fi
}

for script in \
  "$TOOL_DIR/scripts/ha-host-startup-launchd.sh" \
  "$TOOL_DIR/scripts/ha-host-watch-launchd.sh" \
  "$TOOL_DIR/scripts/haos-start-launchd.sh" \
  "$TOOL_DIR/scripts/haos-watch-launchd.sh"; do
  bash -n "$script"
done

root_start_rendered="$(mktemp)"
root_watch_rendered="$(mktemp)"
user_start_rendered="$(mktemp)"
user_watch_rendered="$(mktemp)"
trap 'rm -f "$root_start_rendered" "$root_watch_rendered" "$user_start_rendered" "$user_watch_rendered"' EXIT

render_template "$ROOT_START_TEMPLATE" "$root_start_rendered"
render_template "$ROOT_WATCH_TEMPLATE" "$root_watch_rendered"
render_template "$USER_START_TEMPLATE" "$user_start_rendered"
render_template "$USER_WATCH_TEMPLATE" "$user_watch_rendered"

plutil -lint "$root_start_rendered" "$root_watch_rendered" "$user_start_rendered" "$user_watch_rendered" >/dev/null

if [[ "$DRY_RUN" == "1" ]]; then
  log "dry-run Python: $PYTHON_BIN"
  log "dry-run root startup plist: $root_start_rendered"
  cat "$root_start_rendered"
  log "dry-run root watch plist: $root_watch_rendered"
  cat "$root_watch_rendered"
  log "dry-run user HAOS startup plist: $user_start_rendered"
  cat "$user_start_rendered"
  log "dry-run user HAOS watch plist: $user_watch_rendered"
  cat "$user_watch_rendered"
  trap - EXIT
  exit 0
fi

preflight_utm_permission

sudo launchctl bootout system/com.user.ha-host-startup >/dev/null 2>&1 || true
sudo launchctl bootout system/com.user.ha-host-watch >/dev/null 2>&1 || true
launchctl bootout "gui/$(id -u)/com.user.haos-start" >/dev/null 2>&1 || true
launchctl bootout "gui/$(id -u)/com.user.haos-watch" >/dev/null 2>&1 || true

mkdir -p "$HA_HOST_DIR"
sudo rm -rf "$INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"
sudo cp -R "$TOOL_DIR/src" "$INSTALL_DIR/"
sudo cp "$TOOL_DIR/pyproject.toml" "$INSTALL_DIR/"
sudo cp "$TOOL_DIR/scripts/ha-host-startup-launchd.sh" "$TOOL_DIR/scripts/ha-host-watch-launchd.sh" "$TOOL_DIR/scripts/haos-start-launchd.sh" "$TOOL_DIR/scripts/haos-watch-launchd.sh" "$INSTALL_DIR/"
sudo chmod -R a+rX "$INSTALL_DIR"
sudo chmod +x "$INSTALL_DIR/ha-host-startup-launchd.sh" "$INSTALL_DIR/ha-host-watch-launchd.sh" "$INSTALL_DIR/haos-start-launchd.sh" "$INSTALL_DIR/haos-watch-launchd.sh" "$INSTALL_DIR/src/ha_host_orchestrator/mac_router/mac-router.sh"
sudo chown -R root:wheel "$INSTALL_DIR"

sudo cp "$root_start_rendered" "$ROOT_START_PLIST"
sudo cp "$root_watch_rendered" "$ROOT_WATCH_PLIST"
sudo chown root:wheel "$ROOT_START_PLIST" "$ROOT_WATCH_PLIST"
sudo chmod 644 "$ROOT_START_PLIST" "$ROOT_WATCH_PLIST"

mkdir -p "$HOME/Library/LaunchAgents"
cp "$user_start_rendered" "$USER_START_PLIST"
cp "$user_watch_rendered" "$USER_WATCH_PLIST"
chmod 644 "$USER_START_PLIST" "$USER_WATCH_PLIST"

log "installed root startup daemon: $ROOT_START_PLIST"
log "installed root watch daemon: $ROOT_WATCH_PLIST"
log "installed user HAOS startup agent: $USER_START_PLIST"
log "installed user HAOS watch agent: $USER_WATCH_PLIST"

if [[ "$LOAD_NOW" == "1" ]]; then
  sudo launchctl bootstrap system "$ROOT_START_PLIST"
  sudo launchctl bootstrap system "$ROOT_WATCH_PLIST"
  launchctl bootstrap "gui/$(id -u)" "$USER_START_PLIST"
  launchctl bootstrap "gui/$(id -u)" "$USER_WATCH_PLIST"
  log "bootstrapped launchd jobs"
fi
