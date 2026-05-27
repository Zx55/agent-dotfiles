# HAOS Mac Router

`haos-mac-router.sh` helps a macOS Home Assistant host act as a narrowly scoped IPv4 gateway for one bridged Home Assistant OS VM.

Use this only when HAOS is running in UTM bridged mode and needs outbound access through the Mac host's proxy/TUN path. For example, HAOS can stay visible on the home LAN for mDNS/SSDP discovery while GitHub/GHCR traffic leaves through the Mac.

This tool only configures the Mac side. It does not modify HAOS network settings.

## Network Model

Example:

```text
HAOS bridged IP: 192.168.71.89
Mac LAN IP:     192.168.71.70
DNS:            1.1.1.1
Mac LAN iface:  en0
Mac egress:     auto, often utunN when Clash Verge TUN mode is active
```

HAOS should use the Mac LAN IP as its default gateway:

```text
HAOS -> Mac en0 -> Mac proxy/TUN/default route -> Internet
```

The Mac side enables IPv4 forwarding and loads a `pf` anchor with NAT/pass rules scoped to the single HAOS IP.

## Prerequisites

- UTM is installed.
- HAOS is switched to UTM bridged networking.
- Clash Verge Rev or another TUN/proxy tool is running on the Mac if the Mac should provide proxied outbound access.
- HAOS SSH or web terminal is available so the HAOS network interface can be configured.
- You know the bridged HAOS IPv4 address and the Mac LAN IPv4 address.

The `ha_host` Brewfile installs `clash-verge-rev`, `utm`, and `tailscale-app`.

## Commands

Show local host state:

```sh
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh status
```

Generate a plan without changing anything:

```sh
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh plan \
  --haos-ip 192.168.71.89 \
  --lan-interface en0 \
  --dns 1.1.1.1
```

Apply the Mac-side router rules:

```sh
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh apply \
  --haos-ip 192.168.71.89 \
  --lan-interface en0 \
  --dns 1.1.1.1
```

Stop the Mac-side router rules:

```sh
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh stop
```

Use `--keep-forwarding` with `stop` if another local service also needs IPv4 forwarding:

```sh
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh stop --keep-forwarding
```

## HAOS Side

This tool does not change HAOS. Use `plan` to print the HAOS network command, then run it from Terminal & SSH or the HAOS web terminal after checking the interface name:

```sh
ha network info
```

Example:

```sh
ha network update enp0s1 \
  --ipv4-method static \
  --ipv4-address 192.168.71.89/24 \
  --ipv4-gateway 192.168.71.70 \
  --ipv4-nameserver 1.1.1.1 \
  --ipv6-method disabled

ha host reboot
```

After reboot, verify:

```sh
ha network info
ha supervisor info
ha resolution info
```

Then install or update a small app to confirm GitHub/GHCR access works.

For installation sequence, DNS pitfalls, and service setup, use the `haos-macos-installation` skill.

## Rollback

On HAOS:

```sh
ha network update enp0s1 --ipv4-method auto --ipv6-method auto
ha host reboot
```

On the Mac:

```sh
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh stop
```

If HAOS becomes unreachable after a bad gateway change, use the UTM console or switch the VM back to shared networking and restore DHCP from the HAOS terminal.

## Safety Notes

- The tool uses the `com.apple/agent-dotfiles/haos-mac-router` `pf` anchor because macOS's default `/etc/pf.conf` loads `com.apple/*` anchors.
- The rules are limited to one HAOS IPv4 address.
- The tool does not edit `/etc/pf.conf`.
- The first version is IPv4-only. Disable HAOS IPv6 for this route to avoid traffic bypassing the Mac route.
- `apply` and `stop` require `sudo`.
- `stop` removes this tool's `pf` anchor. It does not disable `pf` globally.
