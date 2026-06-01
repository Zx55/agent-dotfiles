#!/usr/bin/env bash

HAOS_SSH_TARGET="${HAOS_SSH_TARGET:-haos}"

script_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

skill_dir() {
  cd "$(script_dir)/.." && pwd
}

repo_root() {
  if [[ -n "${REPO_ROOT:-}" ]]; then
    printf '%s\n' "$REPO_ROOT"
    return 0
  fi

  local current
  current="$(skill_dir)"
  while [[ "$current" != "/" ]]; do
    if [[ -d "$current/ha-host/bootstrap" && -d "$current/ha-host/agent/skills" ]]; then
      printf '%s\n' "$current"
      return 0
    fi
    current="$(dirname "$current")"
  done

  return 1
}

log() {
  printf '[haos-addons] %s\n' "$*"
}

die() {
  printf '[haos-addons] error: %s\n' "$*" >&2
  exit 1
}

remote() {
  ssh "$HAOS_SSH_TARGET" "$@"
}

precheck() {
  remote 'ha supervisor info >/dev/null && ha network info >/dev/null'
}

install_and_start_app() {
  local slug="$1"
  precheck
  remote "set -e
if ! ha apps info '$slug' >/dev/null 2>&1; then
  ha apps install '$slug' --no-progress
fi
ha apps start '$slug' --no-progress
ha apps info '$slug' | grep -E '^(name|version|state|boot):' || true
"
}

app_info() {
  local slug="$1"
  remote "ha apps info '$slug' 2>/dev/null | grep -E '^(name|version|state|boot):' || true"
}
