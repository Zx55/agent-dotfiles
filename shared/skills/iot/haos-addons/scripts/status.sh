#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

remote 'set -e
echo "== Core =="
ha core info | grep -E "^(version|version_latest|update_available|watchdog|boot):" || true
echo "== Supervisor =="
ha supervisor info | grep -E "^(healthy|supported|version|version_latest|update_available):" || true
echo "== Network =="
ha network info | grep -E "^(host_internet|supervisor_internet):" || true
echo "== Apps =="
for slug in core_samba core_mosquitto local_ps5_ha_bridge; do
  echo "-- ${slug} --"
  ha apps info "${slug}" 2>/dev/null | grep -E "^(name|version|state|boot):" || true
done
echo "== HACS =="
test -f /config/custom_components/hacs/manifest.json && grep -n "domain\\|name" /config/custom_components/hacs/manifest.json || true
echo "== Pyscript =="
test -f /config/custom_components/pyscript/manifest.json && grep -n "domain\\|name\\|version" /config/custom_components/pyscript/manifest.json || true
grep -n "^pyscript:" /config/configuration.yaml || true
echo "== Xiaomi Home =="
test -f /config/custom_components/xiaomi_home/manifest.json && grep -n "domain\\|name\\|version" /config/custom_components/xiaomi_home/manifest.json || true
'
