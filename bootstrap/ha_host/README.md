# Home Assistant Host Bootstrap

This profile is for preparing a macOS machine to run Home Assistant OS in a VM, with remote access handled through a private network path such as Tailscale unless a stronger reason exists.

The first version is intentionally conservative:

- `audit` collects read-only host facts for planning.
- `verify` checks whether the host looks ready.
- `install` ensures Homebrew exists, installs the minimal host package manifest, installs required uv tools, creates the shared agent Python environment, and copies it into a dedicated root-owned HA host service Python at `/usr/local/libexec/agent-dotfiles/ha-host-python`.
- `links` copies Codex runtime files into `~/.codex` and intentionally keeps hooks disabled.
- `tools/orchestrator` contains the host-side orchestration runtime for registered LAN clients, Mac `pf` forwarding, launchd startup/watch jobs, and UTM HAOS startup/watch checks.
- `tools/ps5-ha-bridge` contains an opt-in PS5 to Home Assistant MQTT bridge. It keeps runtime config and Remote Play credentials outside this repository.

Do not automate public SSH exposure, router port forwarding, sleep prevention, VM creation, or Home Assistant OS image setup here until those boundaries are explicitly decided.

Common commands:

```sh
./bootstrap/bootstrap.sh --profile ha_host audit
./bootstrap/bootstrap.sh --profile ha_host verify
./bootstrap/bootstrap.sh --profile ha_host install --dry-run
./bootstrap/bootstrap.sh --profile ha_host links --dry-run
```

Host orchestrator source checks:

```sh
PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.host_startup --check-only --no-require-utun
PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.host_watch --check-only --no-require-utun
PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.haos_start --help
PYTHONPATH=bootstrap/ha_host/tools/orchestrator/src \
  python3 -m ha_host_orchestrator.entrypoints.haos_watch --help
```

Launchd installer for the orchestrator:

```sh
./bootstrap/ha_host/tools/orchestrator/scripts/install-launchd.sh --dry-run
./bootstrap/ha_host/tools/orchestrator/scripts/install-launchd.sh --vm-name HAOS-17.3 --load-now
./bootstrap/ha_host/tools/orchestrator/scripts/uninstall-launchd.sh
```

The orchestrator reads registered devices from `~/.router/device.json`, writes host state and logs under `~/.ha_host/`, runs from a root/user runtime copy under `/usr/local/libexec/agent-dotfiles/orchestrator/`, and uses the HA host service Python at `/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python`. Re-run the installer after changing the orchestrator launchd scripts or plist templates.

Read `bootstrap/ha_host/tools/orchestrator/README.md` before changing registered targets or launchd jobs. The root host jobs own dynamic LAN selection, egress checks, and Mac `pf` routing. The user HAOS jobs own UTM startup and HAOS-side network drift detection.

Optional PS5 Home Assistant bridge:

```sh
cd bootstrap/ha_host/tools/ps5-ha-bridge
uv venv --seed .venv
uv pip install --python .venv/bin/python -e .
.venv/bin/ps5-ha-bridge status --host <ps5-ip>
```

Read `bootstrap/ha_host/tools/ps5-ha-bridge/README.md` before pairing. The bridge stores local test credentials under `~/.config/ps5-ha-bridge/credentials` and the future HAOS add-on stores its own credentials under `/config/ps5-ha-bridge/credentials`.

Optional MiAir bridge:

MiAir can run on the same Mac as an AirPlay or DLNA bridge to Xiaomi AI speakers, but it is not part of the HA host bootstrap or orchestrator. Install, update, or repair it only by explicitly using the setup skill at `agents/skills/iot/miair-installation/`.

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
