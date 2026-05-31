#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/KiriChen-Wind/MiAir.git"
REF="main"
HOSTNAME=""
LOAD_SERVICE=1

INSTALL_ROOT="${MIAIR_HOME:-$HOME/.local/share/miair}"
SRC_DIR="$INSTALL_ROOT/src"
VENV_DIR="$INSTALL_ROOT/venv"
BIN_DIR="$INSTALL_ROOT/bin"
ROOT_SERVICE_PYTHON_BIN="/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python"
SERVICE_PYTHON_BIN="${HA_HOST_SERVICE_PYTHON:-$ROOT_SERVICE_PYTHON_BIN}"
LAUNCHER="$BIN_DIR/miair-core"
IP_WATCHER="$BIN_DIR/miair-watch"
OLD_LAUNCHER="$BIN_DIR/MiAir"
OLD_IP_WATCHER="$BIN_DIR/miair-ip-watch"
CORE_LABEL="com.user.miair-core"
WATCH_LABEL="com.user.miair-watch"
OLD_CORE_LABEL="com.user.miair"
OLD_WATCH_LABEL="com.user.miair-ip-watch"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENTS_DIR="$(cd "$SKILL_DIR/../../.." && pwd)"
WRAPPER_SRC="$AGENTS_DIR/tools/miair-macos-wrapper"
WRAPPER_BIN="$VENV_DIR/bin/miair-macos-wrapper"
CONF_DIR="${MIAIR_CONF:-$HOME/.config/miair}"
STATE_DIR="${MIAIR_STATE:-$HOME/.local/state/miair}"
PLIST="$HOME/Library/LaunchAgents/$CORE_LABEL.plist"
WATCHER_PLIST="$HOME/Library/LaunchAgents/$WATCH_LABEL.plist"
OLD_PLIST="$HOME/Library/LaunchAgents/$OLD_CORE_LABEL.plist"
OLD_WATCHER_PLIST="$HOME/Library/LaunchAgents/$OLD_WATCH_LABEL.plist"

usage() {
  cat <<'USAGE'
Usage: install_macos_native.sh [--hostname <mac-lan-ip>] [--ref <git-ref>] [--no-load]

Installs MiAir natively on macOS with:
  source: ~/.local/share/miair/src
  venv:   ~/.local/share/miair/venv
  launcher: ~/.local/share/miair/bin/miair-core
  watcher: ~/.local/share/miair/bin/miair-watch
  wrapper: ~/.local/share/miair/venv/bin/miair-macos-wrapper
  config: ~/.config/miair
  logs:   ~/.local/state/miair
USAGE
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

detect_lan_endpoint() {
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

detect_lan_ip() {
  local endpoint
  endpoint="$(detect_lan_endpoint || true)"
  if [ -n "$endpoint" ]; then
    printf '%s\n' "${endpoint%%$'\t'*}"
    return 0
  fi
  return 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --hostname)
      HOSTNAME="${2:-}"
      shift 2
      ;;
    --ref)
      REF="${2:-}"
      shift 2
      ;;
    --no-load)
      LOAD_SERVICE=0
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

if [ -z "$HOSTNAME" ]; then
  HOSTNAME="$(detect_lan_ip || true)"
fi

if ! valid_lan_ip "$HOSTNAME"; then
  echo "A real LAN IP is required. Pass --hostname <mac-lan-ip> or connect a wired or Wi-Fi macOS hardware port." >&2
  exit 2
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required. Install Homebrew first." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required. Install git first." >&2
  exit 1
fi

for formula in ffmpeg portaudio; do
  if ! brew list --formula "$formula" >/dev/null 2>&1; then
    brew install "$formula"
  fi
done

if ! brew list --formula uv >/dev/null 2>&1; then
  brew install uv
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required but was not found on PATH after installation." >&2
  exit 1
fi

mkdir -p "$INSTALL_ROOT" "$BIN_DIR" "$CONF_DIR" "$STATE_DIR" "$(dirname "$PLIST")"

if [ "$SERVICE_PYTHON_BIN" != "$ROOT_SERVICE_PYTHON_BIN" ]; then
  echo "MiAir macOS native install requires the root-owned HA host service Python: $ROOT_SERVICE_PYTHON_BIN" >&2
  echo "Do not set HA_HOST_SERVICE_PYTHON for this installer." >&2
  exit 1
fi

if [ ! -x "$SERVICE_PYTHON_BIN" ]; then
  echo "Root-owned HA host service Python is missing: $SERVICE_PYTHON_BIN" >&2
  echo "Run bootstrap/bootstrap.sh --profile ha_host install first." >&2
  exit 1
fi

if [ -d "$SRC_DIR/.git" ]; then
  git -C "$SRC_DIR" fetch --tags origin
  git -C "$SRC_DIR" checkout "$REF"
  if [ "$REF" = "main" ]; then
    git -C "$SRC_DIR" pull --ff-only origin main
  fi
elif [ -e "$SRC_DIR" ]; then
  echo "Source path exists but is not a git checkout: $SRC_DIR" >&2
  exit 1
else
  git clone "$REPO_URL" "$SRC_DIR"
  git -C "$SRC_DIR" checkout "$REF"
fi

if [ -x "$SERVICE_PYTHON_BIN" ] && [ -x "$VENV_DIR/bin/python" ]; then
  venv_realpath="$("$VENV_DIR/bin/python" - <<'PY'
