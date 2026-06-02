#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

if [[ "$#" -eq 0 ]]; then
  set -- configuration.yaml automations.yaml scripts.yaml scenes.yaml
fi

STAMP="$(timestamp)"
DEST="/config/.agent-backups/$STAMP"

precheck
log "creating backup in $DEST"

FILES=""
for file in "$@"; do
  case "$file" in
    /*) die "use paths relative to /config, got absolute path: $file" ;;
    *..*) die "refusing path containing '..': $file" ;;
  esac
  FILES="$FILES $file"
done

remote "set -e
mkdir -p '$DEST'
for file in $FILES; do
  if [ -e \"/config/\$file\" ]; then
    mkdir -p \"$DEST/\$(dirname \"\$file\")\"
    cp -a \"/config/\$file\" \"$DEST/\$file\"
    echo \"$DEST/\$file\"
  else
    echo \"missing:/config/\$file\"
  fi
done
"
