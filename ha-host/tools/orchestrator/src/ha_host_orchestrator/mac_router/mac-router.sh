#!/usr/bin/env bash
set -euo pipefail

TOOL_NAME="mac-router"
ANCHOR="com.apple/agent-dotfiles/mac-router"
STATE_DIR="/var/run/agent-dotfiles"
STATE_FILE="$STATE_DIR/mac-router.state"

COMMAND=""
TARGET_IPS=()
REPLACE_TARGETS=0
LAN_INTERFACE=""
MAC_LAN_IP="auto"
EGRESS_INTERFACE="auto"
DNS_SERVER="auto"
YES=0
KEEP_FORWARDING=0

usage() {
  cat <<'EOF'
Usage:
  mac-router.sh status [options]
  mac-router.sh plan --target-ip IP [--target-ip IP ...] [options]
  sudo mac-router.sh apply --target-ip IP [--target-ip IP ...] [options]
  sudo mac-router.sh stop [--target-ip IP ...] [--keep-forwarding]

Options:
  --target-ip IP           LAN client IPv4 address to route through this Mac. Repeatable.
  --replace-targets        With apply, replace the saved target set instead of appending.
  --lan-interface NAME     Mac LAN interface receiving target traffic. Required.
  --mac-lan-ip IP|auto     Mac LAN IPv4 address. Default: auto from --lan-interface.
  --egress-interface IF    Mac outbound interface for NAT. Default: auto from route to 1.1.1.1.
  --dns IP|auto            DNS server printed in the plan. Default: 1.1.1.1.
  --yes                    Do not prompt before apply.
  --keep-forwarding        With stop, leave net.inet.ip.forwarding unchanged.
  -h, --help               Show this help.

This tool configures only the macOS side. Configure each target device
separately to use the Mac LAN IP as its default gateway.
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
      --target-ip)
        TARGET_IPS+=("${2:-}")
        shift 2
        ;;
      --replace-targets)
        REPLACE_TARGETS=1
        shift
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

join_by_space() {
  local IFS=" "
  printf '%s' "$*"
}

dedupe_ips() {
  local seen=" "
  local ip
  for ip in "$@"; do
    [[ -n "$ip" ]] || continue
    validate_ip "--target-ip" "$ip"
    if [[ "$seen" != *" $ip "* ]]; then
      printf '%s\n' "$ip"
      seen+="$ip "
    fi
  done
}

