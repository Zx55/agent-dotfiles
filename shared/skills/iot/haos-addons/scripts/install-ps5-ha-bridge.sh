#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

LOCAL_ADDON_DIR="/addons/ps5_ha_bridge"
LOCAL_ADDON_SLUG="local_ps5_ha_bridge"

precheck

ROOT="$(repo_root)" || die "could not find agent-dotfiles repo root. Set REPO_ROOT=/path/to/agent-dotfiles."
SRC="$ROOT/ha-host/tools/ps5-ha-bridge"
[[ -f "$SRC/config.yaml" && -f "$SRC/Dockerfile" && -f "$SRC/run.sh" ]] || die "PS5 HA Bridge source is incomplete: $SRC"

log "copying PS5 HA Bridge source to HAOS $LOCAL_ADDON_DIR"
tar \
  --exclude .venv \
  --exclude .pytest_cache \
  --exclude __pycache__ \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  -C "$SRC" -cf - . |
  remote "set -e
rm -rf '$LOCAL_ADDON_DIR'
mkdir -p '$LOCAL_ADDON_DIR'
tar -C '$LOCAL_ADDON_DIR' -xf -
"

log "reloading local add-ons"
remote 'ha apps reload --no-progress >/dev/null 2>&1 || ha addons reload --no-progress >/dev/null 2>&1 || true'

log "installing and starting $LOCAL_ADDON_SLUG"
remote "set -e
if ! ha apps info '$LOCAL_ADDON_SLUG' >/dev/null 2>&1; then
  ha apps install '$LOCAL_ADDON_SLUG' --no-progress
fi
ha apps start '$LOCAL_ADDON_SLUG' --no-progress
ha apps info '$LOCAL_ADDON_SLUG' | grep -E '^(name|version|state|boot):' || true
"

log "open the add-on Web UI to pair or re-pair the PS5."
