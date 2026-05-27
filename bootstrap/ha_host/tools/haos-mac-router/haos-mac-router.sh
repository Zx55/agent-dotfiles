#!/usr/bin/env bash
set -euo pipefail

TOOL_NAME="haos-mac-router"
ANCHOR="com.apple/agent-dotfiles/haos-mac-router"
STATE_DIR="/var/run/agent-dotfiles"
STATE_FILE="$STATE_DIR/haos-mac-router.state"

COMMAND=""
HAOS_IP=""
HAOS_PREFIX="24"
HAOS_INTERFACE="enp0s1"
LAN_INTERFACE="en0"
MAC_LAN_IP="auto"
EGRESS_INTERFACE="auto"
DNS_SERVER="auto"
YES=0
KEEP_FORWARDING=0

usage() {
  cat <<'EOF'
Usage:
  haos-mac-router.sh status [options]
  haos-mac-router.sh plan --haos-ip IP [options]
  sudo haos-mac-router.sh apply --haos-ip IP [options]
  sudo haos-mac-router.sh stop [--keep-forwarding]

Options:
  --haos-ip IP             Bridged HAOS IPv4 address, for example 192.168.71.89.
  --haos-prefix PREFIX     HAOS IPv4 CIDR prefix. Default: 24.
  --haos-interface NAME    HAOS network interface for printed HAOS commands. Default: enp0s1.
  --lan-interface NAME     Mac LAN interface receiving HAOS traffic. Default: en0.
  --mac-lan-ip IP|auto     Mac LAN IPv4 address. Default: auto from --lan-interface.
  --egress-interface IF    Mac outbound interface for NAT. Default: auto from route to 1.1.1.1.
  --dns IP|auto            DNS server printed for HAOS. Default: 1.1.1.1.
  --yes                    Do not prompt before apply.
  --keep-forwarding        With stop, leave net.inet.ip.forwarding unchanged.
  -h, --help               Show this help.

This tool configures only the macOS side. It does not change HAOS networking.
EOF
}

log() {
  printf '[%s] %s\n' "$TOOL_NAME" "$*"
}

warn() {
  printf '[%s] warning: %s\n' "$TOOL_NAME" "$*" >&2
}

die() {
  printf '[%s] error: %s\n' "$TOOL_NAME" "$*" >&2
  exit 1
}

require_macos() {
  [[ "$(uname -s)" == "Darwin" ]] || die "this tool only supports macOS"
}

require_root() {
  [[ "$(id -u)" -eq 0 ]] || die "$COMMAND requires sudo"
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

validate_ip() {
  local name="$1"
  local value="$2"
  is_ipv4 "$value" || die "$name must be an IPv4 address: $value"
}

parse_args() {
  COMMAND="${1:-}"
  case "$COMMAND" in
    status|plan|apply|stop)
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    "")
      usage
      exit 1
      ;;
    *)
      die "unknown command: $COMMAND"
      ;;
  esac

  while [[ $# -gt 0 ]]; do
    case "$1" in
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
      --egress-interface)
        EGRESS_INTERFACE="${2:-}"
        shift 2
        ;;
      --dns)
        DNS_SERVER="${2:-}"
        shift 2
        ;;
      --yes)
        YES=1
        shift
        ;;
      --keep-forwarding)
        KEEP_FORWARDING=1
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

interface_ipv4() {
  local interface="$1"
  local ip
  ip="$(ipconfig getifaddr "$interface" 2>/dev/null || true)"
  if [[ -n "$ip" ]]; then
    printf '%s\n' "$ip"
    return 0
  fi

  ifconfig "$interface" 2>/dev/null | awk '/inet / {print $2; exit}'
}

default_egress_interface() {
  route -n get 1.1.1.1 2>/dev/null | awk '/interface: / {print $2; exit}'
}

gateway_for_interface() {
  local interface="$1"
  netstat -rn -f inet 2>/dev/null | awk -v interface="$interface" '$1 == "default" && $NF == interface {print $2; exit}'
}

fallback_gateway_from_ip() {
  local ip="$1"
  awk -F. '{printf "%s.%s.%s.1\n", $1, $2, $3}' <<< "$ip"
}

resolved_mac_lan_ip() {
  if [[ "$MAC_LAN_IP" != "auto" ]]; then
    printf '%s\n' "$MAC_LAN_IP"
    return 0
  fi

  interface_ipv4 "$LAN_INTERFACE"
}

