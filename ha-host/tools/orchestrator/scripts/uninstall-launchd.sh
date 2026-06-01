#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/usr/local/libexec/agent-dotfiles/orchestrator"
ROOT_START_PLIST="/Library/LaunchDaemons/com.user.ha-host-startup.plist"
ROOT_WATCH_PLIST="/Library/LaunchDaemons/com.user.ha-host-watch.plist"
USER_START_PLIST="$HOME/Library/LaunchAgents/com.user.haos-start.plist"
USER_WATCH_PLIST="$HOME/Library/LaunchAgents/com.user.haos-watch.plist"

launchctl bootout "gui/$(id -u)/com.user.haos-start" >/dev/null 2>&1 || true
launchctl bootout "gui/$(id -u)/com.user.haos-watch" >/dev/null 2>&1 || true
sudo launchctl bootout system/com.user.ha-host-startup >/dev/null 2>&1 || true
sudo launchctl bootout system/com.user.ha-host-watch >/dev/null 2>&1 || true

rm -f "$USER_START_PLIST" "$USER_WATCH_PLIST"
sudo rm -f "$ROOT_START_PLIST" "$ROOT_WATCH_PLIST"
sudo rm -rf "$INSTALL_DIR"

printf '[orchestrator-uninstall] removed launchd jobs and runtime copy\n'
