#!/usr/bin/env bash
set -euo pipefail

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Install the official Docker Engine packages on the MiPlay Ubuntu VM.

Usage:
  install_docker.sh [--registry-mirror <url>] [--proxy-url <url>]

Options:
  --registry-mirror <url>  Configure a Docker Hub registry mirror before the smoke test.
  --proxy-url <url>        Temporarily proxy package downloads and Docker image pulls.
  -h, --help               Show this help.
EOF
}

registry_mirror=""
proxy_url=""
docker_proxy_drop_in_dir="/run/systemd/system/docker.service.d"
docker_proxy_drop_in="$docker_proxy_drop_in_dir/90-miplay-temporary-proxy.conf"
docker_proxy_active=0

disable_temporary_docker_proxy() {
  if ((docker_proxy_active == 0)); then
    return
  fi

  rm -f "$docker_proxy_drop_in"
  rmdir "$docker_proxy_drop_in_dir" 2>/dev/null || true
  systemctl daemon-reload
  systemctl restart docker
  docker_proxy_active=0
}

cleanup() {
  local status=$?
  set +e
  disable_temporary_docker_proxy
  return "$status"
}

trap cleanup EXIT

while (($# > 0)); do
  case "$1" in
    --registry-mirror)
      (($# >= 2)) || die "--registry-mirror requires a value"
      registry_mirror="$2"
      shift 2
      ;;
    --proxy-url)
      (($# >= 2)) || die "--proxy-url requires a value"
      proxy_url="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

if [[ -n "$registry_mirror" && ! "$registry_mirror" =~ ^https?://[^/]+/?$ ]]; then
  die "invalid registry mirror URL: $registry_mirror"
fi

if [[ -n "$proxy_url" && ! "$proxy_url" =~ ^https?://[A-Za-z0-9._-]+:[0-9]+/?$ ]]; then
  die "invalid proxy URL: $proxy_url"
fi

if [[ "$(uname -s)" != "Linux" ]]; then
  die "this installer must run on the Ubuntu VM"
fi

if [[ "$(id -u)" -ne 0 ]]; then
  die "run this installer with sudo or as root"
fi

[[ -r /etc/os-release ]] || die "/etc/os-release is missing"
# shellcheck disable=SC1091
. /etc/os-release

[[ "${ID:-}" == "ubuntu" ]] || die "unsupported distribution: ${ID:-unknown}"

architecture="$(dpkg --print-architecture)"
[[ "$architecture" == "arm64" ]] || die "expected Ubuntu arm64, found: $architecture"

codename="${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}"
[[ -n "$codename" ]] || die "Ubuntu release codename is unavailable"

export DEBIAN_FRONTEND=noninteractive

if [[ -n "$proxy_url" ]]; then
  export HTTP_PROXY="$proxy_url"
  export HTTPS_PROXY="$proxy_url"
  export http_proxy="$proxy_url"
  export https_proxy="$proxy_url"
  export NO_PROXY="localhost,127.0.0.1,::1,.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
  export no_proxy="$NO_PROXY"
fi

apt-get update
apt-get install -y ca-certificates curl git python3 qemu-guest-agent

conflicting_packages=()
for package_name in \
  docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc; do
  if dpkg-query -W -f='${Status}' "$package_name" 2>/dev/null | grep -q 'ok installed$'; then
    conflicting_packages+=("$package_name")
  fi
done

if ((${#conflicting_packages[@]} > 0)); then
  apt-get remove -y "${conflicting_packages[@]}"
fi

install -m 0755 -d /etc/apt/keyrings
curl --fail --silent --show-error --location \
  https://download.docker.com/linux/ubuntu/gpg \
  --output /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

cat >/etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${codename}
Components: stable
Architectures: ${architecture}
Signed-By: /etc/apt/keyrings/docker.asc
EOF

apt-get update
apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

systemctl enable --now docker
systemctl start qemu-guest-agent

if [[ -n "$registry_mirror" ]]; then
  python3 - "$registry_mirror" <<'PY'
import json
import os
import sys

path = "/etc/docker/daemon.json"
mirror = sys.argv[1].rstrip("/")
config: dict[str, object] = {}

if os.path.exists(path):
    with open(path, encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise SystemExit(f"error: {path} must contain a JSON object")
    config = loaded

mirrors = config.get("registry-mirrors", [])
if not isinstance(mirrors, list) or not all(isinstance(item, str) for item in mirrors):
    raise SystemExit(f"error: registry-mirrors in {path} must be a string array")

config["registry-mirrors"] = list(dict.fromkeys([*mirrors, mirror]))
os.makedirs(os.path.dirname(path), mode=0o755, exist_ok=True)
temporary = f"{path}.tmp"
with open(temporary, "w", encoding="utf-8") as handle:
    json.dump(config, handle, indent=2)
    handle.write("\n")
os.chmod(temporary, 0o644)
os.replace(temporary, path)
PY
  systemctl restart docker
fi

if [[ -n "$proxy_url" ]]; then
  install -m 0755 -d "$docker_proxy_drop_in_dir"
  cat >"$docker_proxy_drop_in" <<EOF
[Service]
Environment="HTTP_PROXY=$proxy_url"
Environment="HTTPS_PROXY=$proxy_url"
Environment="NO_PROXY=$NO_PROXY"
EOF
  docker_proxy_active=1
  systemctl daemon-reload
  systemctl restart docker
fi

if ! docker run --rm hello-world >/dev/null; then
  die "Docker is installed, but the Docker Hub smoke test failed"
fi

disable_temporary_docker_proxy

printf 'Ubuntu Docker baseline complete.\n'
printf 'Ubuntu: %s (%s)\n' "${VERSION_ID:-unknown}" "$codename"
printf 'Architecture: %s\n' "$architecture"
printf 'Docker: %s\n' "$(docker version --format '{{.Server.Version}}')"
printf 'Registry mirrors: %s\n' "$(docker info --format '{{json .RegistryConfig.Mirrors}}')"
printf 'Temporary proxy removed: yes\n'
printf 'QEMU guest agent: %s\n' "$(systemctl is-active qemu-guest-agent)"

if [[ -e /var/run/reboot-required ]]; then
  printf 'Reboot required: yes\n'
else
  printf 'Reboot required: no\n'
fi
