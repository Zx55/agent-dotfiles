#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-}"
INSTALL_DIR="/usr/local/libexec/agent-dotfiles/haos-mac-router"
PLIST_SRC="$SKILL_DIR/templates/com.user.haos-mac-router.plist"
WRAPPER_SRC="$SKILL_DIR/scripts/haos-mac-router-launchd.sh"
PLIST_DST="/Library/LaunchDaemons/com.user.haos-mac-router.plist"
HAOS_SSH_HOST="haos"
HAOS_IP=""
HAOS_PREFIX=""
HAOS_INTERFACE=""
LAN_INTERFACE=""
MAC_LAN_IP=""
DNS_SERVER="1.1.1.1"
ROUTE_TARGET="1.1.1.1"
REQUIRE_UTUN="1"
WAIT_SECONDS="120"
SLEEP_SECONDS="5"
DRY_RUN="0"

log() {
  printf '[haos-mac-router-service] %s\n' "$*"
}

usage() {
  cat <<'EOF'
Usage:
  install-haos-mac-router-service.sh [options]

Options:
  --haos-host HOST        SSH host used for auto-detection. Default: haos.
  --haos-ip IP           Bridged HAOS IPv4 address. Auto-detected from SSH if omitted.
  --haos-prefix PREFIX   HAOS IPv4 prefix. Auto-detected from SSH, fallback: 24.
  --haos-interface IF    HAOS network interface. Auto-detected from SSH if omitted.
  --lan-interface IF     Mac LAN interface that receives HAOS traffic. Auto-detected if omitted.
  --mac-lan-ip IP        Mac LAN IPv4 address. Uses Mac interface IP if omitted.
  --dns IP               DNS server passed to the router tool. Default: 1.1.1.1.
  --route-target IP      Route probe target used to detect utun egress. Default: 1.1.1.1.
  --no-require-utun      Do not wait for a utun egress route before applying rules.
  --wait-seconds N       Max seconds to wait for egress readiness. Default: 120.
  --sleep-seconds N      Poll interval while waiting for egress readiness. Default: 5.
  --dry-run              Resolve values and validate the rendered plist without installing.
  -h, --help             Show this help.

The script renders templates/com.user.haos-mac-router.plist with concrete
network values, then installs the rendered plist as a root LaunchDaemon.
EOF
}

die() {
  printf '[haos-mac-router-service] error: %s\n' "$*" >&2
  exit 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --haos-host)
        HAOS_SSH_HOST="${2:-}"
        shift 2
        ;;
      --haos-ip)
        HAOS_IP="${2:-}"
        shift 2
        ;;
      --haos-prefix)
        HAOS_PREFIX="${2:-}"
        shift 2
        ;;
      --haos-interface)
        HAOS_INTERFACE="${2:-}"
        shift 2
        ;;
      --lan-interface)
        LAN_INTERFACE="${2:-}"
        shift 2
        ;;
      --mac-lan-ip)
        MAC_LAN_IP="${2:-}"
        shift 2
        ;;
      --dns)
        DNS_SERVER="${2:-}"
        shift 2
        ;;
      --route-target)
        ROUTE_TARGET="${2:-}"
        shift 2
        ;;
      --no-require-utun)
        REQUIRE_UTUN="0"
        shift
        ;;
      --wait-seconds)
        WAIT_SECONDS="${2:-}"
        shift 2
        ;;
      --sleep-seconds)
        SLEEP_SECONDS="${2:-}"
        shift 2
        ;;
      --dry-run)
        DRY_RUN="1"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown option: $1"
        ;;
    esac
  done
}

find_repo_root() {
  local current="$SKILL_DIR"
  while [[ "$current" != "/" ]]; do
    if [[ -x "$current/bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh" ]]; then
      printf '%s\n' "$current"
      return 0
    fi
    current="$(dirname "$current")"
  done
  return 1
}

haos_network_info() {
  ssh -o BatchMode=yes -o ConnectTimeout=5 "$HAOS_SSH_HOST" 'ha network info' 2>/dev/null || true
}

parse_haos_interface() {
  awk '
    /^interfaces:/ {in_interfaces = 1; next}
    in_interfaces && /^[[:space:]]+interface:/ {print $2; exit}
  '
}

parse_haos_cidr() {
  awk '
    /^interfaces:/ {in_interfaces = 1; next}
    in_interfaces && /^[[:space:]]+address:/ {in_address = 1; next}
    in_interfaces && in_address && /^[[:space:]]+-[[:space:]]+[0-9]+\./ {print $2; exit}
  '
}

route_interface_for_ip() {
  local ip="$1"
  route -n get "$ip" 2>/dev/null | awk '/interface: / {print $2; exit}'
}

interface_ipv4() {
  local interface="$1"
  ipconfig getifaddr "$interface" 2>/dev/null || ifconfig "$interface" 2>/dev/null | awk '/inet / {print $2; exit}'
}

