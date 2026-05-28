#!/usr/bin/env sh
set -eu

exec /command/with-contenv /opt/ps5-ha-bridge/bin/python -m ps5_ha_bridge.addon
