#!/bin/zsh
set -euo pipefail

SCRIPT_DIR=${0:A:h}
ROOT_DIR=${SCRIPT_DIR:h}

cd "$ROOT_DIR"

UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/uv-cache}
export UV_CACHE_DIR
PYINSTALLER_CONFIG_DIR=${PYINSTALLER_CONFIG_DIR:-$ROOT_DIR/build/pyinstaller/config}
export PYINSTALLER_CONFIG_DIR

uv sync --dev

rm -rf "$ROOT_DIR/build/pyinstaller"

uv run pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name zotero-mcp-wrapper \
  --distpath "$ROOT_DIR/dist" \
  --workpath "$ROOT_DIR/build/pyinstaller" \
  --specpath "$ROOT_DIR/build/pyinstaller" \
  --paths "$ROOT_DIR" \
  "$ROOT_DIR/zotero_mcp_wrapper/cli.py"

echo "Built binary: $ROOT_DIR/dist/zotero-mcp-wrapper"
