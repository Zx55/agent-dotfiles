#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

XIAOMI_HOME_VERSION="${XIAOMI_HOME_VERSION:-latest}"

latest_xiaomi_home_tag() {
  git ls-remote --tags --refs https://github.com/XiaoMi/ha_xiaomi_home.git |
    awk '{sub("refs/tags/", "", $2); print $2}' |
    sort -V |
    tail -n 1
}

precheck

version="$XIAOMI_HOME_VERSION"
if [[ "$version" == "latest" ]]; then
  version="$(latest_xiaomi_home_tag)"
fi
[[ -n "$version" ]] || die "could not resolve Xiaomi Home version"

remote "set -e
cd /config
if [ -d ha_xiaomi_home ]; then
  cd ha_xiaomi_home
  git fetch --tags origin
  git checkout '$version'
else
  git clone --branch '$version' https://github.com/XiaoMi/ha_xiaomi_home.git
  cd ha_xiaomi_home
fi
./install.sh /config
grep -n \"domain\\\\|name\\\\|version\" /config/custom_components/xiaomi_home/manifest.json
ha core restart --no-progress
"
log "Xiaomi Home $version installed. Complete Xiaomi OAuth setup in the HA UI after Core restarts."