load_state() {
  FORWARDING_BEFORE=""
  SAVED_TARGET_IPS=""
  SAVED_LAN_INTERFACE=""
  SAVED_MAC_LAN_IP=""
  SAVED_EGRESS_INTERFACE=""
  SAVED_DNS=""

  if [[ -f "$STATE_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$STATE_FILE"
  fi
}

state_targets_array() {
  local target
  for target in ${SAVED_TARGET_IPS:-}; do
    [[ -n "$target" ]] && printf '%s\n' "$target"
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
  if [[ "$DNS_SERVER" != "auto" ]]; then
    printf '%s\n' "$DNS_SERVER"
    return 0
  fi

  printf '1.1.1.1\n'
}

validate_network_args() {
  local mac_ip dns_ip
  [[ -n "$LAN_INTERFACE" ]] || die "--lan-interface is required"
  mac_ip="$(resolved_mac_lan_ip)"
  [[ -n "$mac_ip" ]] || die "could not detect IPv4 address for interface $LAN_INTERFACE"
  validate_ip "--mac-lan-ip" "$mac_ip"

  dns_ip="$(resolved_dns_server)"
  [[ -n "$dns_ip" ]] || die "could not resolve DNS server"
  validate_ip "--dns" "$dns_ip"
}

validate_targets_required() {
  [[ "${#TARGET_IPS[@]}" -gt 0 ]] || die "--target-ip is required for $COMMAND"
  dedupe_ips "${TARGET_IPS[@]}" >/dev/null
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
  load_state

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
  log "state file: $STATE_FILE"
  log "saved targets: ${SAVED_TARGET_IPS:-none}"

  if [[ -d "/Applications/Clash Verge.app" ]]; then
    log "Clash Verge app: installed"
  else
    warn "Clash Verge app not found at /Applications/Clash Verge.app"
  fi
}

print_plan() {
  validate_targets_required
  validate_network_args

  local mac_ip egress dns_ip targets
  mac_ip="$(resolved_mac_lan_ip)"
  egress="$(resolved_egress_interface)"
  dns_ip="$(resolved_dns_server)"
  targets="$(join_by_space $(dedupe_ips "${TARGET_IPS[@]}"))"

  cat <<EOF
[$TOOL_NAME] Plan

Mac side:
  LAN interface:     $LAN_INTERFACE
  Mac LAN IP:        $mac_ip
  Egress interface:  $egress
  Target IPs:        $targets
  pf anchor:         $ANCHOR

Target device settings:
  IPv4 address:      keep each target's current static/reserved LAN IP
  IPv4 gateway:      $mac_ip
  IPv4 DNS:          $dns_ip
  IPv6:              disable on targets that should not bypass this Mac route

Run on Mac:
  sudo $0 apply --replace-targets$(printf ' --target-ip %s' $targets) --lan-interface $LAN_INTERFACE --mac-lan-ip $mac_ip --egress-interface $egress --dns $dns_ip --yes

Rollback on Mac:
  sudo $0 stop
EOF
}

write_state() {
  local forwarding_before="$1"
  local mac_ip="$2"
  local egress="$3"
  local dns_ip="$4"
  shift 4
  local targets=("$@")

  mkdir -p "$STATE_DIR"
  cat > "$STATE_FILE" <<EOF
FORWARDING_BEFORE=$forwarding_before
SAVED_TARGET_IPS="$(join_by_space "${targets[@]}")"
SAVED_LAN_INTERFACE="$LAN_INTERFACE"
SAVED_MAC_LAN_IP="$mac_ip"
SAVED_EGRESS_INTERFACE="$egress"
SAVED_DNS="$dns_ip"
EOF
}

load_pf_rules() {
  local mac_ip="$1"
  local egress="$2"
  shift 2
  local targets=("$@")
  local rules_file target_list target
  rules_file="$(mktemp "${TMPDIR:-/tmp}/mac-router.XXXXXX")"
  target_list=""
  for target in "${targets[@]}"; do
    if [[ -n "$target_list" ]]; then
      target_list+=", "
    fi
    target_list+="$target"
  done

  cat > "$rules_file" <<EOF
# Generated by $TOOL_NAME. Flush with:
#   sudo pfctl -a "$ANCHOR" -F all
table <mac_router_targets> const { $target_list }
lan_if = "$LAN_INTERFACE"
egress_if = "$egress"

nat on \$egress_if inet from <mac_router_targets> to any -> ($egress)
pass in quick on \$lan_if inet from <mac_router_targets> to any keep state
pass out quick on \$egress_if inet from <mac_router_targets> to any keep state
EOF

  pfctl -a "$ANCHOR" -f "$rules_file"
  rm -f "$rules_file"

  log "loaded pf anchor $ANCHOR"
  log "Mac gateway for targets should be $mac_ip"
}

confirm_apply() {
  [[ "$YES" -eq 0 ]] || return 0

  if [[ ! -t 0 ]]; then
    die "refusing non-interactive apply without --yes"
  fi

  printf 'Apply Mac-side forwarding and pf NAT rules for target IPs: %s? [y/N] ' "$(join_by_space "${TARGET_IPS[@]}")"
  local answer
  read -r answer
  [[ "$answer" == "y" || "$answer" == "Y" || "$answer" == "yes" || "$answer" == "YES" ]] || die "aborted"
}

apply_router() {
  require_root
  validate_targets_required
  validate_network_args
  confirm_apply
  load_state

  local mac_ip egress dns_ip forwarding_before pf_before targets_text
  local merged_targets=()
  mac_ip="$(resolved_mac_lan_ip)"
  egress="$(resolved_egress_interface)"
  dns_ip="$(resolved_dns_server)"
  forwarding_before="${FORWARDING_BEFORE:-$(forwarding_status)}"
  pf_before="$(pf_status)"

  [[ "$(anchor_reference_status)" == "present" ]] || warn "/etc/pf.conf does not appear to load com.apple/* anchors"

  if [[ "$REPLACE_TARGETS" -eq 0 ]]; then
    while IFS= read -r target; do
      merged_targets+=("$target")
    done < <(dedupe_ips $(state_targets_array) "${TARGET_IPS[@]}")
  else
    while IFS= read -r target; do
      merged_targets+=("$target")
    done < <(dedupe_ips "${TARGET_IPS[@]}")
  fi

  [[ "${#merged_targets[@]}" -gt 0 ]] || die "target set cannot be empty"

  sysctl -w net.inet.ip.forwarding=1 >/dev/null
  load_pf_rules "$mac_ip" "$egress" "${merged_targets[@]}"

  if [[ "$pf_before" != Enabled* ]]; then
    pfctl -E >/dev/null
    log "enabled pf"
  else
    log "pf already enabled"
  fi

  write_state "$forwarding_before" "$mac_ip" "$egress" "$dns_ip" "${merged_targets[@]}"
  targets_text="$(join_by_space "${merged_targets[@]}")"
  log "applied Mac-side router for targets: $targets_text"
  log "next: set each target device gateway to $mac_ip and DNS to $dns_ip"
}

stop_router() {
  require_root
  load_state

  local remaining_targets=()
  if [[ "${#TARGET_IPS[@]}" -gt 0 ]]; then
    local remove_list=" "
    local target saved mac_ip egress dns_ip
    for target in $(dedupe_ips "${TARGET_IPS[@]}"); do
      remove_list+="$target "
    done

    for saved in $(state_targets_array); do
      if [[ "$remove_list" != *" $saved "* ]]; then
        remaining_targets+=("$saved")
      fi
    done

    if [[ "${#remaining_targets[@]}" -gt 0 ]]; then
      MAC_LAN_IP="${SAVED_MAC_LAN_IP:-$MAC_LAN_IP}"
      LAN_INTERFACE="${SAVED_LAN_INTERFACE:-$LAN_INTERFACE}"
      EGRESS_INTERFACE="${SAVED_EGRESS_INTERFACE:-$EGRESS_INTERFACE}"
      DNS_SERVER="${SAVED_DNS:-$DNS_SERVER}"
      mac_ip="$(resolved_mac_lan_ip)"
      egress="$(resolved_egress_interface)"
      dns_ip="$(resolved_dns_server)"
      load_pf_rules "$mac_ip" "$egress" "${remaining_targets[@]}"
      write_state "${FORWARDING_BEFORE:-$(forwarding_status)}" "$mac_ip" "$egress" "$dns_ip" "${remaining_targets[@]}"
      log "removed targets: $(join_by_space "${TARGET_IPS[@]}")"
      log "remaining targets: $(join_by_space "${remaining_targets[@]}")"
      return 0
    fi
  fi

  pfctl -a "$ANCHOR" -F all >/dev/null 2>&1 || true
  log "flushed pf anchor $ANCHOR"

  if [[ "$KEEP_FORWARDING" -eq 1 ]]; then
    log "left IPv4 forwarding unchanged"
  elif [[ "${FORWARDING_BEFORE:-}" == "0" ]]; then
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
