---
name: miplay-installation
description: Prepare and deploy MiPlay in a dedicated Ubuntu Server ARM64 VM on an Apple Silicon Mac. Use when explicitly asked to install UTM, download and verify Ubuntu Server, configure bridged LAN networking and a stable VM address, establish SSH access, install Docker Engine, build the Zx55 MiPlay fork, preserve MiPlay configuration, or verify Xiaomi-speaker AirPlay playback and known macOS limitations.
---

# MiPlay Installation

Build the Linux VM that hosts MiPlay and deploy MiPlay as the only Xiaomi-speaker AirPlay bridge. This is the canonical installation workflow for the Xiaomi-speaker AirPlay bridge.

Run this workflow only on the local Mac. Do not assume UTM, Homebrew, local network interfaces, or personal SSH configuration exists in remote or cloud environments.

## Source Of Truth

- UTM installation and network behavior: `https://docs.getutm.app/`
- Stable UTM Homebrew cask: `https://formulae.brew.sh/cask/utm`
- Ubuntu Server ARM64 releases: `https://ubuntu.com/download/server/arm`
- Ubuntu release checksums: the `SHA256SUMS` file beside the selected ISO
- MiPlay upstream: `https://github.com/juneix/MiPlay`
- Validated macOS compatibility fork: `https://github.com/Zx55/MiPlay`, branch `codex/fix-macos-airplay1`
- Current validated fork commit: `08cddc0ddad231c5636eb4d4020ed32fa1380a45`
- VM runtime state: UTM and the guest disk, not this repository
- SSH runtime state: `~/.ssh/`, not this repository

Never commit a real LAN address, gateway, DNS address, virtual NIC MAC, password, private key, Xiaomi credential, token, cookie, or router credential to this skill.

## Workflow

1. Confirm the target and host.
   - Use an Apple Silicon Mac and an ARM64 Ubuntu Server ISO.
   - Confirm available CPU, memory, storage, the preferred physical LAN interface, and whether the user can manage router DHCP reservations.
   - Prefer wired Ethernet for a stable Layer 2 bridge. Explain any Wi-Fi bridge limitations before using Wi-Fi.
2. Install or verify UTM.
   - Check `brew list --cask utm` and `/Applications/UTM.app` first.
   - Install the stable cask with `brew install --cask utm` only when missing.
3. Select and download Ubuntu.
   - Verify the current Ubuntu Server ARM64 LTS release from the official Ubuntu page at execution time.
   - Use the default ARM64 image, not the `arm64+largemem` image.
   - Run `scripts/download_ubuntu_server.sh --version <release>` to download into `~/.cache/vm/ubuntu` and verify the official SHA256 value.
4. Create and install the VM.
   - Read [references/utm-ubuntu.md](references/utm-ubuntu.md) before guiding the UTM or Ubuntu screens.
   - Use the validated QEMU baseline and keep every user-visible choice explicit.
5. Configure stable LAN networking.
   - Read [references/networking.md](references/networking.md).
   - Use UTM bridged networking so MiPlay can participate directly in LAN discovery and playback traffic.
   - Prefer a router DHCP reservation. Use a guest static IPv4 address only when reservation is unavailable and the address is known to be outside the DHCP pool.
   - When GitHub or Docker Hub is unreachable, use the documented SSH reverse tunnel only for the affected installation or update operation, then close it.
6. Establish SSH management.
   - Read [references/ssh.md](references/ssh.md).
   - Install OpenSSH during Ubuntu setup, add a Mac public key, create an alias, verify non-interactive access, then disable password authentication.
7. Install the guest and Docker baseline.
   - Read [references/networking.md](references/networking.md) before [references/docker-miplay.md](references/docker-miplay.md).
   - Copy `scripts/install_docker.sh` to the VM and run it with `sudo`.
   - Use Docker's official Ubuntu APT repository. Do not use the convenience installer for this persistent service VM.
8. Verify the baseline.
   - Run `scripts/verify_ubuntu_vm.sh --target <ssh-alias> --expected-ip <vm-ip>`.
   - Confirm ARM64, SSH, the expected IPv4 address, root filesystem capacity, default route, DNS, and `qemu-guest-agent`.
9. Deploy MiPlay.
   - Remove or stop any conflicting AirPlay bridge container before deployment. Only one bridge should advertise the Xiaomi speaker.
   - Copy `scripts/install_miplay.sh` to the VM after the VM baseline passes. Do not clone the `agent-dotfiles` repository into the guest.
   - Let the installer clone the validated fork to `/opt/miplay/src`, build `miplay:local`, persist configuration under `/opt/miplay/conf`, and run with host networking.
   - Report the actual repository URL and commit after every deployment. Use `--repo-url` and `--ref` only when intentionally testing another source.
10. Configure and test playback.
   - Complete Xiaomi account and speaker selection in the Web UI. Treat `/opt/miplay/conf` as secret runtime state.
   - Verify playback from an iPhone and from macOS Music.app.
   - State the macOS system-output limitation explicitly. Do not claim Control Center support.

## Known Limitations

- MiPlay exposes each selected Xiaomi speaker as an AirPlay 1 receiver.
- iPhone playback works.
- macOS Music.app playback works with the validated fork fix.
- macOS Control Center cannot currently select MiPlay as the persistent system audio output. The selection may fail or immediately return to the Mac speakers.
- The Control Center failure is not an acceptance failure for this skill. System-wide macOS output requires a compatible AirPlay 2 receiver path and is outside MiPlay's current AirPlay 1 scope.
- Simultaneous playback through Music.app to the Mac and MiPlay can temporarily lose synchronization after seeking.

## Safety Rules

- Do not use UTM `Open` for an ISO. `Open` imports an existing `.utm` bundle. Create a new virtualized Linux VM and select the ISO as boot media.
- Do not regenerate the virtual NIC MAC after creating a router reservation.
- Do not silently guess a static address, gateway, subnet, DNS server, or bridge interface.
- Check whether a proposed static address responds, but explain that no response does not prove it is outside the DHCP pool.
- Keep display output through installation and initial SSH verification. Sound can be removed. OpenGL is unnecessary for a headless server.
- Keep service data on the guest disk. Do not place Docker volumes or databases in a UTM shared directory.
- Never put passwords, Xiaomi credentials, tokens, or cookies in shell history, skill files, screenshots, or repository files.

## Acceptance Criteria

Report concrete evidence for:

- UTM installation and selected virtualization backend
- Ubuntu release, ISO path, and successful SHA256 verification
- VM CPU, memory, disk, display, sound, and network settings
- bridge interface, stable virtual NIC MAC, and stable IP strategy
- guest IPv4 address, default route, DNS, and Internet reachability
- SSH alias and successful key-only login
- ARM64 architecture, root filesystem capacity, and active SSH service
- official Docker APT repository, active Docker service, and successful container smoke test
- MiPlay repository URL, exact commit, local image, running container, `unless-stopped` restart policy, persistent config path, and Web UI
- confirmation that no conflicting AirPlay bridge container or image remains
- successful iPhone and macOS Music.app playback tests
- explicit disclosure that macOS Control Center system-output selection is unsupported
- any residual DHCP collision risk or verification that could not be completed
