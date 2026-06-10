---
name: lark-cli-installation
description: Install, configure, authorize, update, and repair the official Lark/Feishu CLI for local agents. Use only when explicitly requested for Lark CLI setup, first-run OAuth, missing-scope authorization, SSH-machine setup, or CLI health checks.
disable-model-invocation: true
---

# Lark CLI Installation

Use this skill only when explicitly asked to install, update, configure, authorize, verify, or repair the official `lark-cli`. Do not use it for daily Lark operations after setup is healthy, and do not perform proactive Lark CLI installation work just because a user asks to automate something in Lark. Reading documents, editing docs, sending messages, calendar work, sheets, Base, wiki, slides, whiteboard, and meeting workflows belong to the official Lark companion skills.

This skill intentionally does not manage local agent skill filtering or allowlists.

## Scope

This skill owns:

- installing or updating `lark-cli`
- first-time app configuration with `lark-cli config init --new`
- first-time user login with `lark-cli auth login`
- authorizing additional scopes after `missing_scope` errors
- verifying `bot` and `user` identity readiness
- explaining token refresh behavior and multi-machine setup

This skill does not own:

- storing real app credentials, OAuth codes, device codes, or access tokens in committed files
- copying token stores between machines
- configuring Lark MCP servers
- ongoing product workflows inside Lark

## Install

Check prerequisites first:

```bash
node --version
npm --version
```

Install the official CLI:

```bash
npx @larksuite/cli@latest install
```

Verify:

```bash
command -v lark-cli
lark-cli --version
lark-cli help
```

Expected: a `lark-cli` binary is on `PATH`, and help lists domains such as `auth`, `config`, `docs`, `drive`, `im`, `calendar`, `sheets`, `base`, `wiki`, `slides`, and `task`.

## First-Time App Configuration

Run the AI-agent configuration flow:

```bash
lark-cli config init --new
```

The command prints a Feishu/Lark setup URL and waits for the user to complete browser setup. Extract the URL exactly as printed and send it to the user. Treat the URL as opaque: do not URL-encode, decode, trim internal characters, or add punctuation to it.

If the command asks for QR display, generate a PNG QR code:

```bash
lark-cli auth qrcode "<verification_url>" --output "./lark-cli-config.png"
```

Show the URL first, then display the QR image. Wait for the user to complete the browser flow before continuing.

## First Login

For ordinary local interactive setup, use:

```bash
lark-cli auth login --recommend
```

This grants the CLI's recommended common scopes. Send the printed verification URL to the user exactly as printed. If required, also generate and display a QR code:

```bash
lark-cli auth qrcode "<verification_url>" --output "./lark-cli-auth.png"
```

For agent flows where the turn should end while the user authorizes, prefer the non-blocking flow:

```bash
lark-cli auth login --recommend --no-wait --json
```

From the JSON output:

- send `verification_url` to the user exactly as printed
- generate and display a QR image from `verification_url`
- keep `device_code` only in the current task context
- do not commit or persist `device_code`

After the user confirms authorization, complete polling:

```bash
lark-cli auth login --device-code "<device_code>"
```

Do not restart the login flow while the user is authorizing. Restarting creates a new device code and can invalidate the URL they are using.

## Verification

After app configuration and login, run:

```bash
lark-cli auth status
```

Verify:

- `bot.status` is `ready` when bot identity is expected
- `user.status` is `ready` for user-scoped automation
- `tokenStatus` is `valid`
- the expected brand is selected, usually `feishu` for China accounts

It is fine to summarize expiry timestamps, but do not print raw tokens or secrets.

## Additional Scope Authorization

If a command fails with `missing_scope`, authorize only the missing scopes. Example:

```bash
lark-cli auth login --scope "search:docs:read" --no-wait --json
```

Then follow the same device-flow pattern:

1. Send `verification_url` exactly as printed.
2. Generate and display a QR image:

   ```bash
   lark-cli auth qrcode "<verification_url>" --output "./lark-cli-scope-auth.png"
   ```

3. Wait for the user to confirm authorization.
4. Complete with:

   ```bash
   lark-cli auth login --device-code "<device_code>"
   ```

5. Retry the original command.

Use narrow scopes from the error message. Do not rerun broad recommended login just to add one missing permission unless the user asks for broad access.

## Token And Refresh Behavior

Normal use does not require login every time. `lark-cli` stores credentials in local secure storage and refreshes short-lived access tokens when possible.

Re-authentication is needed when:

- the refresh token expires
- the user logs out
- the user or tenant revokes authorization
- a command needs a scope that has not been granted
- the CLI is being configured on a new machine, SSH host, or profile

## Multi-Machine Setup

Configure each machine independently:

```bash
npx @larksuite/cli@latest install
lark-cli config init --new
lark-cli auth login --recommend
lark-cli auth status
```

Do not copy credential stores from one host to another. For SSH machines, run the same device-flow login and have the user complete authorization in a browser on a trusted device.

Keep app credentials and local secrets out of committed dotfiles. If a setup requires stable app credentials outside the CLI's own secure storage, put them in the user's local secret mechanism rather than repo-tracked files.

## Update And Repair

For a simple health check:

```bash
command -v lark-cli
lark-cli --version
lark-cli auth status
```

If available, run:

```bash
lark-cli doctor
```

Update with:

```bash
lark-cli update
```

If the binary is missing or broken, reinstall:

```bash
npx @larksuite/cli@latest install
```

After repair, run `lark-cli auth status`. Only repeat `config init` or `auth login` when status shows missing config, expired/revoked credentials, or missing scopes.

## Output Expectations

When using this skill, report:

- install/update action taken
- whether app configuration is complete
- whether user and bot identities are ready
- any missing scopes and the exact scope authorization flow used
- whether the original command was retried successfully
- any manual browser action still required from the user
