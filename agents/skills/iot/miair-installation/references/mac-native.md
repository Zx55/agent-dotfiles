# macOS Native MiAir

Use this path when the user does not have an always-on Linux host yet or wants to run MiAir on the current Mac.

## Fixed Paths

- Source: `~/.local/share/miair/src`
- uv-managed Python venv: `~/.local/share/miair/venv`
- launchd-visible launcher: `~/.local/share/miair/bin/MiAir`
- wrapper console script: `~/.local/share/miair/venv/bin/miair-macos-wrapper`
- Config: `~/.config/miair`
- Logs and state: `~/.local/state/miair`
- launchd plist: `~/Library/LaunchAgents/com.user.miair.plist`

MiAir's upstream default config path is `conf` relative to the current working directory. Always pass `--conf-path ~/.config/miair` to avoid config moving when the working directory changes.

## Install

Run:

```bash
scripts/install_macos_native.sh --hostname <mac-lan-ip>
```

The script:

- installs missing Homebrew formulae `ffmpeg` and `portaudio`
- installs missing Homebrew formula `uv`
- clones or updates `https://github.com/KiriChen-Wind/MiAir`
- installs uv-managed Python `3.12` when needed
- creates an independent MiAir venv with `uv venv --python 3.12`
- installs MiAir into that venv with `uv pip`
- installs `agents/tools/miair-macos-wrapper` into that same venv
- writes `~/.local/share/miair/bin/MiAir` as the launchd-visible executable
- writes and loads `com.user.miair.plist`

The script must not install Python packages into system Python or the shared agent Python. MiAir runtime dependencies belong only in `~/.local/share/miair/venv`.
The launchd plist should execute the `MiAir` launcher, not the venv `python` binary directly. This keeps macOS Login Items and Background Items identifiable as MiAir instead of a generic Python process.
The launchd plist must include a PATH containing Homebrew locations so MiAir can find `ffmpeg` during background execution.
The script must not patch files under `~/.local/share/miair/src`. macOS-local behavior belongs in the repo-managed wrapper under `agents/tools/miair-macos-wrapper`. The current wrapper makes AirPlay mDNS prefer the configured `--hostname` when it is an IPv4 address, exports that hostname as `MIAIR_HOSTNAME` before upstream MiAir starts, and publishes the RAOP service through macOS native `dns-sd -R`. The hostname handling avoids a local utun or proxy route such as `198.18.x.x` being used in AirPlay address-sensitive paths. The native `dns-sd` registration ensures the RAOP service appears on the Wi-Fi interface instead of only on loopback.

Use the router-reserved LAN IP as `--hostname`. Do not use `127.0.0.1`, a Tailscale IP, or a Docker/VM IP.

## Service Commands

```bash
launchctl print "gui/$(id -u)/com.user.miair"
launchctl kickstart -k "gui/$(id -u)/com.user.miair"
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.user.miair.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.user.miair.plist"
```

Logs:

```bash
tail -f ~/.local/state/miair/stdout.log
tail -f ~/.local/state/miair/stderr.log
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
- If the IP changed, rerun the installer with the new `--hostname` or update the plist and restart the service.
- The iPhone may need the AirPlay target selected again, but Xiaomi account and speaker configuration do not need to be recreated.

## Common Failures

- iPhone cannot see the device: check same Wi-Fi, no client isolation, multicast allowed, and launchd service running.
- MiAir appears in `dns-sd -B _raop._tcp local` on interface `1` only: verify the wrapper is running and look for `macOS dns-sd RAOP 服务已注册` in `~/.config/miair/miair.log`; the service should also appear on the Wi-Fi interface such as `en0`.
- iPhone sees device but cannot connect: check MiAir is advertising the real Mac LAN IP and macOS firewall is not blocking Python.
- iPhone sees the device but shows "Unable to connect": check `~/.config/miair/miair.log` for `AirPlay mDNS 启动中，IP:`. It must show the LAN IP passed as `--hostname`, not a utun or proxy IP such as `198.18.x.x`.
- Web UI opens but no speakers appear: refresh Xiaomi cookie and verify the speaker is in the Xiaomi account.
- Playback starts then stops: check `~/.config/miair/miair.log` and MiAir stderr for MiNA login or device API errors.
