#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Download and verify an official Ubuntu Server ARM64 ISO.

Usage:
  download_ubuntu_server.sh --version <release> [options]

Options:
  --version <release>     Exact Ubuntu release, for example 26.04 or 24.04.4.
  --output-dir <path>     Destination directory. Default: ~/.cache/vm/ubuntu
  --metadata-only        Print the ISO URL and official SHA256 without downloading it.
  -h, --help             Show this help.
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

version=""
output_dir="${HOME}/.cache/vm/ubuntu"
metadata_only=0

while (($# > 0)); do
  case "$1" in
    --version)
      (($# >= 2)) || die "--version requires a value"
      version="$2"
      shift 2
      ;;
    --output-dir)
      (($# >= 2)) || die "--output-dir requires a value"
      output_dir="$2"
      shift 2
      ;;
    --metadata-only)
      metadata_only=1
      shift
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

[[ -n "$version" ]] || die "--version is required"
[[ "$version" =~ ^[0-9]{2}\.[0-9]{2}(\.[0-9]+)?$ ]] || die "invalid release format: $version"

for command_name in curl shasum awk mktemp; do
  command -v "$command_name" >/dev/null 2>&1 || die "required command not found: $command_name"
done

release_base="https://cdimage.ubuntu.com/ubuntu/releases/${version}/release"
filename="ubuntu-${version}-live-server-arm64.iso"
iso_url="${release_base}/${filename}"
sums_url="${release_base}/SHA256SUMS"
sums_file="$(mktemp -t ubuntu-sha256sums.XXXXXX)"
trap 'rm -f "$sums_file"' EXIT

printf 'Fetching checksums: %s\n' "$sums_url"
curl --fail --location --retry 3 --silent --show-error \
  --output "$sums_file" "$sums_url"

expected_sha256="$({
  awk -v filename="$filename" '
    {
      listed = $2
      sub(/^\*/, "", listed)
      if (listed == filename) {
        print $1
        exit
      }
    }
  ' "$sums_file"
})"

[[ "$expected_sha256" =~ ^[0-9a-fA-F]{64}$ ]] || \
  die "${filename} was not found in the official SHA256SUMS for ${version}"

printf 'ISO URL: %s\n' "$iso_url"
printf 'SHA256:  %s\n' "$expected_sha256"

if ((metadata_only)); then
  exit 0
fi

mkdir -p "$output_dir"
destination="${output_dir}/${filename}"
partial="${destination}.part"

if [[ -f "$destination" ]]; then
  actual_sha256="$(shasum -a 256 "$destination" | awk '{print $1}')"
  if [[ "$actual_sha256" == "$expected_sha256" ]]; then
    printf 'Already verified: %s\n' "$destination"
    exit 0
  fi
  die "existing ISO failed checksum verification: ${destination}"
fi

printf 'Downloading to: %s\n' "$destination"
curl --fail --location --retry 3 --continue-at - \
  --output "$partial" "$iso_url"

actual_sha256="$(shasum -a 256 "$partial" | awk '{print $1}')"
if [[ "$actual_sha256" != "$expected_sha256" ]]; then
  rm -f "$partial"
  die "downloaded ISO failed checksum verification"
fi

mv "$partial" "$destination"
printf 'Verified ISO: %s\n' "$destination"
