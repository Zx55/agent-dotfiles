# Docker Engine and MiPlay Deployment

Use this phase only after the VM has a stable bridged IPv4 address and key-based SSH access. Read [networking.md](networking.md) first. It owns bridge configuration and the temporary SSH proxy tunnel used when GitHub or Docker Hub is unreachable.

## Ownership Boundaries

- This skill owns the Ubuntu VM and official Docker Engine baseline.
- This skill owns its self-contained MiPlay Linux Docker installer.
- The selected MiPlay repository owns the application Dockerfile.
- The guest owns `/opt/miplay` runtime state.
- `/opt/miplay/conf` contains secret runtime configuration and must survive container and image replacement.

Only copy the small installer scripts from the Mac. Do not clone `agent-dotfiles` into the guest.

## Install Docker Engine

Docker officially supports Ubuntu ARM64. Use Docker's APT repository rather than Ubuntu's `docker.io` package or Docker's convenience script.

From the Mac repository root:

```bash
scp shared/skills/iot/miplay-installation/scripts/install_docker.sh \
  <ssh-alias>:/tmp/install_docker.sh
ssh -t <ssh-alias> 'sudo bash /tmp/install_docker.sh'
ssh <ssh-alias> 'rm -f /tmp/install_docker.sh'
```

If direct package or image access fails, start the temporary tunnel from [networking.md](networking.md), then add:

```bash
--proxy-url http://127.0.0.1:7897
```

The script installs Docker Engine, Buildx, Compose, Git, curl, CA certificates, and `qemu-guest-agent`. It enables Docker, starts the guest agent, and runs `hello-world`. It does not add the user to the `docker` group because that group grants root-equivalent access.

Reboot after system package upgrades or when `/var/run/reboot-required` exists:

```bash
ssh -t <ssh-alias> 'sudo apt update && sudo apt full-upgrade -y && sudo reboot'
```

Wait for SSH to return, then run the VM verifier.

## Remove Conflicting Bridges

Only one bridge should advertise the Xiaomi speaker. Inspect existing containers before deployment:

```bash
ssh -t <ssh-alias> 'sudo docker ps -a'
```

If a previous `miair`, test Shairport, or other bridge container is running, stop it explicitly. Remove it only after confirming its persistent configuration is stored outside the container.

## Deploy MiPlay

Copy the installer:

```bash
scp shared/skills/iot/miplay-installation/scripts/install_miplay.sh \
  <ssh-alias>:/tmp/install_miplay.sh
ssh -t <ssh-alias> \
  'sudo bash /tmp/install_miplay.sh --hostname <vm-lan-ip>'
ssh <ssh-alias> 'rm -f /tmp/install_miplay.sh'
```

The default source is the validated fork:

```text
Repository: https://github.com/Zx55/MiPlay.git
Ref: codex/fix-macos-airplay1
Validated commit: 08cddc0ddad231c5636eb4d4020ed32fa1380a45
```

The branch may advance. Always report the exact deployed commit. To reproduce the current validated deployment exactly:

```bash
ssh -t <ssh-alias> \
  'sudo bash /tmp/install_miplay.sh \
    --hostname <vm-lan-ip> \
    --repo-url https://github.com/Zx55/MiPlay.git \
    --ref 08cddc0ddad231c5636eb4d4020ed32fa1380a45'
```

Use `--repo-url` and `--ref` only when intentionally selecting another repository, branch, tag, or commit. If the existing source checkout has local changes, the installer stops instead of discarding them.

When GitHub or Docker image access needs the temporary tunnel, add `--proxy-url http://127.0.0.1:7897`. See [networking.md](networking.md) for the complete start, verification, and shutdown sequence.

The installer:

1. Refuses to continue while a legacy `miair` container is running.
2. Clones or updates the selected MiPlay repository in `/opt/miplay/src`.
3. Builds `miplay:local` from the repository Dockerfile.
4. Persists configuration under `/opt/miplay/conf`.
5. Runs `miplay` with host networking and `--restart unless-stopped`.
6. Passes the VM LAN address through `MIPLAY_HOST`.
7. Waits for the Web UI on port 8300 before reporting success.

Host networking is required for mDNS, RTSP, RTP, RTCP, timing, and dynamic HTTP stream ports. Do not replace it with a short static port mapping list.

## Verify MiPlay

On the VM:

```bash
sudo docker ps --filter name=miplay
sudo docker inspect --format '{{.HostConfig.NetworkMode}} {{.HostConfig.RestartPolicy.Name}}' miplay
sudo docker logs --tail 100 miplay
sudo git -C /opt/miplay/src status --short --branch
sudo git -C /opt/miplay/src remote get-url origin
sudo git -C /opt/miplay/src rev-parse HEAD
sudo test -f /opt/miplay/conf/config.json
curl -fsS http://<vm-lan-ip>:8300/ >/dev/null
```

Expected values include host network mode, `unless-stopped`, the intended repository and commit, a clean checkout, persistent configuration, and a reachable Web UI.

From the Mac, verify the Web UI and AirPlay advertisement:

```bash
curl -I --connect-timeout 5 http://<vm-lan-ip>:8300/
dns-sd -B _raop._tcp local.
```

Stop `dns-sd` after the expected service appears. Complete Xiaomi account setup in the Web UI and keep `/opt/miplay/conf` secret.

## Playback Expectations

Test these paths separately:

1. iPhone to the MiPlay-advertised Xiaomi speaker. Expected to work.
2. macOS Music.app to the MiPlay-advertised Xiaomi speaker. Expected to work with the validated fork.
3. macOS Control Center system output. Known unsupported path. Selection may fail or immediately return to Mac speakers.

Do not diagnose the known Control Center behavior as a bridge, firewall, or Docker failure when the iPhone and Music.app paths pass.

## Clean Old Docker State

After the new container passes configuration and playback checks, remove obsolete test containers, old images, and build cache. Do not delete `/opt/miplay/conf`.

```bash
sudo docker ps -a
sudo docker image prune -af
sudo docker builder prune -af
sudo docker system df
```

The final steady state should contain one running `miplay` container and its `miplay:local` image unless the VM intentionally hosts unrelated Docker services.

## Update

Rerun `scripts/install_miplay.sh` with the same VM address. It preserves `/opt/miplay/conf`, fetches the selected ref, rebuilds the image, and replaces the container. Use the temporary tunnel only when the update needs it.

