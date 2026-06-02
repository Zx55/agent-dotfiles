# HAOS Networking On macOS

Use this only to verify or repair the current HAOS-on-UTM network path. The normal routing setup is owned by the HA host orchestrator under `ha-host/tools/orchestrator/`, not by scripts inside this skill.

## Current Model

- HAOS runs as a UTM bridged VM and keeps its own LAN IP.
- HAOS uses the current Mac LAN IP as its default gateway.
- The Mac host orchestrator applies `pf` forwarding for registered devices from `~/.router/device.json`.
- The host orchestrator dynamically selects a usable LAN IP on each run. It prefers wired Ethernet-class ports, falls back to Wi-Fi, and waits for proxy/TUN egress before applying router rules.
- The HAOS watch job checks whether UTM is bridged to the selected Mac LAN interface, updates the VM config and restarts the VM when needed, then uses `utmctl exec` to repair HAOS routing when repair is needed. After a successful check or repair, later unchanged watch runs use `~/.ha_host/haos-watch-state.json` to skip UTM config access and guest-agent calls. SSH is only a post-repair or cached-match health check. The cached path intentionally trusts the last verified UTM bridge. After manual UTM network edits, run the orchestrator doctor or remove the cache so the next watch reads UTM config again.
- Forced bridge restart is enabled by default. If UTM does not stop gracefully before a bridge-interface change, `haos-watch` can force-stop the VM, apply the UTM config change, and start it again. Disable that with `--no-force-bridge-restart` during orchestrator install if manual control is required.
- DNS should use public resolvers such as `1.1.1.1`; avoid depending on the home router DNS when HAOS routes through the Mac.

Fresh HAOS first boot is still safer through UTM shared networking/NAT until onboarding, Terminal & SSH, and a baseline official HA backup are complete. After `ssh haos` works, bridged mode plus the host orchestrator can be verified.

## Checks

Mac host:

```sh
cd ~/Documents/codex-workspace/agent-dotfiles
PYTHON=/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python
PYTHONPATH=ha-host/tools/orchestrator/src \
  "$PYTHON" -m ha_host_orchestrator.entrypoints.host_startup --check-only --no-require-utun
cat ~/.ha_host/state.json
```

HAOS:

```sh
ssh haos 'ha network info'
ssh haos 'ha supervisor info'
ssh haos 'ha dns info'
ssh haos 'curl -I --connect-timeout 8 https://registry-1.docker.io/v2/'
```

Expected HAOS state:

```text
host_internet: true
supervisor_internet: true
ipv4 gateway: <Mac LAN IP>
nameservers include 1.1.1.1
ipv6 method disabled or intentionally managed
```

Expected Docker Registry result is `HTTP/2 401`, which means the network reached the registry and authentication would be required for API access.

## Notes

If HAOS can reach public sites but cannot ping the home router, do not treat that alone as failure. The supported path is HAOS -> Mac gateway -> proxy/TUN or chosen Mac egress.

If Docker or Google domains resolve to `198.18.0.0/15`, that is usually Clash fake-ip behavior and can be normal when the Mac proxy owns egress.
