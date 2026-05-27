# Launchd Service For haos-mac-router

Use a service only after manual `haos-mac-router.sh apply` and HAOS network settings are proven.

The router tool is intentionally a pure command tool. Service management belongs in this setup workflow, not inside the tool itself.

## When To Install

Install a service when:

- HAOS is intended to stay in bridged networking.
- HAOS uses the Mac LAN IP as its gateway.
- `ha network info` shows `host_internet: true` and `supervisor_internet: true`.
- Docker registry reachability returns `HTTP/2 401`.
- The Mac has Clash Verge Rev or another stable TUN/proxy path when proxy egress is required.

Do not install a service while still experimenting with HAOS IP, DNS, or UTM network mode.

## Skill Service Files

The skill carries the service wrapper and plist for the current HAOS host:

```text
agents/skills/iot/haos-macos-installation/scripts/haos-mac-router-launchd.sh
agents/skills/iot/haos-macos-installation/scripts/install-haos-mac-router-service.sh
agents/skills/iot/haos-macos-installation/scripts/uninstall-haos-mac-router-service.sh
agents/skills/iot/haos-macos-installation/templates/com.user.haos-mac-router.plist
```

The wrapper waits until the Mac route to `1.1.1.1` uses a `utun` interface, then calls the pure router tool:

```sh
haos-mac-router.sh apply \
  --haos-ip 192.168.71.89 \
  --haos-prefix 24 \
  --haos-interface enp0s1 \
  --lan-interface en0 \
  --mac-lan-ip 192.168.71.70 \
  --egress-interface <detected-utun> \
  --dns 1.1.1.1 \
  --yes
```

This avoids the common boot-order issue where launchd runs before Clash Verge TUN mode is ready and the plain tool would auto-detect `en0`.

The plist in `templates/` is only a template. The installer renders it with concrete values before copying it to `/Library/LaunchDaemons`.

By default, the installer queries:

```sh
ssh haos 'ha network info'
```

It uses that output to discover HAOS IP, prefix, and interface. It also uses the Mac route to the HAOS IP to infer the LAN interface, reads the Mac LAN IP from that interface, then validates the rendered plist before installation.

The validated host rendered values were:

```text
HAOS_IP=192.168.71.89
MAC_LAN_IP=192.168.71.70
LAN_INTERFACE=en0
HAOS_INTERFACE=enp0s1
DNS_SERVER=1.1.1.1
```

If auto-detection is unavailable or wrong, pass explicit installer arguments instead of editing the template:

```sh
./agents/skills/iot/haos-macos-installation/scripts/install-haos-mac-router-service.sh \
  --haos-ip 192.168.71.89 \
  --haos-interface enp0s1 \
  --lan-interface en0 \
  --mac-lan-ip 192.168.71.70 \
  --dns 1.1.1.1
```

The installer copies the wrapper and router tool into:

```text
/usr/local/libexec/agent-dotfiles/haos-mac-router/
```

Do not run a LaunchDaemon directly from `~/Documents/...`. macOS privacy controls can block root launchd jobs from executing files under the user's Documents folder with `Operation not permitted`.

The plist uses `KeepAlive` with `SuccessfulExit=false` and `ThrottleInterval=30`, so launchd retries only when the wrapper exits unsuccessfully. After a successful apply, it does not keep reapplying in a tight loop.

## LaunchDaemon Runtime

Create a root LaunchDaemon so the rules can be applied after Mac boot. Use absolute paths. The checked-in plist template is the source of truth:

Source:

```text
agents/skills/iot/haos-macos-installation/templates/com.user.haos-mac-router.plist
```

Installed path:

```text
/Library/LaunchDaemons/com.user.haos-mac-router.plist
```

The installed plist is rendered during installation and contains the concrete `EnvironmentVariables` for that host. Inspect it when debugging:

```sh
plutil -p /Library/LaunchDaemons/com.user.haos-mac-router.plist
```

Runtime files:

```text
/usr/local/libexec/agent-dotfiles/haos-mac-router/haos-mac-router-launchd.sh
/usr/local/libexec/agent-dotfiles/haos-mac-router/haos-mac-router.sh
```

