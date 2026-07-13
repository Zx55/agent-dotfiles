#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROFILE_ROOT="$(cd "$PROFILE_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
ERRORS=0
WARNINGS=0
AGENT="codex"

usage() {
  cat <<'EOF'
Usage: ha-host/bootstrap/bootstrap.sh verify [options]

Options:
  --agent <name>        Agent to verify. Currently only "codex" is supported.
  -h, --help            Show this help.

Checks host readiness for running Home Assistant OS in a macOS VM. This script is read-only.
EOF
}

ok() {
  printf '[ha-host:verify] ok: %s\n' "$*"
}

warn() {
  WARNINGS=$((WARNINGS + 1))
  printf '[ha-host:verify] warning: %s\n' "$*" >&2
}

fail() {
  ERRORS=$((ERRORS + 1))
  printf '[ha-host:verify] error: %s\n' "$*" >&2
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agent)
        if [[ $# -lt 2 ]]; then
          fail "--agent requires a value"
          return 1
        fi
        AGENT="$2"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        fail "unknown argument: $1"
        return 1
        ;;
    esac
    shift
  done
}

validate_args() {
  case "$AGENT" in
    codex)
      ;;
    *)
      fail "unsupported agent: $AGENT"
      return 1
      ;;
  esac
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

pmset_ac_value() {
  local key="$1"
  pmset -g custom | awk -v key="$key" '
    /^AC Power:/ {
      in_ac = 1
      next
    }
    /^[[:alpha:]][[:alnum:] ]*:$/ {
      if (in_ac) {
        exit
      }
    }
    in_ac && $1 == key {
      print $2
      exit
    }
  '
}

check_power_policy() {
  local sleep_value displaysleep_value disksleep_value
  sleep_value="$(pmset_ac_value sleep)"
  displaysleep_value="$(pmset_ac_value displaysleep)"
  disksleep_value="$(pmset_ac_value disksleep)"

  if [[ "$sleep_value" == "0" ]]; then
    ok "AC power system sleep disabled"
  else
    fail "AC power system sleep should be disabled: sleep=${sleep_value:-unset}"
  fi

  if [[ "$displaysleep_value" == "10" ]]; then
    ok "AC power display sleep: ${displaysleep_value} minutes"
  else
    fail "AC power display sleep should be 10 minutes: displaysleep=${displaysleep_value:-unset}"
  fi

  if [[ "$disksleep_value" == "0" ]]; then
    ok "AC power disk sleep disabled"
  else
    fail "AC power disk sleep should be disabled: disksleep=${disksleep_value:-unset}"
  fi
}

check_agent_python() {
  local python="$HOME/.local/share/agent-dotfiles/python/bin/python"
  if [[ -x "$python" ]]; then
    ok "shared agent Python available: $python"
  else
    fail "shared agent Python missing: $python"
  fi

  local root_service_python="/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python"
  if [[ -x "$root_service_python" ]]; then
    ok "root-owned HA host service Python available: $root_service_python"
  else
    fail "HA host service Python missing: $root_service_python"
  fi
}

check_symlink() {
  local source="$1"
  local target="$2"

  if [[ ! -e "$source" ]]; then
    fail "source missing: $source"
    return 0
  fi

  if [[ ! -L "$target" ]]; then
    fail "target should be a symlink: $target"
    return 0
  fi

  if [[ "$(readlink "$target")" == "$source" ]]; then
    ok "symlink current: $target -> $source"
  else
    fail "symlink target differs: $target -> $(readlink "$target")"
  fi
}

resolve_link_target() {
  local link_path="$1"
  local target
  target="$(readlink "$link_path")"
  case "$target" in
    /*)
      printf '%s\n' "$target"
      ;;
    *)
      local target_dir
      local target_base
      target_dir="$(dirname "$target")"
      target_base="$(basename "$target")"
      printf '%s/%s\n' "$(cd "$(dirname "$link_path")/$target_dir" && pwd)" "$target_base"
      ;;
  esac
}

check_resolved_symlink() {
  local source="$1"
  local target="$2"

  if [[ ! -e "$source" ]]; then
    fail "source missing: $source"
    return 0
  fi

  if [[ ! -L "$target" ]]; then
    fail "target should be a symlink: $target"
    return 0
  fi

  if [[ "$(resolve_link_target "$target")" == "$source" ]]; then
    ok "symlink current: $target -> $source"
  else
    fail "symlink target differs: $target -> $(resolve_link_target "$target")"
  fi
}

check_codex_link_state() {
  check_symlink "$PROFILE_ROOT/agent/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
  check_symlink "$PROFILE_ROOT/agent/codex/config.toml" "$HOME/.codex/config.toml"
  check_symlink "$PROFILE_ROOT/agent/codex/hooks.json" "$HOME/.codex/hooks.json"
  check_symlink "$PROFILE_ROOT/agent/codex/rules" "$HOME/.codex/rules"
  check_symlink "$PROFILE_ROOT/agent/codex/automations" "$HOME/.codex/automations"
  check_resolved_symlink "$REPO_ROOT/shared/hooks/codex-sync-config.py" "$PROFILE_ROOT/agent/codex/hooks/codex-sync-config.py"
  check_resolved_symlink "$REPO_ROOT/shared/hooks/codex-sync-automations.py" "$PROFILE_ROOT/agent/codex/hooks/codex-sync-automations.py"
  check_resolved_symlink "$REPO_ROOT/shared/hooks/codex-secret-guard-tool-use-after.py" "$PROFILE_ROOT/agent/codex/hooks/codex-secret-guard-tool-use-after.py"

  local skills_root="$PROFILE_ROOT/agent/skills"
  local skill_path
  while IFS= read -r skill_path; do
    local relative
    local source
    relative="${skill_path#$skills_root/}"
    if [[ ! -L "$skill_path" ]]; then
      fail "profile skill should be a symlink: $skill_path"
      continue
    fi
    source="$(resolve_link_target "$skill_path")"
    if [[ -d "$source" ]]; then
      ok "profile skill link target exists: $relative"
    else
      fail "profile skill link target missing: $skill_path -> $source"
      continue
    fi
    check_symlink "$source" "$HOME/.agents/skills/$relative"
  done < <(find "$skills_root" -mindepth 2 -maxdepth 2 \( -type d -o -type l \) | sort)
}

check_orchestrator_doctor() {
  local doctor="$PROFILE_ROOT/tools/orchestrator/scripts/doctor.sh"
  if [[ ! -x "$doctor" ]]; then
    warn "orchestrator doctor missing or not executable: $doctor"
    return 0
  fi

  ok "running orchestrator doctor: $doctor"
  if "$doctor"; then
    ok "orchestrator doctor passed"
  else
    fail "orchestrator doctor failed"
  fi
}

main() {
  parse_args "$@" || true
  validate_args || true

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
  check_command_required pmset
  check_command_optional tailscale
  check_app_required "/Applications/UTM.app"
  check_app_required "/Applications/Clash Verge.app"
  check_app_required "/Applications/Tailscale.app"
  check_power_policy
  check_agent_python
  check_codex_link_state
  check_orchestrator_doctor

  warn "If the tailscale command is missing after installing Tailscale.app, enable CLI integration from Tailscale settings."
  warn "Remote Login, public SSH exposure, and HAOS VM creation are not automated yet."

  if [[ "$ERRORS" -gt 0 ]]; then
    printf '[ha-host:verify] failed with %s error(s) and %s warning(s)\n' "$ERRORS" "$WARNINGS" >&2
    exit 1
  fi

  printf '[ha-host:verify] passed with %s warning(s)\n' "$WARNINGS"
}

main "$@"
