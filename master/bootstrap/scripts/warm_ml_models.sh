#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROFILE_DIR/../.." && pwd)"
PACKAGE_DIR="$PROFILE_DIR/packages"
MODEL_FILE="$PACKAGE_DIR/ml-models.tsv"

log() {
  printf '[ml-models] %s\n' "$*"
}

die() {
  printf '[ml-models] error: %s\n' "$*" >&2
  exit 1
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
    default|"")
      printf '%s\n' "$value"
      ;;
    *)
      printf '%s\n' "$REPO_ROOT/$value"
      ;;
  esac
}

python_for_torch_hub() {
  local agent_python="$HOME/.local/share/agent-dotfiles/python/bin/python"
  local uv_tool_python="$HOME/.local/share/uv/tools/whisperx/bin/python"
  if [[ -x "$agent_python" ]]; then
    printf '%s\n' "$agent_python"
  elif [[ -x "$uv_tool_python" ]]; then
    printf '%s\n' "$uv_tool_python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  else
    die "python3 is required for torch-hub model warming"
  fi
}

hf_command() {
  local agent_hf="$HOME/.local/share/agent-dotfiles/python/bin/hf"
  if [[ -x "$agent_hf" ]]; then
    printf '%s\n' "$agent_hf"
  elif command -v hf >/dev/null 2>&1; then
    command -v hf
  else
    die "hf command missing. Install huggingface-hub into the shared agent Python environment."
  fi
}

warm_hf() {
  local repo_id="$1"
  local target="$2"
  local hf_bin
  hf_bin="$(hf_command)"
  if [[ -z "$target" || "$target" == "default" ]]; then
    log "Downloading Hugging Face model: $repo_id"
    "$hf_bin" download "$repo_id"
  else
    target="$(expand_path "$target")"
    log "Downloading Hugging Face model: $repo_id -> $target"
    "$hf_bin" download "$repo_id" --local-dir "$target"
  fi
}

warm_torch_hub() {
  local repo_id="$1"
  local model="$2"
  [[ -n "$model" && "$model" != "default" ]] || die "torch-hub row requires target model name: $repo_id"
  local python_bin
  python_bin="$(python_for_torch_hub)"
  log "Warming torch hub model: $repo_id / $model"
  "$python_bin" -c 'import sys, torch; torch.hub.load(repo_or_dir=sys.argv[1], model=sys.argv[2], trust_repo=True)' "$repo_id" "$model"
}

warm_url() {
  local url="$1"
  local target="$2"
  [[ -n "$target" && "$target" != "default" ]] || die "url row requires a target path: $url"
  target="$(expand_path "$target")"
  if [[ -s "$target" ]]; then
    log "Model file already exists: $target"
    return 0
  fi
  command -v curl >/dev/null 2>&1 || die "curl is required for url model downloads"
  log "Downloading model file: $url -> $target"
  mkdir -p "$(dirname "$target")"
  local tmp
  tmp="$(mktemp "${target}.tmp.XXXXXX")"
  if curl --fail -L "$url" -o "$tmp"; then
    mv "$tmp" "$target"
  else
    rm -f "$tmp"
    return 1
  fi
}

main() {
  [[ -f "$MODEL_FILE" ]] || die "missing model package file: $MODEL_FILE"

  local line backend id target notes
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="$(trim "$line")"
    [[ -n "$line" ]] || continue
    [[ "$line" != \#* ]] || continue

    IFS=$'\t' read -r backend id target notes <<< "$line"
    backend="$(trim "${backend:-}")"
    id="$(trim "${id:-}")"
    target="$(trim "${target:-}")"
    [[ -n "$backend" && -n "$id" ]] || die "invalid ml model row: $line"

    case "$backend" in
      hf)
        warm_hf "$id" "$target"
        ;;
      torch-hub)
        warm_torch_hub "$id" "$target"
        ;;
      url)
        warm_url "$id" "$target"
        ;;
      *)
        die "unsupported ml model backend '$backend' in row: $line"
        ;;
    esac
  done < "$MODEL_FILE"
}

main "$@"