resolved_egress_interface() {
  if [[ "$EGRESS_INTERFACE" != "auto" ]]; then
    printf '%s\n' "$EGRESS_INTERFACE"
    return 0
  fi

  local interface
  interface="$(default_egress_interface)"
  if [[ -n "$interface" ]]; then
    printf '%s\n' "$interface"
  else
    printf '%s\n' "$LAN_INTERFACE"
  fi
}

resolved_dns_server() {
  local mac_ip="$1"
  if [[ "$DNS_SERVER" != "auto" ]]; then
    printf '%s\n' "$DNS_SERVER"
    return 0
  fi

  printf '1.1.1.1\n'
}

validate_common_plan_args() {
  [[ -n "$HAOS_IP" ]] || die "--haos-ip is required for $COMMAND"
  validate_ip "--haos-ip" "$HAOS_IP"

  [[ "$HAOS_PREFIX" =~ ^[0-9]+$ ]] || die "--haos-prefix must be numeric"
  [[ "$HAOS_PREFIX" -ge 1 && "$HAOS_PREFIX" -le 32 ]] || die "--haos-prefix must be 1-32"

  local mac_ip dns_ip
  mac_ip="$(resolved_mac_lan_ip)"
  [[ -n "$mac_ip" ]] || die "could not detect IPv4 address for interface $LAN_INTERFACE"
  validate_ip "--mac-lan-ip" "$mac_ip"

  dns_ip="$(resolved_dns_server "$mac_ip")"
  [[ -n "$dns_ip" ]] || die "could not resolve DNS server"
  validate_ip "--dns" "$dns_ip"
}

pf_status() {
  pfctl -s info 2>/dev/null | awk -F': ' '/^Status:/ {print $2; exit}'
}

forwarding_status() {
  sysctl -n net.inet.ip.forwarding 2>/dev/null || printf 'unknown\n'
}

anchor_reference_status() {
  if grep -q 'com\.apple/\*' /etc/pf.conf 2>/dev/null; then
    printf 'present\n'
  else
    printf 'missing\n'
  fi
}

print_status() {
  local mac_ip egress gateway
  mac_ip="$(resolved_mac_lan_ip || true)"
  egress="$(resolved_egress_interface || true)"
  gateway="$(gateway_for_interface "$LAN_INTERFACE" || true)"

  log "macOS: $(sw_vers -productVersion 2>/dev/null || true)"
  log "LAN interface: $LAN_INTERFACE"
  log "LAN IPv4: ${mac_ip:-unavailable}"
  log "LAN gateway: ${gateway:-unavailable}"
  log "Auto egress interface: ${egress:-unavailable}"
  log "IPv4 forwarding: $(forwarding_status)"
  log "pf status: $(pf_status)"
  log "pf com.apple anchor reference: $(anchor_reference_status)"
  log "router anchor: $ANCHOR"

  if [[ -d "/Applications/Clash Verge.app" ]]; then
    log "Clash Verge app: installed"
  else
    warn "Clash Verge app not found at /Applications/Clash Verge.app"
  fi
}

print_plan() {
  validate_common_plan_args

  local mac_ip egress dns_ip
  mac_ip="$(resolved_mac_lan_ip)"
  egress="$(resolved_egress_interface)"
  dns_ip="$(resolved_dns_server "$mac_ip")"

  cat <<EOF
[$TOOL_NAME] Plan

Mac side:
  LAN interface:     $LAN_INTERFACE
  Mac LAN IP:        $mac_ip
  Egress interface:  $egress
  HAOS IP:           $HAOS_IP
  pf anchor:         $ANCHOR

HAOS side:
  Interface:         $HAOS_INTERFACE
  IPv4 address:      $HAOS_IP/$HAOS_PREFIX
  IPv4 gateway:      $mac_ip
  IPv4 DNS:          $dns_ip
  IPv6:              disabled

Run on Mac:
  sudo $0 apply --haos-ip $HAOS_IP --haos-prefix $HAOS_PREFIX --haos-interface $HAOS_INTERFACE --lan-interface $LAN_INTERFACE --mac-lan-ip $mac_ip --egress-interface $egress --dns $dns_ip

Run on HAOS after Mac apply:
  ha network info
  ha network update $HAOS_INTERFACE \\
    --ipv4-method static \\
    --ipv4-address $HAOS_IP/$HAOS_PREFIX \\
    --ipv4-gateway $mac_ip \\
    --ipv4-nameserver $dns_ip \\
    --ipv6-method disabled
  ha host reboot

Rollback on HAOS:
  ha network update $HAOS_INTERFACE --ipv4-method auto --ipv6-method auto
  ha host reboot

Rollback on Mac:
  sudo $0 stop
EOF
}

