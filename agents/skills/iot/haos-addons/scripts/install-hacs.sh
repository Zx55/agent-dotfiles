#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

precheck
remote 'set -e
cd /config
wget -O - https://get.hacs.xyz | bash -
test -f /config/custom_components/hacs/manifest.json
grep -n "domain\\|name" /config/custom_components/hacs/manifest.json
ha core restart --no-progress
'
log "HACS files installed. Complete GitHub authorization in the HA UI after Core restarts."
