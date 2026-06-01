#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROFILE_ROOT="$(cd "$PROFILE_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
PACKAGE_DIR="$PROFILE_DIR/packages"
AGENT="codex"
ERRORS=0
WARNINGS=0

usage() {
  cat <<'EOF'
Usage: master/bootstrap/bootstrap.sh verify [options]

Options:
  --agent <name>         Agent to verify. Currently only "codex" is supported.
  -h, --help             Show this help.
EOF
}

ok() {
  printf '[verify] ok: %s\n' "$*"
}

warn() {
  WARNINGS=$((WARNINGS + 1))
  printf '[verify] warning: %s\n' "$*" >&2
}

fail() {
  ERRORS=$((ERRORS + 1))
  printf '[verify] error: %s\n' "$*" >&2
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agent)
        [[ $# -ge 2 ]] || {
          fail "--agent requires a value"
          exit 2
        }
        AGENT="$2"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        fail "unknown argument: $1"
        exit 2
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
      ;;
  esac
}

check_command() {
  local command_name="$1"
  if command -v "$command_name" >/dev/null 2>&1; then
    ok "command available: $command_name"
  else
    fail "command missing: $command_name"
  fi
}

check_optional_command() {
  local command_name="$1"
  if command -v "$command_name" >/dev/null 2>&1; then
    ok "optional command available: $command_name"
  else
    warn "optional command missing: $command_name"
  fi
}

check_symlink() {
  local source="$1"
  local target="$2"
  local required="${3:-required}"

  if [[ ! -e "$source" ]]; then
    if [[ "$required" == "required" ]]; then
      fail "source missing: $source"
    else
      warn "optional source missing: $source"
    fi
    return 0
  fi

  if [[ ! -L "$target" ]]; then
    if [[ "$required" == "required" ]]; then
      fail "target is not a symlink: $target"
    else
      warn "optional target is not a symlink: $target"
    fi
    return 0
  fi

  if [[ "$(readlink "$target")" == "$source" ]]; then
    ok "symlink: $target"
  else
    fail "symlink target mismatch: $target -> $(readlink "$target"), expected $source"
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

check_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    ok "file exists: $path"
  else
    fail "file missing: $path"
  fi
}

check_regular_file() {
  local path="$1"
  if [[ -f "$path" && ! -L "$path" ]]; then
    ok "regular file: $path"
  elif [[ -L "$path" ]]; then
    fail "target should be a regular local file, not a symlink: $path"
  else
    fail "file missing: $path"
  fi
}

check_text_absent() {
  local path="$1"
  local needle="$2"
  local label="$3"

  if grep -Fq "$needle" "$path"; then
    fail "$label contains forbidden text '$needle': $path"
  else
    ok "$label has no forbidden text: $path"
  fi
}

check_package_files() {
  local file
  for file in \
    "$PACKAGE_DIR/Brewfile.core" \
    "$PACKAGE_DIR/Brewfile.large-app" \
    "$PACKAGE_DIR/agent-python.txt" \
    "$PACKAGE_DIR/uv-tools.txt" \
    "$PACKAGE_DIR/npm-global.txt" \
    "$PACKAGE_DIR/local-tools.txt" \
    "$PACKAGE_DIR/mas-apps.txt" \
    "$PACKAGE_DIR/ml-models.tsv"; do
    check_file "$file"
  done
}

check_local_tools_sources() {
  local file="$PACKAGE_DIR/local-tools.txt"
  [[ -f "$file" ]] || return 0

  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="$(trim "$line")"
    [[ -n "$line" ]] || continue

    local source_path="${line%%|*}"
    source_path="$(trim "$source_path")"
    source_path="$(expand_path "$source_path")"
    if [[ -f "$source_path" ]]; then
      ok "local tool source exists: $source_path"
    else
      fail "local tool source missing: $source_path"
    fi
  done < "$file"
}

