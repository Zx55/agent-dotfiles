#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/install-samba.sh"
"$SCRIPT_DIR/install-mosquitto.sh"
"$SCRIPT_DIR/install-hacs.sh"
"$SCRIPT_DIR/install-xiaomi-home.sh"
"$SCRIPT_DIR/install-ps5-ha-bridge.sh"
