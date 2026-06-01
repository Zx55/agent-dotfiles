#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/KiriChen-Wind/MiAir.git"
REF="main"
HOSTNAME=""
BASE_DIR="/opt/miair"
SRC_DIR="$BASE_DIR/src"
CONF_DIR="$BASE_DIR/conf"
IMAGE_NAME="miair:local"
CONTAINER_NAME="miair"

usage() {
  cat <<'USAGE'
Usage: install_linux_docker.sh --hostname <host-lan-ip> [--ref <git-ref>]

Installs MiAir on Linux Docker with fixed paths:
  source: /opt/miair/src
  config: /opt/miair/conf
  container: miair
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
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ "$(uname -s)" != "Linux" ]; then
  echo "This installer is for Linux Docker hosts only." >&2
  exit 2
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo or as root." >&2
  exit 1
fi

if [ -z "$HOSTNAME" ] || [ "$HOSTNAME" = "127.0.0.1" ]; then
  echo "A real LAN IP is required. Pass --hostname <host-lan-ip>." >&2
  exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required before running this installer." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required before running this installer." >&2
  exit 1
fi

mkdir -p "$BASE_DIR" "$CONF_DIR"

if [ -d "$SRC_DIR/.git" ]; then
  git -C "$SRC_DIR" fetch --tags origin
  git -C "$SRC_DIR" checkout "$REF"
  if [ "$REF" = "main" ]; then
    git -C "$SRC_DIR" pull --ff-only origin main
  fi
elif [ -e "$SRC_DIR" ]; then
  echo "Source path exists but is not a git checkout: $SRC_DIR" >&2
  exit 1
else
  git clone "$REPO_URL" "$SRC_DIR"
  git -C "$SRC_DIR" checkout "$REF"
fi

docker build -t "$IMAGE_NAME" "$SRC_DIR"
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

docker run -d \
  --name "$CONTAINER_NAME" \
  --network=host \
  -e TZ=Asia/Shanghai \
  -e MIAIR_HOSTNAME="$HOSTNAME" \
  -e MIAIR_DOCKER=1 \
  -v "$CONF_DIR:/app/conf" \
  --restart unless-stopped \
  --cap-add=NET_ADMIN \
  --cap-add=NET_BIND_SERVICE \
  --cap-add=NET_BROADCAST \
  --entrypoint /bin/sh \
  "$IMAGE_NAME" \
  -c 'if [ ! -f /app/conf/config.json ]; then cp /app/config-example.json /app/conf/config.json; fi && if [ ! -f /app/conf/.env ]; then cp /app/.env.example /app/conf/.env; fi && exec python miair.py --conf-path /app/conf --hostname "$MIAIR_HOSTNAME"'

echo "MiAir Linux Docker install complete."
echo "Source: $SRC_DIR"
echo "Config: $CONF_DIR"
echo "Container: $CONTAINER_NAME"
echo "Web UI: http://$HOSTNAME:8300"
echo "Logs: docker logs -f $CONTAINER_NAME"
