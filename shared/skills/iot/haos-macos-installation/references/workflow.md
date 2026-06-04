# HAOS macOS Host Workflow

Use this for the normal lifecycle after a Mac reinstall or when preparing a dedicated Home Assistant host.

## Fresh Mac Baseline

Assume:

- Apple ID and iCloud sync are complete.
- `agent-dotfiles` is present at `~/agent-dotfiles`.
- The current shell can run Homebrew or the bootstrap script can install it.

Run:

```sh
cd ~/agent-dotfiles
./ha-host/bootstrap/bootstrap.sh install --dry-run
./ha-host/bootstrap/bootstrap.sh install
./ha-host/bootstrap/bootstrap.sh verify --agent codex
./ha-host/bootstrap/bootstrap.sh links --agent codex --dry-run
```

Only run `links` for real when the Mac should become the dedicated HA host. The HA host profile installs active agent runtime config by symlinking Codex instructions from `ha-host/agent/codex/AGENTS.md` plus profile-managed runtime config, hooks, skills, and dotfiles.

## Required Host Apps

The `ha_host` Brewfile should provide:

- UTM for the HAOS VM.
- Tailscale for private remote access.
- Clash Verge Rev for Mac-side TUN/proxy routing.
- The agent runtime and lightweight CLI/tooling needed for remote maintenance.

Keep LaTeX, large media tooling, and other master-only apps out of `ha-host` unless a real HA maintenance workflow needs them.

The HA host bootstrap also sets the plugged-in power policy with `pmset`: system sleep disabled, display sleep after 10 minutes, and disk sleep disabled. Battery-power settings are left alone.

## First HAOS Boot

Use UTM shared networking/NAT for the initial HAOS boot. The first boot downloads Home Assistant Core and app store data, and there is no reliable command-line path yet because Terminal & SSH is not installed or configured.

Do not start in bridged Mac-gateway mode for a fresh VM. The Mac-side route only becomes useful after HAOS has Terminal & SSH, a reachable HA UI, and a known network interface.

After setup:

1. Expand the HAOS disk before installing more apps. A 6 GB qcow2 image can fill up immediately after Core is installed. Use at least 32 GB, preferably 64 GB.
2. Finish HA onboarding in the web UI.
3. Install `Terminal & SSH` from the HA app store in the UI.
4. Configure `Terminal & SSH` in the UI with an SSH public key. Use a temporary password only as a break-glass path and do not preserve it in the repo or final answer.
5. Start `Terminal & SSH`, enable start-on-boot, and verify web terminal access.
6. Add a local `~/.ssh/config` alias such as `Host haos`, point it at the HAOS LAN IP and configured SSH key, then verify `ssh haos`.
7. Verify `ssh haos 'ha supervisor info'`, `ssh haos 'ha network info'`, and `ssh haos 'ha resolution info'`.
8. Create an official HA backup before bridge or gateway changes.

After `ssh haos` works, later add-ons and custom integrations are out of scope for this skill. Use the `haos-addons` skill for those docs and scripts.

Do not start add-on installation until `ssh haos 'ha supervisor info'` succeeds.

## Switch To Bridged Mac Gateway

Only switch to bridged mode after the NAT baseline is complete. The normal path is now the HA host orchestrator, not manual UTM and HAOS gateway edits:

1. Ensure HAOS is registered in `~/.router/device.json` if it should be routed through the Mac.
2. Install or repair the orchestrator from `ha-host/tools/orchestrator/`.
3. Load the four launchd jobs and let `haos-watch` reconcile UTM bridged networking and the HAOS default route.
4. Verify `~/.ha_host/state.json`, the UTM bridge interface, `ssh haos 'ha network info'`, `ssh haos 'ha supervisor info'`, Docker registry reachability, and the four launchd jobs.

Do not use SSH as the bridge or gateway repair mechanism. `haos-watch` uses `utmctl exec` through the guest agent for repair, because a stale gateway can make `ssh haos` unreachable. SSH is the final health check after repair.

## Automation Boundary

Required baseline:

- `Terminal & SSH`: install manually first, start on boot, watchdog on, sidebar on, SSH public key configured, and local `ssh haos` alias verified.
- `ssh haos 'ha supervisor info'` must succeed before this skill is considered complete.
- `ssh haos 'ha network info'` must show the expected IPv4 address, gateway, DNS servers, and IPv6 policy.
- `ssh haos 'ha resolution info'` should not show blocking health issues.

Other HA add-ons, custom integrations, and device bridges are intentionally not part of this host-bootstrap skill.

## Backups

Create one official HA backup after clean initial setup and another after bridged Mac routing is proven.

Suggested names:

```text
haos-baseline-YYYY-MM-DD
haos-bridged-mac-gateway-YYYY-MM-DD
```

Use the HA UI backup page or HA CLI:

```sh
ssh haos 'ha backups new --name haos-baseline-YYYY-MM-DD --no-progress'
ssh haos 'ha backups list'
```

Report the backup name and slug. Copy official backup tar files off HAOS when a file-transfer path is available. Do not rely only on HAOS local backup storage for major bridge or gateway changes.
