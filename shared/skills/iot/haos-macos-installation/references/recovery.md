# Recovery And Rollback

Use this when HAOS becomes unreachable or store/Docker connectivity fails after network changes.

## If HA UI Is Slow After Reboot

HAOS can take several minutes after reboot. A temporary page saying `Unable to connect to Home Assistant` can be normal while Core starts.

Check:

```text
http://<haos-ip>:4357
```

Observer can show whether Supervisor is alive while Core is still starting.

## If HAOS Is Reachable But Store/App Install Fails

Check:

```sh
ssh haos 'ha network info'
ssh haos 'ha resolution info'
ssh haos 'ha supervisor logs | tail -n 120'
ssh haos 'ha dns info'
```

Common causes:

- IPv6 still enabled and Docker chooses an unreachable IPv6 route.
- DNS points to the home router and Supervisor marks it failed.
- Host orchestrator router rules are not loaded after Mac reboot.
- Clash/TUN is not running or `utunN` changed.
- The Mac selected a different LAN gateway, such as Wi-Fi after wired disappeared, and HAOS still points at the previous Mac LAN IP.

## Restore HAOS DHCP

If static gateway settings break access, use the UTM console or whichever SSH path still works:

```sh
ha network update enp0s1 --ipv4-method auto --ipv6-method auto
ha host reboot
```

Then temporarily switch UTM back to shared networking/NAT if needed.

## Stop Host Router

```sh
cd ~/agent-dotfiles
sudo ./ha-host/tools/orchestrator/src/ha_host_orchestrator/mac_router/mac-router.sh stop
```

If other tooling uses IPv4 forwarding:

```sh
sudo ./ha-host/tools/orchestrator/src/ha_host_orchestrator/mac_router/mac-router.sh stop --keep-forwarding
```

## Switch Back To UTM Shared Networking

1. Shut down HAOS from the HA UI or UTM.
2. Change UTM network mode to shared networking.
3. Start HAOS.
4. Find the UTM private IP, often `192.168.64.2`.
5. Access `http://<utm-private-ip>:8123`.

This is a safe recovery mode for updates and repairs, but it may not provide the same LAN discovery behavior as bridged mode.

## Official HA Backup Restore

If configuration changes cause a bad state:

1. Boot HAOS.
2. Open `Settings -> System -> Backups`.
3. Restore the most recent known-good official HA backup.
4. Re-check SSH and network after restore.

Keep at least one official HA backup copied off HAOS through an available file-transfer path before major network changes.
