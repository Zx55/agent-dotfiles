# macOS Daemon And Proxy Reference

Use this reference when moving from a working foreground setup to a durable background service on macOS.

## Install The Daemon

Use the directory that contains `config.toml`:

```bash
cc-connect daemon install --work-dir ~/.cc-connect
```

After install:

```bash
cc-connect daemon status --work-dir ~/.cc-connect
```

The LaunchAgent is usually created at:

```text
~/Library/LaunchAgents/com.cc-connect.service.plist
```

## Why `--work-dir` Matters

For daemon installation, `cc-connect` is more reliable when given the config directory instead of the config file path.

Prefer:

```bash
cc-connect daemon install --work-dir ~/.cc-connect
```

Do not rely on:

```bash
cc-connect --config ~/.cc-connect/config.toml daemon install
```

Foreground runs often accept `--config`, but daemon setup can behave differently.

## What The LaunchAgent Does

The generated plist typically enables:

- `RunAtLoad`: start when the macOS user logs in
- `KeepAlive`: restart after unexpected exits

This means the bot is login-start, not necessarily pre-login system-start.

## Foreground vs Daemon Proxy Behavior

Do not assume the user already has shell helpers, aliases, or wrapper commands for proxying.

First ask:

- does this host need a proxy to reach Telegram?
- what proxy address should be used?
- how does the user normally enable that proxy?

Interactive shell helpers, aliases, or wrapper commands can help in a terminal session only.

They do not automatically carry into `launchd`.

If Telegram requires a proxy, persist proxy environment variables into the LaunchAgent plist.

## Persist Proxy Into The LaunchAgent

Example for a local proxy on `127.0.0.1:7890`:

```bash
cp ~/Library/LaunchAgents/com.cc-connect.service.plist \
  ~/Library/LaunchAgents/com.cc-connect.service.plist.bak

plutil -replace EnvironmentVariables.http_proxy  -string http://127.0.0.1:7890 ~/Library/LaunchAgents/com.cc-connect.service.plist
plutil -replace EnvironmentVariables.https_proxy -string http://127.0.0.1:7890 ~/Library/LaunchAgents/com.cc-connect.service.plist
plutil -replace EnvironmentVariables.HTTP_PROXY  -string http://127.0.0.1:7890 ~/Library/LaunchAgents/com.cc-connect.service.plist
plutil -replace EnvironmentVariables.HTTPS_PROXY -string http://127.0.0.1:7890 ~/Library/LaunchAgents/com.cc-connect.service.plist
plutil -replace EnvironmentVariables.all_proxy   -string socks5://127.0.0.1:7890 ~/Library/LaunchAgents/com.cc-connect.service.plist
plutil -replace EnvironmentVariables.ALL_PROXY   -string socks5://127.0.0.1:7890 ~/Library/LaunchAgents/com.cc-connect.service.plist
```

The lowercase and uppercase variants are both worth setting because different tools and libraries may read different names.

Replace the example address with the user's actual proxy values.

## Reload The LaunchAgent

After editing the plist:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.cc-connect.service.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.cc-connect.service.plist
launchctl kickstart -k gui/$(id -u)/com.cc-connect.service
```

Then verify:

```bash
cc-connect daemon status --work-dir ~/.cc-connect
tail -n 80 ~/.cc-connect/logs/cc-connect.log
```

## Daily Service Commands

```bash
cc-connect daemon status --work-dir ~/.cc-connect
cc-connect daemon logs -f --work-dir ~/.cc-connect
cc-connect daemon stop --work-dir ~/.cc-connect
cc-connect daemon start --work-dir ~/.cc-connect
cc-connect daemon restart --work-dir ~/.cc-connect
```

If `restart` behaves oddly, use `stop` and `start` separately.

## Dependency Reminder

Persisting proxy settings into the plist solves only the `cc-connect` side.

The proxy program itself must still be running and listening on the configured local address after login.
