# Config reference

Use this reference when creating or reviewing `~/.cc-connect/config.toml` for `Codex + Telegram`.

## Minimal working config

```toml
[log]
level = "info"

[[projects]]
name = "my-codex"
admin_from = "123456789"

[projects.agent]
type = "codex"

[projects.agent.options]
work_dir = "/absolute/path/to/your/project"
mode = "suggest"
model = "gpt-5.4"
reasoning_effort = "high"

[[projects.platforms]]
type = "telegram"

[projects.platforms.options]
token = "your-telegram-bot-token"
allow_from = "123456789"
```

## Field guide

### `name`

Use a short project label that will make sense in `/status`, such as `my-codex` or a repo name.

### `type = "codex"`

This must be on `[projects.agent]` for `cc-connect` to launch the local Codex CLI instead of another agent type.

### `work_dir`

- Use an absolute path.
- Prefer a specific repo path over a broad folder like `/Users/you/Documents`.
- Narrower working directories reduce mistakes and make permissions easier to reason about.

### `mode`

Start with:

```toml
mode = "suggest"
```

Use other modes only when the user wants more automation:

- `suggest`: ask before each tool action
- `auto-edit`: auto-approve file edits, still ask for shell commands
- `full-auto`: more automated, still intended to stay within workspace boundaries
- `yolo`: least safe; bypass-oriented mode for users who explicitly want it

### `model`

Set a model only if the local Codex install should not use its default selection.

### `reasoning_effort`

`high` is a good default for general coding tasks. Lower it only when the user prefers speed over depth.

### `token`

Use the Telegram bot token from `@BotFather`.

### `allow_from`

Safer rollout pattern:

1. Start with `allow_from = "*"` only if needed for first bootstrap.
2. Once the bot is online, send `/whoami` from Telegram.
3. Replace `*` with the user's numeric Telegram id.

This prevents other Telegram users from interacting with the bot.

### `admin_from`

`admin_from` controls privileged commands such as `/dir`, `/shell`, `/restart`, `/upgrade`, and `/commands addexec`.

Set it explicitly if the user should be able to run those commands.

Use the same Telegram numeric id pattern as `allow_from`. Send `/whoami` or `/status` to the bot to get the id.

## Validate in the foreground

Before installing the daemon, validate the config in the foreground:

```bash
cc-connect --config ~/.cc-connect/config.toml
```

If Telegram connectivity is uncertain, ask the user whether this host needs a proxy before assuming one exists.

If the host does need a proxy, ask for the proxy address and how the user normally enables it.

One generic fallback pattern is:

```bash
HTTPS_PROXY=http://127.0.0.1:7890 \
HTTP_PROXY=http://127.0.0.1:7890 \
ALL_PROXY=socks5://127.0.0.1:7890 \
cc-connect --config ~/.cc-connect/config.toml
```

Replace the example proxy values with the user's actual settings.

Healthy startup usually includes:

```text
telegram: connected
platform started
cc-connect is running
```

## Common pitfalls

### Local `config.toml` interference

Some manual runs can be confused by a different `./config.toml` in the current directory.

When in doubt:

- run from a neutral directory, or
- pass `--config ~/.cc-connect/config.toml` explicitly

### Too-broad `work_dir`

A wide working directory can make the bot feel powerful at first, but it increases risk and weakens task boundaries.

### Locking down `allow_from` too early

If the bot is online but ignoring the user, confirm that the Telegram numeric id is correct.

### Privileged commands blocked because `admin_from` is unset

If normal chat works but `/dir` or `/shell` is rejected, check whether `admin_from` is missing from the project config.
