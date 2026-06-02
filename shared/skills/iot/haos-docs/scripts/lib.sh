#!/usr/bin/env bash

HAOS_SSH_TARGET="${HAOS_SSH_TARGET:-haos}"

log() {
  printf '[haos-docs] %s\n' "$*"
}

die() {
  printf '[haos-docs] error: %s\n' "$*" >&2
  exit 1
}

remote() {
  ssh "$HAOS_SSH_TARGET" "$@"
}

precheck() {
  remote 'ha supervisor info >/dev/null && test -d /config'
}

timestamp() {
  date '+%Y%m%d-%H%M%S'
}
