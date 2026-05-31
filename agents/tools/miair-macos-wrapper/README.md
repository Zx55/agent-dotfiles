# miair-macos-wrapper

`miair-macos-wrapper` is a small macOS-only launcher for MiAir native installs.

It keeps the upstream MiAir checkout unmodified while adapting AirPlay discovery for this local macOS workflow:

- prefer the configured `--hostname` for AirPlay mDNS address publication when it is an IPv4 address
- export the configured `--hostname` as `MIAIR_HOSTNAME` before MiAir starts so upstream RTSP authentication code uses the same LAN IP
- publish RAOP through macOS native `/usr/bin/dns-sd -R` so the service appears on the Wi-Fi interface instead of only on loopback
- launch MiAir in the same Python process so the wrapper can apply the runtime adaptation before MiAir starts

The wrapper does not patch or rewrite files under `~/.local/share/miair/src`.

## Development

```bash
uv sync
uv run python -m unittest discover -s tests -v
```

## Runtime Shape

The MiAir installation skill installs this project into MiAir's own venv:

```text
~/.local/share/miair/venv/bin/miair-macos-wrapper
```

launchd runs the stable launcher path:

```text
~/.local/share/miair/bin/miair-core
```

which execs the venv console script.
