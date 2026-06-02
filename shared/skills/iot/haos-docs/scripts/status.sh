#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

log "checking $HAOS_SSH_TARGET"
remote 'set -e
echo "host=$(hostname)"
echo "config_path=$(readlink /config 2>/dev/null || echo /config)"
ha supervisor info | grep -E "^(host_internet|supervisor_internet|healthy|supported):" || true
ha core info | grep -E "^(version|version_latest|port|ssl):" || true
ls -ld /config /homeassistant 2>/dev/null || true
printf "pyscript_config="
grep -q "^pyscript:" /config/configuration.yaml && echo yes || echo no
printf "pyscript_dir="
test -d /config/pyscript && echo yes || echo no
'
