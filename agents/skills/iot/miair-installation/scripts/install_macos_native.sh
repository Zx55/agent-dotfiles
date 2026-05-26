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
LAUNCHER="$BIN_DIR/MiAir"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENTS_DIR="$(cd "$SKILL_DIR/../../.." && pwd)"
WRAPPER_SRC="$AGENTS_DIR/tools/miair-macos-wrapper"
WRAPPER_BIN="$VENV_DIR/bin/miair-macos-wrapper"
CONF_DIR="${MIAIR_CONF:-$HOME/.config/miair}"
STATE_DIR="${MIAIR_STATE:-$HOME/.local/state/miair}"
PLIST="$HOME/Library/LaunchAgents/com.user.miair.plist"

usage() {
  cat <<'USAGE'
Usage: install_macos_native.sh --hostname <mac-lan-ip> [--ref <git-ref>] [--no-load]

Installs MiAir natively on macOS with:
  source: ~/.local/share/miair/src
  venv:   ~/.local/share/miair/venv
  launcher: ~/.local/share/miair/bin/MiAir
  wrapper: ~/.local/share/miair/venv/bin/miair-macos-wrapper
  config: ~/.config/miair
  logs:   ~/.local/state/miair
USAGE
}

detect_lan_ip() {
  ipconfig getifaddr en0 2>/dev/null || true
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
  HOSTNAME="$(detect_lan_ip)"
fi

if [ -z "$HOSTNAME" ] || [ "$HOSTNAME" = "127.0.0.1" ]; then
  echo "A real LAN IP is required. Pass --hostname <mac-lan-ip>." >&2
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

uv python install 3.12

if [ ! -x "$VENV_DIR/bin/python" ]; then
  uv venv --python 3.12 "$VENV_DIR"
fi

uv pip install --python "$VENV_DIR/bin/python" -e "$SRC_DIR"
uv pip install --python "$VENV_DIR/bin/python" -e "$WRAPPER_SRC"
rm -rf "$SRC_DIR/miair.egg-info"
find "$SRC_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} +
rm -f "$BIN_DIR/miair_wrapper.py"

cat > "$LAUNCHER" <<LAUNCHER
#!/usr/bin/env bash
set -euo pipefail
exec "$WRAPPER_BIN" "\$@"
LAUNCHER
chmod 755 "$LAUNCHER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.user.miair</string>
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

if [ "$LOAD_SERVICE" -eq 1 ]; then
  launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"
  launchctl enable "gui/$(id -u)/com.user.miair" >/dev/null 2>&1 || true
  launchctl kickstart -k "gui/$(id -u)/com.user.miair" >/dev/null 2>&1 || true
fi

echo "MiAir macOS native install complete."
echo "Source: $SRC_DIR"
echo "Venv: $VENV_DIR"
echo "Launcher: $LAUNCHER"
echo "Wrapper: $WRAPPER_BIN"
echo "Config: $CONF_DIR"
echo "Logs: $STATE_DIR"
echo "Web UI: http://$HOSTNAME:8300"