Do not hard-code `utun8` in the plist. The wrapper detects the current `utunN` route to `1.1.1.1` and passes that interface to the pure router tool. This is more robust across reboots where the `utun` number may change.

## Install

Install the service from the repo:

```sh
cd ~/Documents/codex-workspace/agent-dotfiles
./agents/skills/iot/haos-macos-installation/scripts/install-haos-mac-router-service.sh --dry-run
./agents/skills/iot/haos-macos-installation/scripts/install-haos-mac-router-service.sh
```

Run the installer again after changing `haos-mac-router.sh`, the launchd wrapper, the plist template, or the HAOS network identity. The LaunchDaemon runs the rendered plist and runtime copy under `/usr/local/libexec/agent-dotfiles/haos-mac-router/`, not the repo file directly.

If the skill is executed from a copied location that is not inside `agent-dotfiles`, pass the repo explicitly:

```sh
REPO_ROOT=~/Documents/codex-workspace/agent-dotfiles /path/to/haos-macos-installation/scripts/install-haos-mac-router-service.sh
```

If replacing an existing service, unload it first:

```sh
sudo launchctl bootout system/com.user.haos-mac-router
```

Verify:

```sh
sudo launchctl print system/com.user.haos-mac-router
tail -n 80 /var/log/haos-mac-router.log
tail -n 80 /var/log/haos-mac-router.err
sudo pfctl -a com.apple/agent-dotfiles/haos-mac-router -sr
sudo pfctl -a com.apple/agent-dotfiles/haos-mac-router -sn
ssh haos 'ha network info'
ssh haos 'curl -I --connect-timeout 8 https://registry-1.docker.io/v2/'
```

The service is a one-shot apply job. After a successful run, `launchctl print` may show `state = not running` and `last exit code = 0`; that is healthy. Confirm success from `/var/log/haos-mac-router.log` and the `pf` anchor rules.

If `/var/log/haos-mac-router.err` still contains old `Operation not permitted` lines from an earlier plist that executed `~/Documents/...`, check the installed plist path first:

```sh
plutil -p /Library/LaunchDaemons/com.user.haos-mac-router.plist
```

If `ProgramArguments` points to `/usr/local/libexec/agent-dotfiles/haos-mac-router/haos-mac-router-launchd.sh`, those old errors are stale log history. Clear logs only after confirming the current service is installed correctly:

```sh
sudo truncate -s 0 /var/log/haos-mac-router.log /var/log/haos-mac-router.err
sudo launchctl kickstart -k system/com.user.haos-mac-router
```

## Uninstall

```sh
cd ~/Documents/codex-workspace/agent-dotfiles
./agents/skills/iot/haos-macos-installation/scripts/uninstall-haos-mac-router-service.sh
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh stop --keep-forwarding
```

Use `--keep-forwarding` if another service might rely on IPv4 forwarding. If this Mac only uses forwarding for HAOS, omit it:

```sh
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh stop
```

## Caveats

LaunchDaemons run early. The checked-in wrapper waits for `utun`, but if Clash starts very late or is disabled, the wrapper exits with code `75` and launchd retries. After Clash starts, force a retry with:

```sh
sudo launchctl kickstart -k system/com.user.haos-mac-router
```

If the host intentionally should route HAOS directly through `en0`, set `REQUIRE_UTUN=0` in the wrapper environment or replace the service with a direct call to `haos-mac-router.sh apply`.

If HAOS can reach `version.home-assistant.io` but `registry-1.docker.io` times out, test the Mac itself:

```sh
curl -I --connect-timeout 8 https://registry-1.docker.io/v2/
http_proxy=http://127.0.0.1:7897 https_proxy=http://127.0.0.1:7897 curl -I --connect-timeout 8 https://registry-1.docker.io/v2/
```

If the Mac also times out and `route -n get registry-1.docker.io` or DNS resolves through fake-ip space such as `198.18.0.0/15`, the issue is in Clash/TUN/proxy routing rather than launchd or HAOS. Switching to a working Clash node fixed this in the validated setup. A healthy result is `HTTP/2 401`.
