# UTM and Ubuntu Server Setup

Use this reference for the manual UTM wizard and Ubuntu Server installer. The values below are a conservative baseline for a small MiPlay and Docker service VM on Apple Silicon.

## Prepare UTM

Verify the stable cask before installing anything:

```bash
brew list --cask utm >/dev/null 2>&1 || brew install --cask utm
test -d /Applications/UTM.app
```

Open UTM and create a new VM. `Open` is only for an existing `.utm` bundle.

## Create The VM

Choose these UTM options:

1. Select `Virtualize`.
2. Select `Linux`.
3. Keep `Use Apple Virtualization` disabled for the validated QEMU path.
4. Select `Boot from ISO image`. Do not select `Import existing drive`.
5. Select the verified `ubuntu-<release>-live-server-arm64.iso`.
6. Allocate 4096 MiB RAM and 4 CPU cores.
7. Keep display output enabled and OpenGL acceleration disabled.
8. Create a 64 GiB virtual disk.
9. Leave the shared directory empty.
10. Name the VM `Services-Linux`, unless the user already has a naming convention.

Sound can be removed. Keep display output until installation, networking, and SSH are verified because it is the recovery console.

Before installing Ubuntu, stop the VM and configure its network according to [networking.md](networking.md). Reboot the installer and confirm it receives an address from the physical LAN rather than UTM's shared-network subnet.

## Install Ubuntu Server

Use these installer choices:

1. Select the normal `Ubuntu Server` install, not `Ubuntu Server (minimized)`.
2. Do not search for third-party drivers for the standard UTM VirtIO devices.
3. Configure networking according to [networking.md](networking.md).
4. Leave the installer proxy empty unless the environment explicitly requires an HTTP installation proxy.
5. Use the default Ubuntu mirror when it passes the installer test.
6. Use the entire 64 GiB virtual disk.
7. Disable LVM for this simple service VM. UTM owns disk growth and snapshots.
8. Do not enable LUKS unless unattended boot is not required and the user accepts manual unlock after every restart.
9. Confirm the resulting layout has an EFI partition and an ext4 root partition using almost all remaining space.
10. Skip Ubuntu Pro unless the user has a specific requirement for it.
11. Install OpenSSH Server. Temporarily allow password authentication until the Mac public key is installed.
12. Do not select featured server snaps. Install Docker and MiPlay later through their documented workflows.
13. Reboot after installation and eject the ISO when prompted.

If the VM boots into the installer again, stop it, eject or remove the ISO drive in UTM, and start it from the virtual disk.

## Initial Guest Setup

After key-based SSH works, update the guest and install the UTM QEMU agent:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent
sudo reboot
```

After reboot, verify the guest before deploying MiPlay:

```bash
uname -m
findmnt -n -o SOURCE,FSTYPE,SIZE,AVAIL /
ip -4 address show scope global
ip route show default
resolvectl status
systemctl is-active ssh qemu-guest-agent
```
