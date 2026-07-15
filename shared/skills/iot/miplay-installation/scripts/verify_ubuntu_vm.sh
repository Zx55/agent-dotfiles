#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Verify an Ubuntu Server VM through an SSH target or alias.

Usage:
  verify_ubuntu_vm.sh [options]

Options:
  --target <ssh-target>   SSH alias or user@host. Default: ubuntu
  --expected-ip <ip>     Require this IPv4 address on the guest.
  --allow-missing-agent  Warn instead of failing when qemu-guest-agent is inactive.
  -h, --help             Show this help.
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

pass() {
  printf '[PASS] %s\n' "$*"
}

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  failures=$((failures + 1))
}

warn() {
  printf '[WARN] %s\n' "$*" >&2
}

target="ubuntu"
expected_ip=""
allow_missing_agent=0

while (($# > 0)); do
  case "$1" in
    --target)
      (($# >= 2)) || die "--target requires a value"
      target="$2"
      shift 2
      ;;
    --expected-ip)
      (($# >= 2)) || die "--expected-ip requires a value"
      expected_ip="$2"
      shift 2
      ;;
    --allow-missing-agent)
      allow_missing_agent=1
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

for command_name in ssh awk grep; do
  command -v "$command_name" >/dev/null 2>&1 || die "required command not found: $command_name"
done

ssh_config="$(ssh -G "$target" 2>/dev/null)" || die "cannot resolve SSH target: $target"
resolved_host="$(awk '$1 == "hostname" {print $2; exit}' <<<"$ssh_config")"
resolved_user="$(awk '$1 == "user" {print $2; exit}' <<<"$ssh_config")"
identity_file="$(awk '$1 == "identityfile" {print $2; exit}' <<<"$ssh_config")"

[[ -n "$resolved_host" ]] || die "SSH target has no resolved hostname: $target"

printf 'Target:   %s\n' "$target"
printf 'Host:     %s\n' "$resolved_host"
printf 'User:     %s\n' "$resolved_user"
printf 'Identity: %s\n' "$identity_file"

failures=0

if command -v nc >/dev/null 2>&1; then
  if nc -z -w 3 "$resolved_host" 22 >/dev/null 2>&1; then
    pass "SSH port 22 is reachable"
  else
    fail "SSH port 22 is not reachable"
  fi
else
  warn "nc is unavailable, skipping the direct port check"
fi

remote_output="$(
  ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" '
    set -eu
    printf "hostname=%s\n" "$(hostname)"
    printf "arch=%s\n" "$(uname -m)"
    printf "ips=%s\n" "$(hostname -I | xargs)"
    printf "rootfs=%s\n" "$(findmnt -n -o SOURCE,FSTYPE,SIZE,AVAIL / | xargs)"
    printf "default_route=%s\n" "$(ip route show default | head -n 1)"
    printf "dns=%s\n" "$(resolvectl dns 2>/dev/null | tr "\n" ";" || true)"
    printf "ssh_service=%s\n" "$(systemctl is-active ssh 2>/dev/null || true)"
    printf "qemu_agent=%s\n" "$(systemctl is-active qemu-guest-agent 2>/dev/null || true)"
  '
)" || die "key-only SSH connection failed for target: $target"

printf '\nGuest state:\n%s\n\n' "$remote_output"

arch="$(awk -F= '$1 == "arch" {print $2; exit}' <<<"$remote_output")"
ips="$(awk -F= '$1 == "ips" {sub(/^[^=]*=/, ""); print; exit}' <<<"$remote_output")"
rootfs="$(awk -F= '$1 == "rootfs" {sub(/^[^=]*=/, ""); print; exit}' <<<"$remote_output")"
default_route="$(awk -F= '$1 == "default_route" {sub(/^[^=]*=/, ""); print; exit}' <<<"$remote_output")"
dns="$(awk -F= '$1 == "dns" {sub(/^[^=]*=/, ""); print; exit}' <<<"$remote_output")"
ssh_service="$(awk -F= '$1 == "ssh_service" {print $2; exit}' <<<"$remote_output")"
qemu_agent="$(awk -F= '$1 == "qemu_agent" {print $2; exit}' <<<"$remote_output")"

case "$arch" in
  aarch64|arm64)
    pass "guest architecture is ARM64 (${arch})"
    ;;
  *)
    fail "unexpected guest architecture: ${arch:-unknown}"
    ;;
esac

if [[ -n "$expected_ip" ]]; then
  if [[ " $ips " == *" $expected_ip "* ]]; then
    pass "guest has expected IPv4 address ${expected_ip}"
  else
    fail "guest does not report expected IPv4 address ${expected_ip}"
  fi
fi

[[ -n "$rootfs" ]] && pass "root filesystem is visible (${rootfs})" || fail "root filesystem check returned no data"
[[ -n "$default_route" ]] && pass "default route is configured" || fail "default route is missing"
[[ -n "$dns" ]] && pass "DNS servers are configured" || fail "DNS server check returned no data"
[[ "$ssh_service" == "active" ]] && pass "SSH service is active" || fail "SSH service is not active"

if [[ "$qemu_agent" == "active" ]]; then
  pass "qemu-guest-agent is active"
elif ((allow_missing_agent)); then
  warn "qemu-guest-agent is not active"
else
  fail "qemu-guest-agent is not active"
fi

if ((failures > 0)); then
  printf '\nVerification failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf '\nUbuntu VM verification passed.\n'
