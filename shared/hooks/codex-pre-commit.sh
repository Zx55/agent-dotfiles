#!/usr/bin/env bash

codex_pre_commit() {
  local repo_root="$1"
  local config_source="$HOME/.codex/config.toml"
  local hooks_target="$HOME/.codex/hooks.json"
  local sync_script="$repo_root/shared/hooks/codex-sync-config.py"
  local automations_source="$HOME/.codex/automations"
  local automations_sync_script="$repo_root/shared/hooks/codex-sync-automations.py"
  local active_profile_root=""

  codex_pre_commit_log() {
    printf '[pre-commit:codex] %s\n' "$*" >&2
  }

  codex_detect_active_profile() {
    [[ -L "$hooks_target" ]] || return 1
    local target
    target="$(readlink "$hooks_target")"
    local profile
    for profile in master ha-host; do
      if [[ "$target" == "$repo_root/$profile/agent/codex/hooks.json" ]]; then
        active_profile_root="$repo_root/$profile"
        return 0
      fi
    done
    return 1
  }

  codex_config_load_check() {
    local profile_codex_home="$1"
    local temp_home
    local status=0
    temp_home="$(mktemp -d "${TMPDIR:-/tmp}/agent-dotfiles-codex.XXXXXX")"
    cp "$profile_codex_home/config.toml" "$temp_home/config.toml"
    CODEX_HOME="$temp_home" codex features list >/dev/null || status=$?
    rm -rf "$temp_home"
    return "$status"
  }

  codex_sync_portable_config() {
    local portable_config="$1"
    python3 "$sync_script" --config "$config_source" --output "$portable_config" >/dev/null
    if ! git -C "$repo_root" diff --quiet -- "$portable_config"; then
      git -C "$repo_root" add "$portable_config"
    fi
  }

  if codex_detect_active_profile; then
    local portable_config="$active_profile_root/agent/codex/config.toml"
    local portable_automations="$active_profile_root/agent/codex/automations"

    if [[ -f "$config_source" ]]; then
      codex_pre_commit_log "Syncing portable config from ~/.codex/config.toml"
      codex_sync_portable_config "$portable_config"
    else
      codex_pre_commit_log "Skipping config sync because ~/.codex/config.toml is missing"
    fi

    if [[ -d "$automations_source" ]]; then
      codex_pre_commit_log "Syncing portable automations from ~/.codex/automations"
      python3 "$automations_sync_script" \
        --runtime-dir "$automations_source" \
        --output-dir "$portable_automations" \
        >/dev/null
      git -C "$repo_root" add "$portable_automations"
    else
      codex_pre_commit_log "Skipping automation sync because ~/.codex/automations is missing"
    fi
  else
    codex_pre_commit_log "Skipping config and automation sync because ~/.codex/hooks.json is not linked to a profile in this repo"
  fi

  if command -v codex >/dev/null 2>&1; then
    if [[ -n "$active_profile_root" ]]; then
      codex_config_load_check "$active_profile_root/agent/codex"
      if [[ -f "$config_source" ]]; then
        codex_sync_portable_config "$active_profile_root/agent/codex/config.toml"
      fi
    else
      codex_pre_commit_log "Skipping config load check because no active repo profile was detected"
    fi
  else
    codex_pre_commit_log "Skipping config load check because codex is unavailable"
  fi
}