import os
import sys

print(os.path.realpath(sys.executable))
PY
)"
  expected_realpath="$(VENV_DIR="$VENV_DIR" "$SERVICE_PYTHON_BIN" - <<'PY'
import os
from pathlib import Path

print(Path(os.environ["VENV_DIR"]).joinpath("bin", "python").absolute())
PY
)"
  if [ "$venv_realpath" != "$expected_realpath" ]; then
    rm -rf "$VENV_DIR"
  fi
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  "$SERVICE_PYTHON_BIN" -m venv --copies "$VENV_DIR"
fi

uv pip install --python "$VENV_DIR/bin/python" -e "$SRC_DIR"
uv pip install --python "$VENV_DIR/bin/python" -e "$WRAPPER_SRC"
rm -rf "$SRC_DIR/miair.egg-info"
find "$SRC_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} +
rm -f "$BIN_DIR/miair_wrapper.py"

cat > "$LAUNCHER" <<LAUNCHER
#!/usr/bin/env bash
set -euo pipefail

PLIST="$PLIST"
WATCHER="$IP_WATCHER"
WRAPPER="$WRAPPER_BIN"

if [ -x "\$WATCHER" ]; then
  "\$WATCHER" --plist "\$PLIST" --label $CORE_LABEL --no-restart >/dev/null 2>&1 || true
fi

resolved_hostname=""
if [ -f "\$PLIST" ]; then
  resolved_hostname="\$(/usr/libexec/PlistBuddy -c 'Print :ProgramArguments:4' "\$PLIST" 2>/dev/null || true)"
fi

args=("\$@")
if [ -n "\$resolved_hostname" ]; then
  replaced=0
  for index in "\${!args[@]}"; do
    if [ "\${args[\$index]}" = "--hostname" ] && [ \$((index + 1)) -lt "\${#args[@]}" ]; then
      args[\$((index + 1))]="\$resolved_hostname"
      replaced=1
      break
    fi
    if [[ "\${args[\$index]}" == --hostname=* ]]; then
      args[\$index]="--hostname=\$resolved_hostname"
      replaced=1
      break
    fi
  done
  if [ "\$replaced" -eq 0 ]; then
    args+=("--hostname" "\$resolved_hostname")
  fi
  export MIAIR_HOSTNAME="\$resolved_hostname"
fi

exec "\$WRAPPER" "\${args[@]}"
LAUNCHER
chmod 755 "$LAUNCHER"
install -m 755 "$SCRIPT_DIR/miair_macos_ip_watch.sh" "$IP_WATCHER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$CORE_LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$LAUNCHER</string>
    <string>--conf-path</string>
    <string>$CONF_DIR</string>
    <string>--hostname</string>
    <string>$HOSTNAME</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$SRC_DIR</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$STATE_DIR/stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$STATE_DIR/stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONUNBUFFERED</key>
    <string>1</string>
    <key>PYTHONDONTWRITEBYTECODE</key>
    <string>1</string>
    <key>MIAIR_HOSTNAME</key>
    <string>$HOSTNAME</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
</dict>
</plist>
PLIST

cat > "$WATCHER_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$WATCH_LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$IP_WATCHER</string>
    <string>--plist</string>
    <string>$PLIST</string>
    <string>--label</string>
    <string>$CORE_LABEL</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>300</integer>
  <key>StandardOutPath</key>
  <string>$STATE_DIR/ip-watch.log</string>
  <key>StandardErrorPath</key>
  <string>$STATE_DIR/ip-watch.err.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
</dict>
</plist>
PLIST

if [ "$LOAD_SERVICE" -eq 1 ]; then
  "$IP_WATCHER" --plist "$PLIST" --label "$CORE_LABEL" --no-restart >/dev/null 2>&1 || true
  launchctl bootout "gui/$(id -u)" "$OLD_WATCHER_PLIST" >/dev/null 2>&1 || true
  launchctl bootout "gui/$(id -u)" "$OLD_PLIST" >/dev/null 2>&1 || true
  launchctl bootout "gui/$(id -u)" "$WATCHER_PLIST" >/dev/null 2>&1 || true
  launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
  rm -f "$OLD_WATCHER_PLIST" "$OLD_PLIST"
  rm -f "$OLD_IP_WATCHER" "$OLD_LAUNCHER"
  launchctl bootstrap "gui/$(id -u)" "$WATCHER_PLIST"
  launchctl enable "gui/$(id -u)/$WATCH_LABEL" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"
  launchctl enable "gui/$(id -u)/$CORE_LABEL" >/dev/null 2>&1 || true
  launchctl kickstart -k "gui/$(id -u)/$CORE_LABEL" >/dev/null 2>&1 || true
  launchctl kickstart -k "gui/$(id -u)/$WATCH_LABEL" >/dev/null 2>&1 || true
fi

echo "MiAir macOS native install complete."
echo "Source: $SRC_DIR"
echo "Venv: $VENV_DIR"
echo "Launcher: $LAUNCHER"
echo "Wrapper: $WRAPPER_BIN"
echo "IP watcher: $IP_WATCHER"
echo "Config: $CONF_DIR"
echo "Logs: $STATE_DIR"
echo "Web UI: http://$HOSTNAME:8300"
