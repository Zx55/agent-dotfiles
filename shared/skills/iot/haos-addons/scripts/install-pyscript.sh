#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

PYSCRIPT_ZIP_URL="${PYSCRIPT_ZIP_URL:-https://github.com/custom-components/pyscript/releases/latest/download/hass-custom-pyscript.zip}"
PYSCRIPT_NO_RESTART="${PYSCRIPT_NO_RESTART:-0}"

precheck

remote "set -e
ts=\$(date +%Y%m%d%H%M%S)
workdir=\$(mktemp -d /tmp/pyscript-install.XXXXXX)
cleanup() {
  rm -rf \"\$workdir\"
}
trap cleanup EXIT

cd /config
test -f configuration.yaml
cp configuration.yaml \"configuration.yaml.bak-pyscript-\$ts\"

if [ -d /config/custom_components/pyscript ]; then
  rm -rf \"/config/custom_components/pyscript.bak-pyscript-\$ts\"
  cp -a /config/custom_components/pyscript \"/config/custom_components/pyscript.bak-pyscript-\$ts\"
fi

wget -O \"\$workdir/hass-custom-pyscript.zip\" '$PYSCRIPT_ZIP_URL'
rm -rf \"\$workdir/unpack\"
mkdir -p \"\$workdir/unpack\"
unzip -q \"\$workdir/hass-custom-pyscript.zip\" -d \"\$workdir/unpack\"

if [ -d \"\$workdir/unpack/custom_components/pyscript\" ]; then
  src=\"\$workdir/unpack/custom_components/pyscript\"
elif [ -f \"\$workdir/unpack/manifest.json\" ]; then
  src=\"\$workdir/unpack\"
else
  echo 'Could not find pyscript component in release zip' >&2
  find \"\$workdir/unpack\" -maxdepth 3 -type f | sort >&2
  exit 1
fi

mkdir -p /config/custom_components
rm -rf /config/custom_components/pyscript
cp -a \"\$src\" /config/custom_components/pyscript
mkdir -p /config/pyscript

if ! grep -Eq '^pyscript:[[:space:]]*$' /config/configuration.yaml; then
  cat >> /config/configuration.yaml <<'EOF'

pyscript:
  hass_is_global: true
EOF
fi

test -f /config/custom_components/pyscript/manifest.json
grep -n \"domain\\|name\\|version\" /config/custom_components/pyscript/manifest.json || true
grep -n '^pyscript:' /config/configuration.yaml
ha core check

if [ '$PYSCRIPT_NO_RESTART' != '1' ]; then
  ha core restart --no-progress
else
  echo 'PYSCRIPT_NO_RESTART=1; restart skipped'
fi
"

if [[ "$PYSCRIPT_NO_RESTART" == "1" ]]; then
  log "Pyscript files installed and HA config check passed. Restart HA Core before using Pyscript."
else
  log "Pyscript files installed, HA config check passed, and HA Core restart was requested."
fi
