#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
ERRORS=0
WARNINGS=0

usage() {
  cat <<'EOF'
Usage: bootstrap/bootstrap.sh --profile ha_host verify

Checks host readiness for running Home Assistant OS in a macOS VM. This script is read-only.
EOF
}

ok() {
  printf '[ha_host:verify] ok: %s\n' "$*"
}

warn() {
  WARNINGS=$((WARNINGS + 1))
  printf '[ha_host:verify] warning: %s\n' "$*" >&2
}

fail() {
  ERRORS=$((ERRORS + 1))
  printf '[ha_host:verify] error: %s\n' "$*" >&2
}

check_command_required() {
  local command_name="$1"
  if command -v "$command_name" >/dev/null 2>&1; then
    ok "command available: $command_name"
  else
    fail "command missing: $command_name"
  fi
}

check_command_optional() {
  local command_name="$1"
  if command -v "$command_name" >/dev/null 2>&1; then
    ok "optional command available: $command_name"
  else
    warn "optional command missing: $command_name"
  fi
}

check_app_optional() {
  local app_path="$1"
  if [[ -d "$app_path" ]]; then
    ok "app installed: $app_path"
  else
    warn "app missing: $app_path"
  fi
}

check_app_required() {
  local app_path="$1"
  if [[ -d "$app_path" ]]; then
    ok "app installed: $app_path"
  else
    fail "app missing: $app_path"
  fi
}

check_arch() {
  local arch
  arch="$(uname -m)"
  if [[ "$arch" == "arm64" ]]; then
    ok "Apple Silicon architecture: $arch"
  else
    fail "unexpected architecture for this HA host plan: $arch"
  fi
}

check_memory() {
  local memory_bytes memory_gb
  memory_bytes="$(sysctl -n hw.memsize 2>/dev/null || true)"
  if [[ -z "$memory_bytes" || ! "$memory_bytes" =~ ^[0-9]+$ ]]; then
    warn "memory size unavailable"
    return 0
  fi

  memory_gb=$((memory_bytes / 1024 / 1024 / 1024))
  if [[ "$memory_gb" -ge 16 ]]; then
    ok "memory: ${memory_gb}GB"
  else
    warn "memory may be tight for HA OS VM plus macOS: ${memory_gb}GB"
  fi
}

check_disk() {
  local available_kb available_gb
  available_kb="$(df -k / | awk 'NR == 2 {print $4}')"
  available_gb=$((available_kb / 1024 / 1024))
  if [[ "$available_gb" -ge 80 ]]; then
    ok "root disk free: ${available_gb}GB"
  else
    warn "root disk free space may be tight for VM images and backups: ${available_gb}GB"
  fi
}

check_agent_python() {
  local python="$HOME/.local/share/agent-dotfiles/python/bin/python"
  if [[ -x "$python" ]]; then
    ok "shared agent Python available: $python"
  else
    fail "shared agent Python missing: $python"
  fi
}

check_copied_file() {
  local source="$1"
  local target="$2"

  if [[ ! -f "$target" ]]; then
    fail "copied file missing: $target"
    return 0
  fi
  if [[ -L "$target" ]]; then
    fail "target should be a copied regular file, not a symlink: $target"
    return 0
  fi
  if cmp -s "$source" "$target"; then
    ok "copied file current: $target"
  else
    fail "copied file differs from source: $target"
  fi
}

check_copied_directory() {
  local source="$1"
  local target="$2"

  if [[ ! -d "$target" ]]; then
    fail "copied directory missing: $target"
    return 0
  fi
  if [[ -L "$target" ]]; then
    fail "target should be a copied directory, not a symlink: $target"
    return 0
  fi
  if diff -qr "$source" "$target" >/dev/null 2>&1; then
    ok "copied directory current: $target"
  else
    fail "copied directory differs from source: $target"
  fi
}

check_absent() {
  local target="$1"
  if [[ -e "$target" || -L "$target" ]]; then
    fail "target should be absent for HA host profile: $target"
  else
    ok "target absent: $target"
  fi
}

check_codex_copy_state() {
  check_copied_file "$REPO_ROOT/agents/AGENTS.md" "$HOME/.codex/AGENTS.md"
  check_copied_file "$REPO_ROOT/agents/codex/config.toml" "$HOME/.codex/config.toml"
  check_copied_directory "$REPO_ROOT/agents/codex/rules" "$HOME/.codex/rules"
  check_absent "$HOME/.codex/hooks.json"

  local skill_dir
  for skill_dir in "$REPO_ROOT"/agents/skills/*; do
    [[ -d "$skill_dir" ]] || continue
    check_copied_directory "$skill_dir" "$HOME/.codex/skills/$(basename "$skill_dir")"
  done
}

main() {
  case "${1:-}" in
    -h|--help)
      usage
      exit 0
      ;;
    "")
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac

  check_arch
  check_memory
  check_disk
  check_command_required brew
  check_command_required ssh
  check_command_required codex
  check_command_required uv
  check_command_required node
  check_command_required npm
  check_command_required git
  check_command_required git-lfs
  check_command_required rg
  check_command_required tmux
  check_command_required mcp-launcher
  check_command_optional tailscale
  check_app_required "/Applications/UTM.app"
  check_app_required "/Applications/Clash Verge.app"
  check_app_required "/Applications/Tailscale.app"
  check_agent_python
  check_codex_copy_state

  warn "If the tailscale command is missing after installing Tailscale.app, enable CLI integration from Tailscale settings."
  warn "Remote Login, public SSH exposure, sleep policy, and HA OS VM settings are not automated yet."

  if [[ "$ERRORS" -gt 0 ]]; then
    printf '[ha_host:verify] failed with %s error(s) and %s warning(s)\n' "$ERRORS" "$WARNINGS" >&2
    exit 1
  fi

  printf '[ha_host:verify] passed with %s warning(s)\n' "$WARNINGS"
}

main "$@"
