# Troubleshooting

Use this reference when `cc-connect`, Telegram, and Codex do not all behave as expected.

## Fast triage

Check these in order:

1. Is the daemon running?
2. Can the host reach `api.telegram.org`?
3. Do the logs show a Telegram auth failure or a later-stage issue?
4. Does the LaunchAgent include proxy variables if the host needs a proxy?
5. Is `allow_from` preventing the user from talking to the bot?

## Quick commands

### Check daemon status

```bash
cc-connect daemon status --work-dir ~/.cc-connect
```

### Tail logs

```bash
tail -n 80 ~/.cc-connect/logs/cc-connect.log
```

### Check Telegram reachability without proxy

```bash
curl -I --max-time 15 https://api.telegram.org
```

### Check Telegram reachability with proxy

Ask the user for the proxy address if it is not already known.

```bash
HTTPS_PROXY=http://127.0.0.1:7890 \
HTTP_PROXY=http://127.0.0.1:7890 \
ALL_PROXY=socks5://127.0.0.1:7890 \
curl -I --max-time 15 https://api.telegram.org
```

Replace the example values with the user's actual proxy settings.

### Inspect LaunchAgent environment

```bash
plutil -p ~/Library/LaunchAgents/com.cc-connect.service.plist
```

## Healthy startup signature

Good logs usually include:

```text
config loaded
telegram: connected
platform started
engine started
cc-connect is running
```

## Common failure patterns

### Foreground works, daemon fails

Most likely cause:

- the daemon does not have proxy environment variables

Action:

- inspect the LaunchAgent plist
- persist proxy variables there
- reload the LaunchAgent

### Telegram auth times out

Most likely causes:

- no proxy
- wrong proxy address
- proxy program not running

This is usually a connectivity issue, not a broken token.

### Bot is online but ignores messages

Most likely causes:

- wrong `allow_from`
- user id not updated after bootstrap

Action:

- check `/whoami`
- compare it with `allow_from` in `~/.cc-connect/config.toml`

### Daemon status looks running, but the service is crash-looping

Action:

- inspect the recent log tail
- look for repeating `config loaded` followed by Telegram auth failures

This usually means launchd is repeatedly restarting a process that still cannot connect.

### Manual tests seem to use the wrong config

Possible cause:

- the current directory contains another `config.toml`

Action:

- run `cc-connect --config ~/.cc-connect/config.toml`
- or change into a directory without another `config.toml`
