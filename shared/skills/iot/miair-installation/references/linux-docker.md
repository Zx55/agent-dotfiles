# Linux Docker MiAir

Use this path for Linux, OpenWrt, iStoreOS, NAS, soft router, Raspberry Pi, or any host where Docker can use real host networking.

## Fixed Paths

- Source: `/opt/miair/src`
- Config: `/opt/miair/conf`
- Container: `miair`
- Image: `miair:local`
- Docker logs: `docker logs miair`
- MiAir app log: `/opt/miair/conf/miair.log`

Do not make the config path user-selectable in the skill. Fixed paths make later repair and updates predictable.

## Install

Run as root or through sudo:

```bash
sudo scripts/install_linux_docker.sh --hostname <host-lan-ip>
```

The script:

- verifies Docker is available
- clones or updates upstream MiAir into `/opt/miair/src`
- builds a local Docker image from the upstream Dockerfile
- runs the container with `--network=host`
- mounts `/opt/miair/conf` into `/app/conf`
- sets `MIAIR_HOSTNAME=<host-lan-ip>`
- starts MiAir with `--hostname "$MIAIR_HOSTNAME"` so the explicit host LAN IP overrides any hostname previously saved in `/opt/miair/conf/config.json`
- sets Docker restart policy to `unless-stopped`

The macOS native wrapper is not used on Linux Docker. Keep the Linux container on upstream MiAir unless a Linux-specific failure is reproduced.

## Why Host Networking

MiAir relies on LAN discovery and dynamic media ports:

- AirPlay RAOP discovery through mDNS
- DLNA discovery through SSDP multicast
- RTSP, RTP, RTCP, timing, and HTTP stream ports opened dynamically

Linux Docker host networking gives the container direct access to the host network namespace. This is more reliable for MiAir than port mapping.

## macOS Wrapper Issues And Linux

The macOS native wrapper fixes two local macOS behaviors:

- MiAir can publish a utun or proxy address such as `198.18.x.x` if it relies on route-based IP detection.
- Python `zeroconf` can publish RAOP in a way that local checks show only on loopback instead of the Wi-Fi interface.

Linux Docker should not use the macOS wrapper. The installer sets `MIAIR_HOSTNAME=<host-lan-ip>` and starts MiAir with `--hostname "$MIAIR_HOSTNAME"` so the explicit host LAN IP takes precedence over saved config and route-based detection. Host networking also avoids Docker port mapping and multicast problems.

If a Linux host runs a VPN, transparent proxy, or multiple default routes, the same wrong-address symptom may still happen. Diagnose by checking the MiAir log for `AirPlay mDNS 启动中，IP:` and confirm it is the physical LAN IP passed as `--hostname`. If it is not, treat that as a Linux-specific bug before copying the macOS wrapper behavior.

## Service Commands

```bash
docker ps -a --filter name=miair
docker logs -f miair
docker restart miair
docker rm -f miair
```

Web UI:

```text
http://<host-lan-ip>:8300
```

## Update

Rerun:

```bash
sudo scripts/install_linux_docker.sh --hostname <host-lan-ip>
```

The config under `/opt/miair/conf` is preserved. The old container is replaced.

## Common Failures

- iPhone cannot see the AirPlay target: check host networking, multicast on the LAN, and that the host IP is the physical LAN IP.
- Web UI does not open: check `docker logs miair`, host firewall, and whether port `8300` is already occupied.
- Speaker list is empty: refresh Xiaomi cookie and inspect `/opt/miair/conf/config.json` only on the target host.
- Playback fails after discovery: check that the speaker can fetch `http://<host-lan-ip>:<dynamic-port>/airplay/stream.wav`.
