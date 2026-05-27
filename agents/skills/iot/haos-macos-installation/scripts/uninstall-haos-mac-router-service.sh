#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/usr/local/libexec/agent-dotfiles/haos-mac-router"
PLIST_DST="/Library/LaunchDaemons/com.user.haos-mac-router.plist"

sudo launchctl bootout system/com.user.haos-mac-router >/dev/null 2>&1 || true
sudo rm -f "$PLIST_DST"
sudo rm -rf "$INSTALL_DIR"

echo "[haos-mac-router-service] removed service files"
echo "[haos-mac-router-service] run haos-mac-router.sh stop separately if you also want to flush current pf rules"
