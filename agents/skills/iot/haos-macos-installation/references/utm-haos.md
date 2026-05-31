# UTM HAOS VM Setup

Use official Home Assistant OS generic aarch64 qcow2 images for Apple Silicon Macs.

## Download

Download the current HAOS generic aarch64 qcow2 image from the official Home Assistant OS releases. Store VM images outside the repo, for example:

```text
~/.cache/vm/haos/
```

If downloading `.qcow2.xz`, decompress it before importing into UTM.

## UTM VM Creation

Manual UTM settings that worked for Apple Silicon:

- Virtualize, not emulate.
- Operating system: Other.
- Architecture: ARM64/aarch64.
- System: QEMU ARM virt machine.
- Boot device: none for imported qcow2 disk.
- UEFI: enabled.
- RAM: 4096 MiB minimum.
- CPU: 4 cores is reasonable on an M1 Pro.
- Storage: import the HAOS qcow2 as a VirtIO disk.
- Disk size after setup: at least 32 GB, preferably 64 GB.
- Network for first boot: shared networking/NAT.
- Network for final topology: bridged advanced on the Mac LAN interface, `virtio-net-pci`.

Delete any tiny default placeholder disk before importing the HAOS qcow2. A 196 KB generated disk is not the HAOS system disk.

## Display Output

`Display output is not active` in the UTM window is not necessarily a failure. HAOS is managed through the web UI at port `8123`, through Observer at port `4357`, and through the Terminal & SSH app after it is installed.

## First-Boot Network Rule

Use shared networking/NAT until Home Assistant Core is installed, onboarding is complete, and Terminal & SSH is installed and configured. A fresh HAOS VM cannot be managed through SSH yet, so it cannot safely apply static bridged network settings or use the Mac gateway workflow.

Switch to bridged networking only after:

- The HA dashboard is reachable in NAT mode.
- Terminal & SSH is installed, starts successfully, and is configured for public-key or temporary password access.
- The Mac has a working local SSH alias such as `Host haos`.
- A baseline HA backup exists.

## Expansion

If Core updates, backups, or later add-on installs fail with `not enough free space`, stop HAOS and expand the VirtIO disk in UTM. HAOS usually grows the data partition automatically after reboot. Verify with:

```sh
ssh haos 'df -h /config'
```

Expected after 64 GB expansion: roughly 62 GB total and plenty of free space.

## Restore From Backup

For a fresh VM, use the HA onboarding restore flow if a backup is available. If already inside HA:

1. Upload the backup `.tar` through the UI or copy it through an already configured file-transfer path.
2. Open `Settings -> System -> Backups`.
3. Restore the desired full backup.
4. Re-check SSH, network, and host health after the restore.
