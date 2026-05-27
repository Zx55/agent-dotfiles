# HAOS Networking On macOS

Use this when HAOS runs in UTM on a Mac and needs both LAN visibility and reliable outbound access.

## Modes

Shared networking/NAT:

- HAOS is reachable from the Mac at a UTM private IP such as `192.168.64.2`.
- Downloads often work because traffic follows the Mac host's path.
- LAN device discovery may be weaker because HAOS is not a first-class LAN peer.

Bridged networking:

- HAOS receives a LAN IP such as `192.168.71.89`.
- Better for mDNS/SSDP/local device discovery.
- HAOS may fail to download from GitHub/GHCR/Docker if the LAN path or IPv6 path is unreliable.

Mac gateway:

- HAOS remains bridged on the LAN.
- HAOS default gateway points to the Mac LAN IP.
- The Mac runs `haos-mac-router.sh apply` to enable IPv4 forwarding and `pf` NAT for the HAOS IP.
- HAOS IPv6 should be disabled to avoid Docker/GHCR choosing broken IPv6 routes.

Do not use Mac gateway mode for a fresh HAOS first boot. Use shared networking/NAT until Terminal & SSH is installed and `ssh haos` works. The Mac gateway flow requires a working HAOS shell because HAOS still needs its static IPv4, gateway, DNS, and IPv6 settings applied from inside HAOS.

## Manual Mac Gateway Flow

Prerequisites:

- HAOS has already completed first boot in UTM shared networking/NAT.
- Terminal & SSH is installed and configured.
- `ssh haos` works from the Mac.
- A full HA backup exists.

Mac side:

```sh
cd ~/Documents/codex-workspace/agent-dotfiles
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh status
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh plan --haos-ip 192.168.71.89 --lan-interface en0
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh apply --haos-ip 192.168.71.89 --lan-interface en0 --dns 1.1.1.1
```

HAOS side:

```sh
ha network info
ha network update enp0s1 \
  --ipv4-method static \
  --ipv4-address 192.168.71.89/24 \
  --ipv4-gateway 192.168.71.70 \
  --ipv4-nameserver 1.1.1.1 \
  --ipv4-nameserver 8.8.8.8 \
  --ipv6-method disabled
ha host reboot
```

Use the actual interface name from `ha network info`; do not assume `enp0s1` if HAOS reports a different interface.

## DNS Pitfall

Do not assume the home router DNS is usable after HAOS points its gateway to the Mac. In testing, `192.168.71.1` caused:

- `host_internet: false`
- `supervisor_internet: false`
- Resolution issues `dns_server_failed` and `dns_server_ipv6_error`
- app installation blocked with `no host internet connection`

The same system had working HTTPS and Docker registry connectivity after using public DNS:

```text
nameservers:
- 1.1.1.1
- 8.8.8.8
```

In a Clash Verge TUN setup, DNS may resolve public domains to fake IPs in `198.18.0.0/15`. That can be expected when Clash owns the route.

## Docker Registry Pitfall

Docker-related domains do not all fail the same way. In the validated setup:

- `version.home-assistant.io` returned `HTTP/2 200`.
- `auth.docker.io/token` returned `HTTP/2 405`.
- `ghcr.io/v2/` returned `HTTP/2 405`.
- `pkg-containers.githubusercontent.com/` returned `HTTP/2 400`.
- `registry-1.docker.io/v2/` initially timed out from both HAOS and the Mac.

That pattern means HAOS routing and the Mac gateway are mostly healthy, but the current Clash/TUN egress cannot reach Docker Hub registry. Switch Clash nodes or add an explicit rule for `registry-1.docker.io`/`docker.io`, then test again. The expected successful Docker Hub registry result is:

```text
HTTP/2 401
```

## Verification

Check network state:

```sh
ssh haos 'ha network info'
```

Expected:

```text
host_internet: true
supervisor_internet: true
gateway: 192.168.71.70
nameservers:
- 1.1.1.1
- 8.8.8.8
ipv6:
  method: disabled
```

Check Docker registry reachability:

```sh
ssh haos 'curl -I --connect-timeout 8 https://registry-1.docker.io/v2/'
curl -I --connect-timeout 8 https://registry-1.docker.io/v2/
```

Expected:

```text
HTTP/2 401
```

Check app installation:

```sh
ssh haos 'ha apps install core_mosquitto'
ssh haos 'ha apps info core_mosquitto | grep "^state:"'
```

If installation is blocked, inspect:

```sh
ssh haos 'ha resolution info'
ssh haos 'ha supervisor logs | tail -n 120'
ssh haos 'ha dns info'
ssh haos 'ha dns logs | tail -n 120'
```

## Mac-Side Checks

Check the `pf` anchor:

```sh
sudo pfctl -a com.apple/agent-dotfiles/haos-mac-router -sr
sudo pfctl -a com.apple/agent-dotfiles/haos-mac-router -sn
sysctl net.inet.ip.forwarding
```

Expected:

```text
pass in quick on en0 inet from <haos-ip> to any
pass out quick on <egress-interface> inet from <haos-ip> to any
nat on <egress-interface> inet from <haos-ip> to any -> (<egress-interface>)
net.inet.ip.forwarding: 1
```

If Clash/TUN is suspected, test with `--egress-interface en0` temporarily. If direct `en0` works but TUN does not, the Mac forwarding layer is healthy and the issue is in proxy/TUN handling.
