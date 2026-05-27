# Home Assistant Host Bootstrap

This profile is for preparing a macOS machine to run Home Assistant OS in a VM, with remote access handled through a private network path such as Tailscale unless a stronger reason exists.

The first version is intentionally conservative:

- `audit` collects read-only host facts for planning.
- `verify` checks whether the host looks ready.
- `install` ensures Homebrew exists, installs the minimal host package manifest, installs required uv tools, and creates the shared agent Python environment.
- `links` copies Codex runtime files into `~/.codex` and intentionally keeps hooks disabled.
- `tools/haos-mac-router` contains an opt-in macOS IPv4 forwarding helper for a bridged HAOS VM.

Do not automate public SSH exposure, router port forwarding, sleep prevention, VM creation, or Home Assistant OS image setup here until those boundaries are explicitly decided.

Common commands:

```sh
./bootstrap/bootstrap.sh --profile ha_host audit
./bootstrap/bootstrap.sh --profile ha_host verify
./bootstrap/bootstrap.sh --profile ha_host install --dry-run
./bootstrap/bootstrap.sh --profile ha_host links --dry-run
```

Optional HAOS bridged-router helper:

```sh
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh status
./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh plan --haos-ip 192.168.71.89 --lan-interface en0 --dns 1.1.1.1
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh apply --haos-ip 192.168.71.89 --lan-interface en0 --dns 1.1.1.1
sudo ./bootstrap/ha_host/tools/haos-mac-router/haos-mac-router.sh stop
```

Optional launchd service for the helper:

```sh
./agents/skills/iot/haos-macos-installation/scripts/install-haos-mac-router-service.sh
./agents/skills/iot/haos-macos-installation/scripts/uninstall-haos-mac-router-service.sh
```

The installer queries `ssh haos 'ha network info'` by default and renders the launchd plist with concrete HAOS network values. Pass explicit installer arguments if the `haos` SSH alias is not available or the detected values are wrong.

Re-run the installer after changing the router tool, wrapper, plist template, or HAOS network identity. The service executes a root-owned runtime copy under `/usr/local/libexec/agent-dotfiles/haos-mac-router/`.

Read `bootstrap/ha_host/tools/haos-mac-router/README.md` before using `apply`. The helper touches macOS `pf` and IPv4 forwarding, and it intentionally leaves HAOS network changes as a separate manual step.

For the full HAOS-on-macOS workflow after a Mac reinstall, including UTM setup, backup restore, bridged-network verification, DNS pitfalls, and launchd service setup, use the setup skill at `agents/skills/iot/haos-macos-installation/`.

Codex config policy:

- copy-only from this repository to `~/.codex`
- no symlinked runtime files
- no `hooks.json`
- no runtime-to-repo sync from the HA host
- master remains the profile that keeps the portable Codex config snapshot current

Likely future decisions:

- whether to switch from the Tailscale standalone app cask to the CLI-only `tailscaled` formula for a stricter unattended setup
- whether Remote Login should be enabled manually or by script
- whether HA OS VM creation stays manual in UTM or gets scripted later
- whether host sleep, display sleep, and network wake settings belong in install or verify-only documentation
- whether public SSH is forbidden by default or allowed behind an explicit hardening checklist
