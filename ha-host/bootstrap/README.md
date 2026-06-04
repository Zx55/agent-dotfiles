# Home Assistant Host Bootstrap

This profile is for preparing a macOS machine to run Home Assistant OS in a VM, with remote access handled through a private network path such as Tailscale unless a stronger reason exists.

The first version is intentionally conservative:

- `audit` collects read-only host facts for planning.
- `verify` checks whether the host looks ready.
- `install` ensures Homebrew exists, installs the minimal host package manifest, installs required uv tools, creates the shared agent Python environment, copies it into a dedicated root-owned HA host service Python at `/usr/local/libexec/agent-dotfiles/ha-host-python`, and sets the AC power policy so the host does not sleep while plugged in.
- `links` symlinks this profile's Codex instructions, config, hooks, skills, and dotfiles into `~/.codex`.
- `tools/orchestrator` contains the host-side orchestration runtime for registered LAN clients, Mac `pf` forwarding, launchd startup/watch jobs, and UTM HAOS startup/watch checks.
- `tools/ps5-ha-bridge` contains an opt-in PS5 to Home Assistant MQTT bridge. It keeps runtime config and Remote Play credentials outside this repository.

Do not automate public SSH exposure, router port forwarding, sleep prevention, VM creation, or Home Assistant OS image setup here until those boundaries are explicitly decided.

Common commands:

```sh
./ha-host/bootstrap/bootstrap.sh audit
./ha-host/bootstrap/bootstrap.sh verify --agent codex
./ha-host/bootstrap/bootstrap.sh install --dry-run
./ha-host/bootstrap/bootstrap.sh links --agent codex --dry-run
```

Host orchestrator source checks:

```sh
PYTHON=/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python
PYTHONPATH=ha-host/tools/orchestrator/src \
  "$PYTHON" -m ha_host_orchestrator.entrypoints.host_startup --check-only --no-require-utun
PYTHONPATH=ha-host/tools/orchestrator/src \
  "$PYTHON" -m ha_host_orchestrator.entrypoints.host_watch --check-only --no-require-utun
PYTHONPATH=ha-host/tools/orchestrator/src \
  "$PYTHON" -m ha_host_orchestrator.entrypoints.haos_start --help
PYTHONPATH=ha-host/tools/orchestrator/src \
  "$PYTHON" -m ha_host_orchestrator.entrypoints.haos_watch --help
```

Launchd installer for the orchestrator:

```sh
./ha-host/tools/orchestrator/scripts/install-launchd.sh --dry-run
./ha-host/tools/orchestrator/scripts/install-launchd.sh --vm-name HAOS-17.3 --load-now
./ha-host/tools/orchestrator/scripts/uninstall-launchd.sh
```

The orchestrator reads registered devices from `~/.router/device.json`, writes host state and logs under `~/.ha_host/`, runs from a root/user runtime copy under `/usr/local/libexec/agent-dotfiles/orchestrator/`, and uses the HA host service Python at `/usr/local/libexec/agent-dotfiles/ha-host-python/bin/python`. Re-run the installer after changing the orchestrator launchd scripts or plist templates.

Read `ha-host/tools/orchestrator/README.md` before changing registered targets or launchd jobs. The root host jobs own dynamic LAN selection, egress checks, and Mac `pf` routing. The user HAOS jobs own UTM startup and HAOS-side network drift detection.

AC power policy:

```sh
sudo pmset -c sleep 0 displaysleep 10 disksleep 0
pmset -g custom
```

This keeps the Mac awake while connected to power, lets the display turn off after 10 minutes, and leaves battery-power settings untouched.

Optional PS5 Home Assistant bridge:

```sh
cd ha-host/tools/ps5-ha-bridge
uv venv --seed .venv
uv pip install --python .venv/bin/python -e .
.venv/bin/ps5-ha-bridge status --host <ps5-ip>
```

Read `ha-host/tools/ps5-ha-bridge/README.md` before pairing. The bridge stores local test credentials under `~/.config/ps5-ha-bridge/credentials` and the future HAOS add-on stores its own credentials under `/config/ps5-ha-bridge/credentials`.

Optional MiAir bridge:

MiAir can run on the same Mac as an AirPlay or DLNA bridge to Xiaomi AI speakers, but it is not part of the HA host bootstrap or orchestrator. Install, update, or repair it only by explicitly using the `miair-installation` setup skill.

For the full HAOS-on-macOS workflow after a Mac reinstall, including UTM setup, backup restore, bridged-network verification, DNS pitfalls, and launchd service setup, use the `haos-macos-installation` setup skill.

Codex config policy:

- symlink Codex instructions from `ha-host/agent/codex/AGENTS.md` into `~/.codex/AGENTS.md`
- symlink profile-managed files from `ha-host/agent/codex/` into `~/.codex`
- install only the IoT skill symlinks present under `ha-host/agent/skills/iot/`, resolving each one to its canonical source under `shared/skills/`
- keep `hooks.json` profile-specific, calling profile-local hook symlinks under `ha-host/agent/codex/hooks/`
- sync runtime Codex config and automation snapshots back only to `ha-host/agent/codex/`
- keep HA host skills and tools separate from master-only research, finance, and desktop automation assets

Likely future decisions:

- whether to switch from the Tailscale standalone app cask to the CLI-only `tailscaled` formula for a stricter unattended setup
- whether Remote Login should be enabled manually or by script
- whether HA OS VM creation stays manual in UTM or gets scripted later
- whether network wake settings belong in install or verify-only documentation
- whether public SSH is forbidden by default or allowed behind an explicit hardening checklist