check_uv_tools_sources() {
  local file="$PACKAGE_DIR/uv-tools.txt"
  [[ -f "$file" ]] || return 0

  while IFS= read -r tool || [[ -n "$tool" ]]; do
    tool="${tool%%#*}"
    tool="$(trim "$tool")"
    [[ -n "$tool" ]] || continue

    if [[ "$tool" == ./* ]]; then
      local source_path="$REPO_ROOT/${tool#./}"
      if [[ -e "$source_path" ]]; then
        ok "uv local tool source exists: $tool"
      else
        fail "uv local tool source missing: $tool"
      fi
    fi
  done < "$file"
}

check_ml_models_file() {
  local file="$PACKAGE_DIR/ml-models.tsv"
  [[ -f "$file" ]] || return 0

  local line backend id target notes
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="$(trim "$line")"
    [[ -n "$line" ]] || continue
    [[ "$line" != \#* ]] || continue

    IFS=$'\t' read -r backend id target notes <<< "$line"
    backend="$(trim "${backend:-}")"
    id="$(trim "${id:-}")"
    target="$(trim "${target:-}")"
    if [[ -z "$backend" || -z "$id" ]]; then
      fail "invalid ml model row: $line"
      continue
    fi
    case "$backend" in
      hf)
        ok "ml model row valid: $backend $id"
        ;;
      torch-hub)
        if [[ -n "$target" && "$target" != "default" ]]; then
          ok "ml model row valid: $backend $id"
        else
          fail "torch-hub ml model row requires target model name: $line"
        fi
        ;;
      url)
        if [[ -n "$target" && "$target" != "default" ]]; then
          ok "ml model row valid: $backend $id"
        else
          fail "url ml model row requires target path: $line"
        fi
        ;;
      *)
        fail "invalid ml model backend: $backend"
        ;;
    esac
  done < "$file"
}

check_mas_file() {
  local file="$PACKAGE_DIR/mas-apps.txt"
  [[ -f "$file" ]] || return 0

  local line app_id
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="$(trim "$line")"
    [[ -n "$line" ]] || continue
    [[ "$line" != \#* ]] || continue
    app_id="${line%%[[:space:]]*}"
    if [[ "$app_id" =~ ^[0-9]+$ ]]; then
      ok "mas app id valid: $app_id"
    else
      fail "invalid mas app line: $line"
    fi
  done < "$file"
}

check_codex_links() {
  check_symlink "$REPO_ROOT/shared/AGENTS.md" "$HOME/.codex/AGENTS.md"
  check_symlink "$PROFILE_ROOT/agent/codex/config.toml" "$HOME/.codex/config.toml"
  check_symlink "$PROFILE_ROOT/agent/codex/hooks.json" "$HOME/.codex/hooks.json"
  check_symlink "$PROFILE_ROOT/agent/codex/rules" "$HOME/.codex/rules" optional
  check_symlink "$PROFILE_ROOT/agent/codex/automations" "$HOME/.codex/automations" optional

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
    check_symlink "$source" "$HOME/.codex/skills/$relative"
  done < <(find "$skills_root" -mindepth 2 -maxdepth 2 \( -type d -o -type l \) | sort)
}

check_codex_automations() {
  local automations_dir="$PROFILE_ROOT/agent/codex/automations"
  local runtime_dir="$HOME/.codex/automations"
  local syncer="$REPO_ROOT/shared/hooks/codex-sync-automations.py"
  local automation_dir runtime_automation_dir source target expected_id actual_id runtime_source
  [[ -d "$automations_dir" ]] || {
    warn "optional Codex automations source missing: $automations_dir"
    return 0
  }

  if [[ -f "$syncer" ]]; then
    if command -v python3 >/dev/null 2>&1; then
      if python3 "$syncer" \
        --runtime-dir "$HOME/.codex/automations" \
        --output-dir "$automations_dir" \
        --check >/dev/null 2>&1; then
        ok "Codex automation snapshots are synced"
      else
        fail "Codex automation snapshots are out of sync with ~/.codex/automations"
      fi
    else
      fail "python3 missing for Codex automation sync hook"
    fi
  else
    fail "Codex automation sync hook missing: $syncer"
  fi

  if [[ -d "$runtime_dir" ]]; then
    for runtime_automation_dir in "$runtime_dir"/*; do
      [[ -d "$runtime_automation_dir" ]] || continue
      runtime_source="$runtime_automation_dir/automation.toml"
      [[ -f "$runtime_source" ]] || continue

      expected_id="$(basename "$runtime_automation_dir")"
      source="$automations_dir/$expected_id/automation.toml"

      actual_id="$(awk -F '"' '/^id = / {print $2; exit}' "$runtime_source")"
      if [[ "$actual_id" == "$expected_id" ]]; then
        ok "installed Codex automation id matches directory: $expected_id"
      else
        fail "installed Codex automation id '$actual_id' does not match directory '$expected_id'"
      fi

      check_regular_file "$source"
      [[ -f "$source" ]] || continue
      check_text_absent "$source" "/Users/chenzeren" "portable Codex automation source"

      actual_id="$(awk -F '"' '/^id = / {print $2; exit}' "$source")"
      if [[ "$actual_id" == "$expected_id" ]]; then
        ok "Codex automation snapshot id matches directory: $expected_id"
      else
        fail "Codex automation snapshot id '$actual_id' does not match directory '$expected_id'"
      fi
    done
  else
    warn "optional Codex automation runtime missing: $runtime_dir"
  fi

  for automation_dir in "$automations_dir"/*; do
    [[ -d "$automation_dir" ]] || continue
    expected_id="$(basename "$automation_dir")"
    source="$automation_dir/automation.toml"
    target="$HOME/.codex/automations/$expected_id/automation.toml"

    check_file "$source"
    [[ -f "$source" ]] || continue
    check_text_absent "$source" "/Users/chenzeren" "portable Codex automation source"

    actual_id="$(awk -F '"' '/^id = / {print $2; exit}' "$source")"
    if [[ "$actual_id" == "$expected_id" ]]; then
      ok "Codex automation id matches directory: $expected_id"
    else
      fail "Codex automation id '$actual_id' does not match directory '$expected_id'"
    fi

    check_regular_file "$target"
    [[ -f "$target" ]] || continue
    actual_id="$(awk -F '"' '/^id = / {print $2; exit}' "$target")"
    if [[ "$actual_id" == "$expected_id" ]]; then
      ok "installed Codex automation id matches directory: $expected_id"
    else
      fail "installed Codex automation id '$actual_id' does not match directory '$expected_id'"
    fi
  done
}

check_dotfile_links() {
  check_symlink "$PROFILE_ROOT/dotfiles/zsh/zshrc" "$HOME/.zshrc" optional
  check_symlink "$PROFILE_ROOT/dotfiles/zsh/zprofile" "$HOME/.zprofile" optional
  check_symlink "$PROFILE_ROOT/dotfiles/git/gitconfig" "$HOME/.gitconfig" optional
  check_symlink "$PROFILE_ROOT/dotfiles/git/gitignore_global" "$HOME/.gitignore_global" optional
  check_secret_link
}

check_secret_link() {
  local source="$PROFILE_ROOT/dotfiles/secrets/secret.local"
  local target="$HOME/.secret"

  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    ok "symlink: $target"
    return 0
  fi

  if [[ ! -e "$source" ]]; then
    warn "optional secret source unavailable or sandbox-blocked: $source"
    return 0
  fi

  check_symlink "$source" "$target" optional
}

check_codex_config() {
  local config="$PROFILE_ROOT/agent/codex/config.toml"
  local syncer="$REPO_ROOT/shared/hooks/codex-sync-config.py"
  [[ -f "$config" ]] || {
    fail "Codex config missing: $config"
    return 0
  }

  if [[ -f "$syncer" && -f "$config" ]] && command -v python3 >/dev/null 2>&1; then
    python3 "$syncer" --config "$config" --output "$config" >/dev/null
  fi

  if awk '
    /^\[hooks\.state(\.|])/{in_hooks_state=1; next}
    /^\[/{in_hooks_state=0}
    !in_hooks_state && /\/Users\/chenzeren/{found=1}
    END{exit found ? 0 : 1}
  ' "$config"; then
    fail "Codex config contains hard-coded /Users/chenzeren outside hooks.state"
  else
    ok "Codex config has no portable-path violations"
  fi

  if [[ -f "$syncer" ]]; then
    if command -v python3 >/dev/null 2>&1; then
      if python3 "$syncer" --config "$config" --output "$config" --check >/dev/null 2>&1; then
        ok "Codex config paths are normalized"
      else
        fail "Codex config contains machine-local home paths"
      fi
    else
      fail "python3 missing for Codex config sync hook"
    fi
  else
    fail "Codex config sync missing: $syncer"
  fi

  if command -v codex >/dev/null 2>&1; then
    local temp_codex_home
    temp_codex_home="$(mktemp -d "${TMPDIR:-/tmp}/agent-dotfiles-codex.XXXXXX")"
    cp "$config" "$temp_codex_home/config.toml"
    if CODEX_HOME="$temp_codex_home" codex features list >/dev/null 2>&1; then
      python3 "$syncer" --config "$config" --output "$config" >/dev/null
      ok "portable Codex config loads"
    else
      python3 "$syncer" --config "$config" --output "$config" >/dev/null
      fail "portable Codex config did not load with CODEX_HOME=$PROFILE_ROOT/agent/codex"
    fi
    rm -rf "$temp_codex_home"
  else
    warn "codex command unavailable, skipping portable config load check"
  fi
}

check_git_hooks_path() {
  local hooks_path
  hooks_path="$(git -C "$REPO_ROOT" config --get core.hooksPath || true)"
  if [[ "$hooks_path" == ".githooks" ]]; then
    ok "git core.hooksPath is .githooks"
  else
    fail "git core.hooksPath is '$hooks_path', expected .githooks"
  fi

  if [[ -x "$REPO_ROOT/.githooks/pre-commit" ]]; then
    ok "git pre-commit hook is executable"
  else
    fail "git pre-commit hook missing or not executable"
  fi
}

check_runtime_tools() {
  check_command brew
  check_command python3
  check_command uv
  check_command node
  check_command npm
  check_command git-lfs
  check_command codex
  check_command mcp-launcher
  check_optional_command mas

  if [[ -x "$HOME/.local/bin/zotero-mcp-wrapper" ]]; then
    ok "zotero-mcp-wrapper installed"
  else
    fail "zotero-mcp-wrapper missing or not executable at ~/.local/bin/zotero-mcp-wrapper"
  fi

  check_agent_python
}

check_agent_python() {
  local python="$HOME/.local/share/agent-dotfiles/python/bin/python"
  if [[ -x "$python" ]]; then
    ok "shared agent Python available: $python"
  else
    warn "shared agent Python missing: $python"
  fi
}

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

expand_path() {
  local value="$1"
  case "$value" in
    "~")
      printf '%s\n' "$HOME"
      ;;
    "~/"*)
      printf '%s\n' "$HOME/${value#~/}"
      ;;
    /*)
      printf '%s\n' "$value"
      ;;
    *)
      printf '%s\n' "$REPO_ROOT/$value"
      ;;
  esac
}

main() {
  parse_args "$@"
  validate_args

  check_package_files
  check_local_tools_sources
  check_uv_tools_sources
  check_mas_file
  check_ml_models_file
  check_codex_config
  check_git_hooks_path
  check_runtime_tools
  check_codex_links
  check_codex_automations
  check_dotfile_links

  if [[ "$ERRORS" -gt 0 ]]; then
    printf '[verify] failed with %s error(s) and %s warning(s)\n' "$ERRORS" "$WARNINGS" >&2
    exit 1
  fi

  printf '[verify] passed with %s warning(s)\n' "$WARNINGS"
}

main "$@"