write_state() {
  local forwarding_before="$1"
  local mac_ip="$2"
  local egress="$3"
  local dns_ip="$4"

  mkdir -p "$STATE_DIR"
  cat > "$STATE_FILE" <<EOF
forwarding_before=$forwarding_before
haos_ip=$HAOS_IP
lan_interface=$LAN_INTERFACE
mac_lan_ip=$mac_ip
egress_interface=$egress
dns=$dns_ip
EOF
}

load_pf_rules() {
  local mac_ip="$1"
  local egress="$2"
  local rules_file
  rules_file="$(mktemp "${TMPDIR:-/tmp}/haos-mac-router.XXXXXX.pf")"

  cat > "$rules_file" <<EOF
# Generated by $TOOL_NAME. Flush with:
#   sudo pfctl -a "$ANCHOR" -F all
haos_ip = "$HAOS_IP"
lan_if = "$LAN_INTERFACE"
egress_if = "$egress"

nat on \$egress_if inet from \$haos_ip to any -> ($egress)
pass in quick on \$lan_if inet from \$haos_ip to any keep state
pass out quick on \$egress_if inet from \$haos_ip to any keep state
EOF

  pfctl -a "$ANCHOR" -f "$rules_file"
  rm -f "$rules_file"

  log "loaded pf anchor $ANCHOR"
  log "Mac gateway for HAOS should be $mac_ip"
}

confirm_apply() {
  [[ "$YES" -eq 0 ]] || return 0

  if [[ ! -t 0 ]]; then
    die "refusing non-interactive apply without --yes"
  fi

  printf 'Apply Mac-side forwarding and pf NAT rules for HAOS %s? [y/N] ' "$HAOS_IP"
  local answer
  read -r answer
  [[ "$answer" == "y" || "$answer" == "Y" || "$answer" == "yes" || "$answer" == "YES" ]] || die "aborted"
}

apply_router() {
  require_root
  validate_common_plan_args
  confirm_apply

  local mac_ip egress dns_ip forwarding_before pf_before
  mac_ip="$(resolved_mac_lan_ip)"
  egress="$(resolved_egress_interface)"
  dns_ip="$(resolved_dns_server "$mac_ip")"
  forwarding_before="$(forwarding_status)"
  pf_before="$(pf_status)"

  [[ "$(anchor_reference_status)" == "present" ]] || warn "/etc/pf.conf does not appear to load com.apple/* anchors"

  sysctl -w net.inet.ip.forwarding=1 >/dev/null
  load_pf_rules "$mac_ip" "$egress"

  if [[ "$pf_before" != Enabled* ]]; then
    pfctl -E >/dev/null
    log "enabled pf"
  else
    log "pf already enabled"
  fi

  write_state "$forwarding_before" "$mac_ip" "$egress" "$dns_ip"
  log "applied Mac-side router for HAOS $HAOS_IP"
  log "next: run the printed HAOS network update command from 'plan'"
}

stop_router() {
  require_root

  local forwarding_before=""
  if [[ -f "$STATE_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$STATE_FILE"
  fi

  pfctl -a "$ANCHOR" -F all >/dev/null 2>&1 || true
  log "flushed pf anchor $ANCHOR"

  if [[ "$KEEP_FORWARDING" -eq 1 ]]; then
    log "left IPv4 forwarding unchanged"
  elif [[ "${forwarding_before:-}" == "0" ]]; then
    sysctl -w net.inet.ip.forwarding=0 >/dev/null
    log "restored IPv4 forwarding to 0"
  else
    log "left IPv4 forwarding unchanged"
  fi

  rm -f "$STATE_FILE"
}

main() {
  parse_args "$@"
  require_macos

  case "$COMMAND" in
    status)
      print_status
      ;;
    plan)
      print_plan
      ;;
    apply)
      apply_router
      ;;
    stop)
      stop_router
      ;;
  esac
}

main "$@"
