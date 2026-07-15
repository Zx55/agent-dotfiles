#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Zx55/MiPlay.git"
REF="codex/fix-macos-airplay1"
HOSTNAME=""
PROXY_URL=""
BASE_DIR="/opt/miplay"
SRC_DIR="$BASE_DIR/src"
CONF_DIR="$BASE_DIR/conf"
IMAGE_NAME="miplay:local"
CONTAINER_NAME="miplay"
DOCKER_PROXY_DROP_IN_DIR="/run/systemd/system/docker.service.d"
DOCKER_PROXY_DROP_IN="$DOCKER_PROXY_DROP_IN_DIR/90-miplay-temporary-proxy.conf"
DOCKER_PROXY_ACTIVE=0

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

disable_temporary_docker_proxy() {
  if [ "$DOCKER_PROXY_ACTIVE" -eq 0 ]; then
    return
  fi

  rm -f "$DOCKER_PROXY_DROP_IN"
  rmdir "$DOCKER_PROXY_DROP_IN_DIR" 2>/dev/null || true
  systemctl daemon-reload
  systemctl restart docker
  DOCKER_PROXY_ACTIVE=0
}

cleanup() {
  local status=$?
  set +e
  disable_temporary_docker_proxy
  return "$status"
}

trap cleanup EXIT

usage() {
  cat <<'USAGE'
Usage: install_miplay.sh --hostname <host-lan-ip> [--repo-url <git-url>] [--ref <git-ref>] [--proxy-url <url>]

Installs MiPlay on the Ubuntu VM with fixed paths:
  source: /opt/miplay/src
  config: /opt/miplay/conf
  container: miplay

Stop or remove any conflicting AirPlay bridge container before running this
installer. The installer does not remove unrelated containers or images.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --hostname)
      HOSTNAME="${2:-}"
      shift 2
      ;;
    --ref)
      REF="${2:-}"
      shift 2
      ;;
    --repo-url)
      REPO_URL="${2:-}"
      shift 2
      ;;
    --proxy-url)
      PROXY_URL="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[ "$(uname -s)" = "Linux" ] || die "this installer is for Linux Docker hosts only"
[ "$(id -u)" -eq 0 ] || die "run with sudo or as root"
[ -n "$HOSTNAME" ] && [ "$HOSTNAME" != "127.0.0.1" ] || \
  die "pass the VM LAN address with --hostname <host-lan-ip>"
[ -n "$REPO_URL" ] || die "repository URL must not be empty"

if [ -n "$PROXY_URL" ] && [[ ! "$PROXY_URL" =~ ^https?://[A-Za-z0-9._-]+:[0-9]+/?$ ]]; then
  die "proxy URL must be an HTTP or HTTPS origin, for example http://127.0.0.1:7897"
fi

command -v docker >/dev/null 2>&1 || die "Docker is required before running this installer"
command -v git >/dev/null 2>&1 || die "git is required before running this installer"
command -v curl >/dev/null 2>&1 || die "curl is required before running this installer"

ensure_conflicting_bridge_stopped() {
  if [ "$(docker inspect -f '{{.State.Running}}' miair 2>/dev/null || true)" = "true" ]; then
    die "the legacy MiAir container is still running; stop or remove it before installing MiPlay"
  fi
}

ensure_conflicting_bridge_stopped

mkdir -p "$BASE_DIR" "$CONF_DIR"

DOCKER_BUILD_ARGS=()
if [ -n "$PROXY_URL" ]; then
  export HTTP_PROXY="$PROXY_URL"
  export HTTPS_PROXY="$PROXY_URL"
  export http_proxy="$PROXY_URL"
  export https_proxy="$PROXY_URL"
  export NO_PROXY="localhost,127.0.0.1,::1,.local,$HOSTNAME,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  export no_proxy="$NO_PROXY"
  DOCKER_BUILD_ARGS+=(
    --network=host
    --build-arg "HTTP_PROXY=$PROXY_URL"
    --build-arg "HTTPS_PROXY=$PROXY_URL"
    --build-arg "http_proxy=$PROXY_URL"
    --build-arg "https_proxy=$PROXY_URL"
    --build-arg "NO_PROXY=$NO_PROXY"
    --build-arg "no_proxy=$NO_PROXY"
  )

  install -m 0755 -d "$DOCKER_PROXY_DROP_IN_DIR"
  cat >"$DOCKER_PROXY_DROP_IN" <<EOF
[Service]
Environment="HTTP_PROXY=$PROXY_URL"
Environment="HTTPS_PROXY=$PROXY_URL"
Environment="NO_PROXY=$NO_PROXY"
EOF
  DOCKER_PROXY_ACTIVE=1
  systemctl daemon-reload
  systemctl restart docker
  ensure_conflicting_bridge_stopped
fi

if [ -d "$SRC_DIR/.git" ]; then
  git -C "$SRC_DIR" remote set-url origin "$REPO_URL"
  git -C "$SRC_DIR" fetch --tags origin
  if ! git -C "$SRC_DIR" diff --quiet || \
     ! git -C "$SRC_DIR" diff --cached --quiet || \
     [ -n "$(git -C "$SRC_DIR" ls-files --others --exclude-standard)" ]; then
    die "source checkout has local changes; preserve or discard them explicitly before reinstalling"
  fi
elif [ -e "$SRC_DIR" ]; then
  die "source path exists but is not a git checkout: $SRC_DIR"
else
  git clone "$REPO_URL" "$SRC_DIR"
fi

if git -C "$SRC_DIR" show-ref --verify --quiet "refs/remotes/origin/$REF"; then
  git -C "$SRC_DIR" checkout -B "$REF" "origin/$REF"
else
  git -C "$SRC_DIR" checkout "$REF"
fi

docker build "${DOCKER_BUILD_ARGS[@]}" -t "$IMAGE_NAME" "$SRC_DIR"
disable_temporary_docker_proxy
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

docker run -d \
  --name "$CONTAINER_NAME" \
  --network=host \
  -e TZ=Asia/Shanghai \
  -e "MIPLAY_HOST=$HOSTNAME" \
  -e WEB_PORT=8300 \
  -v "$CONF_DIR:/app/conf" \
  --restart unless-stopped \
  "$IMAGE_NAME"

ready=0
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:8300/" >/dev/null; then
    ready=1
    break
  fi
  if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null || true)" != "true" ]; then
    break
  fi
  sleep 1
done

if [ "$ready" -ne 1 ]; then
  docker logs --tail 100 "$CONTAINER_NAME" >&2 || true
  die "MiPlay did not expose its Web UI on port 8300"
fi

printf 'MiPlay Linux Docker install complete.\n'
printf 'Source: %s\n' "$SRC_DIR"
printf 'Repository: %s\n' "$REPO_URL"
printf 'Commit: %s\n' "$(git -C "$SRC_DIR" rev-parse HEAD)"
printf 'Config: %s\n' "$CONF_DIR"
printf 'Container: %s\n' "$CONTAINER_NAME"
printf 'Web UI: http://%s:8300\n' "$HOSTNAME"
printf 'Logs: docker logs -f %s\n' "$CONTAINER_NAME"
