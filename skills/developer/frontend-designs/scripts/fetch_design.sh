#!/usr/bin/env zsh

emulate -L zsh
set -u
setopt pipe_fail

if [[ -f "$HOME/.zshrc" ]]; then
  source "$HOME/.zshrc" >/dev/null 2>&1 || true
fi

usage() {
  cat <<'EOF'
Usage:
  fetch_design.sh <brand> [target_dir] [--force]

Examples:
  fetch_design.sh apple
  fetch_design.sh stripe /path/to/project
  fetch_design.sh vercel . --force

Behavior:
  - Runs `npx getdesign@latest add <brand>` in the target directory.
  - Refuses to overwrite an existing DESIGN.md unless --force is passed.
  - If the first network attempt fails and `proxy_on` is available, retries once with the proxy enabled.
EOF
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

brand=""
target_dir="."
force=0

for arg in "$@"; do
  case "$arg" in
    --force)
      force=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$brand" ]]; then
        brand="$arg"
      elif [[ "$target_dir" == "." ]]; then
        target_dir="$arg"
      else
        print -u2 -- "Unexpected argument: $arg"
        usage >&2
        exit 1
      fi
      ;;
  esac
done

if [[ -z "$brand" ]]; then
  print -u2 -- "Missing brand slug."
  usage >&2
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  print -u2 -- "npx is required but was not found. Install Node.js/npm first."
  exit 1
fi

if [[ ! -d "$target_dir" ]]; then
  print -u2 -- "Target directory does not exist: $target_dir"
  exit 1
fi

cd "$target_dir" || exit 1

if [[ -f DESIGN.md && $force -ne 1 ]]; then
  print -- "DESIGN.md already exists in $PWD. Re-run with --force to replace it."
  exit 0
fi

cleanup_proxy() {
  if [[ "${PROXY_ENABLED:-0}" -eq 1 ]]; then
    proxy_off >/dev/null 2>&1 || true
  fi
}

run_fetch() {
  print -- "Fetching DESIGN.md for brand: $brand"
  npx getdesign@latest add "$brand"
}

PROXY_ENABLED=0
trap cleanup_proxy EXIT

if run_fetch; then
  exit 0
fi

status=$?

if whence -w proxy_on >/dev/null 2>&1; then
  print -u2 -- "Initial fetch failed. Retrying once with proxy_on enabled."
  proxy_on >/dev/null 2>&1 || true
  PROXY_ENABLED=1
  if run_fetch; then
    exit 0
  fi
  status=$?
fi

exit "$status"
