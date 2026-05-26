# Router DHCP Reservation For MiAir

MiAir should advertise a stable LAN IP. Use the router's DHCP reservation or static lease feature.

## What To Bind

Bind the network interface that runs MiAir:

- For macOS native, bind the Mac Wi-Fi MAC address when the Mac uses Wi-Fi at home.
- For a wired Linux/NAS host, bind the Ethernet MAC address.
- Do not bind a Tailscale, Docker, Thunderbolt bridge, VPN, or VM adapter address.

Choose an address in the home LAN range that will not collide with other devices, for example `192.168.1.50` when the router subnet is `192.168.1.0/24`.

## Router UI Names

Different routers use different names:

- DHCP reservation
- static lease
- address reservation
- IP and MAC binding
- LAN DHCP binding

After saving, reconnect the host to Wi-Fi or renew DHCP. Verify the host receives the reserved address before installing or restarting MiAir.

## macOS Checks

Find current Wi-Fi IP:

```bash
ipconfig getifaddr en0
```

Find Wi-Fi MAC address:

```bash
networksetup -getmacaddress Wi-Fi
```

Renew DHCP:

```bash
sudo ipconfig set en0 DHCP
```

## Acceptance Criteria

- The host gets the same LAN IP after reconnecting.
- MiAir is started with that same IP.
- `http://<reserved-ip>:8300` opens from another device on the LAN.
- iPhone and speaker are on the same LAN and can discover the MiAir AirPlay target.
