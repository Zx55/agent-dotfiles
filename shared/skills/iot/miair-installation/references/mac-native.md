# macOS Native MiAir

Use this path when the user does not have an always-on Linux host yet or wants to run MiAir on the current Mac.

## Fixed Paths

- Source: `~/.local/share/miair/src`
- uv-managed Python venv: `~/.local/share/miair/venv`
- launchd-visible launcher: `~/.local/share/miair/bin/miair-core`
- wrapper console script: `~/.local/share/miair/venv/bin/miair-macos-wrapper`
- Config: `~/.config/miair`
- Logs and state: `~/.local/state/miair`
- launchd plist: `~/Library/LaunchAgents/com.user.miair-core.plist`
- IP watcher executable: `~/.local/share/miair/bin/miair-watch`
- IP watcher launchd plist: `~/Library/LaunchAgents/com.user.miair-watch.plist`

MiAir's upstream default config path is `conf` relative to the current working directory. Always pass `--conf-path ~/.config/miair` to avoid config moving when the working directory changes.

## Install

Run:

```bash
scripts/install_macos_native.sh --hostname <mac-lan-ip>
```

If `--hostname` is omitted, the script enumerates macOS hardware ports with `networksetup -listallhardwareports`, chooses an active wired Ethernet-class port first, and falls back to an active Wi-Fi or AirPort port.

The script:

- installs missing Homebrew formulae `ffmpeg` and `portaudio`
- installs missing Homebrew formula `uv`
- clones or updates `https://github.com/KiriChen-Wind/MiAir`
- requires the shared agent Python at `~/.local/share/agent-dotfiles/python/bin/python`
- creates an independent MiAir venv with `~/.local/share/agent-dotfiles/python/bin/python -m venv --copies` so MiAir runtime dependencies stay outside the shared agent Python.
- installs MiAir into that venv with `uv pip`
- installs `ha-host/tools/miair-macos-wrapper` into that same venv
- writes `~/.local/share/miair/bin/miair-core` as the launchd-visible executable
- writes `~/.local/share/miair/bin/miair-watch` as the launchd-visible watcher executable
- writes and loads `com.user.miair-core.plist`
- writes and loads `com.user.miair-watch.plist`

The script must not install Python packages into system Python or the shared agent Python. MiAir runtime dependencies belong only in `~/.local/share/miair/venv`.
The launchd plist should execute the `miair-core` launcher, not the venv `python` binary directly. This keeps macOS Login Items and Background Items identifiable by the service role instead of a generic Python process.
macOS System Settings displays Background Items from the executable basename and the Background Task Management cache, not only from the launchd `Label`. Keep the launchd-visible executable names aligned with the plist labels.
The launchd plist must include a PATH containing Homebrew locations so MiAir can find `ffmpeg` during background execution.
The `miair-core` launcher runs the IP watcher once with `--no-restart` before starting upstream MiAir, then rewrites the current `--hostname` argument from the plist. This makes startup independent of whether launchd happens to start the watcher job before or after the main job.
The script must not patch files under `~/.local/share/miair/src`. macOS-local behavior belongs either in this skill's launchd/watch scripts or in the repo-managed Python package under `ha-host/tools/miair-macos-wrapper`.

## Runtime Wrapper Boundary

Do not move `ha-host/tools/miair-macos-wrapper` into this skill directory. The skill owns installation and operations. The wrapper is runtime code with its own Python package metadata and tests, and the installer installs it into `~/.local/share/miair/venv` with `uv pip install -e`.

The current wrapper makes AirPlay mDNS prefer the configured `--hostname` when it is an IPv4 address, exports that hostname as `MIAIR_HOSTNAME` before upstream MiAir starts, and publishes the RAOP service through macOS native `dns-sd -R`. The hostname handling avoids a local utun or proxy route such as `198.18.x.x` being used in AirPlay address-sensitive paths. The native `dns-sd` registration ensures the RAOP service appears on the Wi-Fi interface instead of only on loopback.

Use the router-reserved LAN IP as `--hostname`. Do not use `127.0.0.1`, a Tailscale IP, or a Docker/VM IP. The IP watcher runs every 5 minutes, enumerates macOS hardware ports, prefers active wired Ethernet-class ports over Wi-Fi, rewrites the MiAir plist when the selected IP differs from `--hostname`, and reloads the MiAir launchd service so the new hostname takes effect.

## IP Watcher

The watcher is a separate launchd job instead of a wrapper around the long-running MiAir process. MiAir keeps its normal `KeepAlive` service as `com.user.miair-core`, while `com.user.miair-watch` runs on `StartInterval=300` and exits after one check.