is_ipv4() {
  local value="$1"
  [[ "$value" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1

  local IFS=.
  local octets
  read -r -a octets <<< "$value"
  local octet
  for octet in "${octets[@]}"; do
    [[ "$octet" -ge 0 && "$octet" -le 255 ]] || return 1
  done
}

validate_ipv4() {
  local name="$1"
  local value="$2"
  is_ipv4 "$value" || die "$name must be an IPv4 address: $value"
}

validate_number() {
  local name="$1"
  local value="$2"
  [[ "$value" =~ ^[0-9]+$ ]] || die "$name must be numeric: $value"
}

render_plist() {
  local dst="$1"
  cp "$PLIST_SRC" "$dst"

  local name value
  for name in \
    HAOS_IP HAOS_PREFIX HAOS_INTERFACE LAN_INTERFACE MAC_LAN_IP DNS_SERVER \
    ROUTE_TARGET REQUIRE_UTUN WAIT_SECONDS SLEEP_SECONDS; do
    value="${!name}"
    PLACEHOLDER="__${name}__" VALUE="$value" perl -0pi -e 's/\Q$ENV{PLACEHOLDER}\E/$ENV{VALUE}/g' "$dst"
  done

  if grep -q '__[A-Z0-9_][A-Z0-9_]*__' "$dst"; then
    die "rendered plist still contains unresolved placeholders"
  fi
}

resolve_network_values() {
  local info cidr detected_lan detected_mac_ip
  info="$(haos_network_info)"

  if [[ -n "$info" ]]; then
    if [[ -z "$HAOS_INTERFACE" ]]; then
      HAOS_INTERFACE="$(printf '%s\n' "$info" | parse_haos_interface)"
    fi

    cidr="$(printf '%s\n' "$info" | parse_haos_cidr)"
    if [[ -n "$cidr" ]]; then
      if [[ -z "$HAOS_IP" ]]; then
        HAOS_IP="${cidr%/*}"
      fi
      if [[ -z "$HAOS_PREFIX" && "$cidr" == */* ]]; then
        HAOS_PREFIX="${cidr#*/}"
      fi
    fi
  fi

  [[ -n "$HAOS_IP" ]] || die "could not auto-detect HAOS IP from ssh host '$HAOS_SSH_HOST'. Pass --haos-ip."
  HAOS_PREFIX="${HAOS_PREFIX:-24}"
  [[ -n "$HAOS_INTERFACE" ]] || die "could not auto-detect HAOS interface from ssh host '$HAOS_SSH_HOST'. Pass --haos-interface."

  if [[ -z "$LAN_INTERFACE" ]]; then
    detected_lan="$(route_interface_for_ip "$HAOS_IP")"
    LAN_INTERFACE="${detected_lan:-en0}"
  fi

  if [[ -z "$MAC_LAN_IP" ]]; then
    detected_mac_ip="$(interface_ipv4 "$LAN_INTERFACE")"
    MAC_LAN_IP="$detected_mac_ip"
  fi

  validate_ipv4 "--haos-ip" "$HAOS_IP"
  validate_number "--haos-prefix" "$HAOS_PREFIX"
  [[ "$HAOS_PREFIX" -ge 1 && "$HAOS_PREFIX" -le 32 ]] || die "--haos-prefix must be 1-32"
  validate_ipv4 "--mac-lan-ip" "$MAC_LAN_IP"
  validate_ipv4 "--dns" "$DNS_SERVER"
  validate_ipv4 "--route-target" "$ROUTE_TARGET"
  validate_number "--wait-seconds" "$WAIT_SECONDS"
  validate_number "--sleep-seconds" "$SLEEP_SECONDS"

  case "$REQUIRE_UTUN" in
    0|1) ;;
    *) die "--no-require-utun produced invalid REQUIRE_UTUN value: $REQUIRE_UTUN" ;;
  esac
}

parse_args "$@"

if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$(find_repo_root)" || {
    die "could not find agent-dotfiles repo root. Set REPO_ROOT=/path/to/agent-dotfiles."
  }
fi

TOOL_SRC="$REPO_ROOT/bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh"

[[ -x "$TOOL_SRC" ]] || {
  die "router tool not found or not executable: $TOOL_SRC"
}

bash -n "$WRAPPER_SRC"
bash -n "$TOOL_SRC"
plutil -lint "$PLIST_SRC" >/dev/null
resolve_network_values

log "resolved HAOS_IP=$HAOS_IP"
log "resolved HAOS_INTERFACE=$HAOS_INTERFACE"
log "resolved LAN_INTERFACE=$LAN_INTERFACE"
log "resolved MAC_LAN_IP=$MAC_LAN_IP"
log "resolved DNS_SERVER=$DNS_SERVER"

rendered_plist="$(mktemp)"
trap 'rm -f "$rendered_plist"' EXIT
render_plist "$rendered_plist"
plutil -lint "$rendered_plist" >/dev/null

if [[ "$DRY_RUN" == "1" ]]; then
  log "dry-run: rendered plist is valid"
  log "dry-run: no files installed"
  exit 0
fi

log "installing runtime files into $INSTALL_DIR"
sudo install -d -o root -g wheel -m 755 "$INSTALL_DIR"
sudo install -o root -g wheel -m 755 "$WRAPPER_SRC" "$INSTALL_DIR/haos-mac-router-launchd.sh"
sudo install -o root -g wheel -m 755 "$TOOL_SRC" "$INSTALL_DIR/haos-mac-router.sh"

log "installing LaunchDaemon plist"
sudo launchctl bootout system/com.user.haos-mac-router >/dev/null 2>&1 || true
sudo install -o root -g wheel -m 644 "$rendered_plist" "$PLIST_DST"
sudo launchctl bootstrap system "$PLIST_DST"
sudo launchctl kickstart -k system/com.user.haos-mac-router

log "installed com.user.haos-mac-router"
log "logs: /var/log/haos-mac-router.log and /var/log/haos-mac-router.err"
