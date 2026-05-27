# HAOS macOS Host Workflow

Use this for the normal lifecycle after a Mac reinstall or when preparing a dedicated Home Assistant host.

## Fresh Mac Baseline

Assume:

- Apple ID and iCloud sync are complete.
- `agent-dotfiles` is present at `~/Documents/codex-workspace/agent-dotfiles`.
- The current shell can run Homebrew or the bootstrap script can install it.

Run:

```sh
cd ~/Documents/codex-workspace/agent-dotfiles
./bootstrap/bootstrap.sh --profile ha_host install --dry-run
./bootstrap/bootstrap.sh --profile ha_host install
./bootstrap/bootstrap.sh --profile ha_host verify
./bootstrap/bootstrap.sh --profile ha_host links --dry-run
```

Only run `links` for real when the Mac should become the dedicated HA host. The HA host profile copies Codex config into `~/.codex` and intentionally avoids hooks and symlinks.

## Required Host Apps

The `ha_host` Brewfile should provide:

- UTM for the HAOS VM.
- Tailscale for private remote access.
- Clash Verge Rev for Mac-side TUN/proxy routing.
- Codex and the lightweight CLI/tooling needed for remote maintenance.

Keep LaTeX, large media tooling, and other master-only apps out of `ha_host` unless a real HA maintenance workflow needs them.

## First HAOS Boot

Use UTM shared networking/NAT for the initial HAOS boot. The first boot downloads Home Assistant Core and app store data, and there is no reliable command-line path yet because Terminal & SSH is not installed or configured.

Do not start in bridged Mac-gateway mode for a fresh VM. The Mac-side soft router only becomes useful after HAOS has Terminal & SSH, a reachable HA UI, and a known network interface.

After setup:

1. Expand the HAOS disk before installing more apps. A 6 GB qcow2 image can fill up immediately after Core is installed. Use at least 32 GB, preferably 64 GB.
2. Finish HA onboarding in the web UI.
3. Install `Terminal & SSH` from the HA app store in the UI.
4. Configure `Terminal & SSH` in the UI with an SSH public key or temporary password.
5. Start `Terminal & SSH`, enable start-on-boot, and verify web terminal access.
6. Add a local `~/.ssh/config` alias such as `Host haos` and verify `ssh haos`.
7. Install `File editor`.
8. Install `Samba share`.
9. Create a full backup and copy it off HAOS through Samba.

After `ssh haos` works, later add-ons can be installed through CLI, for example:

```sh
ssh haos 'ha apps install core_mosquitto'
```

This does not remove the need to install and configure Terminal & SSH through the UI during the initial NAT phase.

## Switch To Bridged Mac Gateway

Only switch to bridged mode after the NAT baseline is complete:

1. Stop HAOS.
2. Change UTM networking from shared networking/NAT to bridged advanced on the Mac LAN interface.
3. Start HAOS and find the bridged LAN IP from HA UI, router ARP, or `ha network info`.
4. Run `haos-mac-router.sh plan` and `apply` on the Mac.
5. Use `ssh haos` or the web terminal to set HAOS static IPv4 with the Mac LAN IP as gateway, public DNS, and IPv6 disabled.
6. Reboot HAOS and wait several minutes for Core to return.
7. Verify Docker registry reachability and install a small add-on before creating the launchd service.

## Baseline HA Apps

Recommended baseline:

- `Terminal & SSH`: start on boot, watchdog on, sidebar on, SSH public key configured.
- `File editor`: sidebar on, use only for light config edits.
- `Samba share`: expose only needed shares when possible, keep Apple compatibility mode on, keep legacy compatibility off.
- `Mosquitto broker`: install after bridged routing is proven if MQTT devices or integrations are planned. It can be installed from CLI once `ssh haos` works.

## Backups

Create one backup after clean initial setup and another after bridged Mac routing is proven.

Suggested names:

```text
haos-baseline-YYYY-MM-DD
haos-bridged-mac-router-YYYY-MM-DD
```

Copy backups from the Samba `backup` share to the Mac. Do not rely only on HAOS local backup storage.
