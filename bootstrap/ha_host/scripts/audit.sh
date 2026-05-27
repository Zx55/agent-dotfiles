#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[ha_host:audit] %s\n' "$*"
}

section() {
  printf '\n[%s]\n' "$*"
}

print_command() {
  local label="$1"
  shift
  printf '%s: ' "$label"
  if "$@" 2>/dev/null; then
    return 0
  fi
  printf 'unavailable\n'
}

main() {
  section "system"
  print_command "macOS" sw_vers -productVersion
  print_command "build" sw_vers -buildVersion
  print_command "model" sysctl -n hw.model
  print_command "arch" uname -m
  print_command "cpu cores" sysctl -n hw.ncpu
  print_command "memory bytes" sysctl -n hw.memsize

  section "disk"
  df -h / || true

  section "candidate apps"
  for app in \
    "/Applications/UTM.app" \
    "/Applications/Tailscale.app" \
    "/Applications/Docker.app" \
    "/Applications/OrbStack.app" \
    "/Applications/Parallels Desktop.app"; do
    if [[ -d "$app" ]]; then
      log "found: $app"
    else
      log "missing: $app"
    fi
  done

  section "commands"
  for command_name in brew codex uv node npm git git-lfs rg tmux mcp-launcher tailscale ssh; do
    if command -v "$command_name" >/dev/null 2>&1; then
      log "command available: $command_name"
    else
      log "command missing: $command_name"
    fi
  done

  section "power"
  pmset -g custom 2>/dev/null || log "pmset custom settings unavailable"

  section "network"
  scutil --nwi 2>/dev/null || log "network state unavailable"
}

main "$@"