Selection order:

1. Active hardware ports that are not Wi-Fi or AirPort and are not loopback, bridge, peer-to-peer, tunnel, or VM-style interfaces.
2. Active Wi-Fi or AirPort hardware ports.

The watcher ignores empty, loopback, and link-local addresses. It does not depend on stable interface names. When the selected IP differs from both `ProgramArguments[4]` and `EnvironmentVariables.MIAIR_HOSTNAME` in `com.user.miair-core.plist`, it updates both values, validates the plist, bootstraps the main service again, and kickstarts it.

The watcher restarts MiAir only when the selected IP differs from the plist hostname. If the IP already matches, it exits without touching launchd. This is a bidirectional reconcile, not a one-way fallback. If wired Ethernet goes away, the watcher can move MiAir to Wi-Fi. If wired Ethernet later returns and becomes the preferred active hardware port, the watcher can move MiAir back to the wired address.

Manual check:

```bash
~/.local/share/miair/bin/miair-watch --verbose
```

This command is safe to run repeatedly. It prints a no-change line when the plist already matches the selected IP.

## Service Commands

```bash
launchctl print "gui/$(id -u)/com.user.miair-core"
launchctl print "gui/$(id -u)/com.user.miair-watch"
launchctl kickstart -k "gui/$(id -u)/com.user.miair-core"
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.user.miair-core.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.user.miair-core.plist"
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.user.miair-watch.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.user.miair-watch.plist"
```

Logs:

```bash
tail -f ~/.local/state/miair/stdout.log
tail -f ~/.local/state/miair/stderr.log
tail -f ~/.local/state/miair/ip-watch.log
tail -f ~/.local/state/miair/ip-watch.err.log
tail -f ~/.config/miair/miair.log
```

Web UI:

```text
http://<mac-lan-ip>:8300
```

## Same-Mac AirPlay Discovery

macOS native MiAir is intended for other devices on the LAN, such as iPhone, iPad, or another Mac, to discover and use as an AirPlay target.

The same Mac that is running MiAir may not list its own MiAir AirPlay receiver in Sound output or AirPlay UI, even when Bonjour discovery is healthy. Treat same-Mac visibility as non-authoritative. Verify macOS native MiAir with another Apple device on the LAN.

Useful local checks:

```bash
dns-sd -B _raop._tcp local
system_profiler SPAudioDataType
```

If `dns-sd` shows the MiAir RAOP service on the Wi-Fi interface but macOS Sound does not list it, prefer testing from iPhone/iPad or a different Mac.

## Cookie Login

Prefer cookie login through MiAir Web UI.

1. Open `https://account.xiaomi.com` in a browser and complete Xiaomi login and verification.
2. Obtain `userId` and `passToken` from Xiaomi cookies.
3. In MiAir Web UI, enter those values in the account dialog.
4. Select the Xiaomi speaker and save.

Do not write real cookie values into this repository. MiAir stores them in `~/.config/miair/config.json`.

## Mac Leaves Home

If the Mac leaves the home LAN, AirPlay discovery and playback stop. When it returns:

- If DHCP gives the same reserved IP, launchd should keep or restart MiAir and iPhone should rediscover it.
- If the preferred active hardware port changes between wired Ethernet and Wi-Fi, or if the selected IP changed, the IP watcher should update the plist and restart MiAir within 5 minutes. If it does not, run `miair-watch --verbose` from `~/.local/share/miair/bin`.
- The iPhone may need the AirPlay target selected again, but Xiaomi account and speaker configuration do not need to be recreated.

## Common Failures

- iPhone cannot see the device: check same Wi-Fi, no client isolation, multicast allowed, and launchd service running.
- MiAir appears in `dns-sd -B _raop._tcp local` on interface `1` only: verify the wrapper is running and look for `macOS dns-sd RAOP 服务已注册` in `~/.config/miair/miair.log`; the service should also appear on the active LAN interface.
- iPhone sees device but cannot connect: check MiAir is advertising the real Mac LAN IP and macOS firewall is not blocking Python.
- iPhone sees the device but shows "Unable to connect": check `~/.config/miair/miair.log` for `AirPlay mDNS 启动中，IP:`. It must show the LAN IP passed as `--hostname`, not a utun or proxy IP such as `198.18.x.x`.
- Web UI opens but no speakers appear: refresh Xiaomi cookie and verify the speaker is in the Xiaomi account.
- Playback starts then stops: check `~/.config/miair/miair.log` and MiAir stderr for MiNA login or device API errors.
