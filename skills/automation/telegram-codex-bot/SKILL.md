---
name: telegram-codex-bot
description: Install a Telegram bot that controls a local Codex agent through cc-connect on macOS. Use when the user wants to set up, configure, connect, or debug a Codex bot from Telegram, including installing cc-connect, bringing the bot online, and installing the macOS launchd service.
---

# Telegram Codex Bot

Install `cc-connect` on macOS so Telegram can talk to a local `Codex` CLI, then make the bot durable enough to survive logins and restarts.

## Core workflow

### Confirm prerequisites

Make sure `codex` and `npm` are installed. Confirm the machine can either reach `api.telegram.org` directly or has a working proxy path.

### Install `cc-connect`

Install `cc-connect` before touching config or `launchd`. Prefer the shortest stable path for Telegram + Codex on macOS:

```bash
npm install -g cc-connect
cc-connect --version
```

Only switch to GitHub Releases or build-from-source instructions if `npm install -g cc-connect` is blocked or the user explicitly wants a non-`npm` install path. For those cases, read [`cc-connect` INSTALL.md](https://github.com/chenhg5/cc-connect/blob/main/INSTALL.md).

### Build the minimal config

Create one `[[projects]]` entry with `type = "codex"` and one Telegram platform entry. Prefer a narrow `work_dir` instead of a broad directory. For exact `config.toml` structure, field choices, and minimal examples, read [references/config.md](references/config.md).

### Validate in the foreground

Prefer `mode = "suggest"` for the first working version. Start `cc-connect` manually before installing the daemon so config and Telegram issues stay separate from `launchd` issues. For verification details and common failures, read [references/troubleshooting.md](references/troubleshooting.md).

### Tighten Telegram access after bootstrap

If needed, begin with `allow_from = "*"`, then get the user's Telegram numeric id with `/whoami` and replace it with that id.

### Install the daemon

Only install the daemon after the foreground test passes. On macOS, prefer `cc-connect daemon install --work-dir ~/.cc-connect`. Do not assume `--config ~/.cc-connect/config.toml` behaves the same during daemon install.

Treat proxy setup as a service concern, not just a shell concern. If Telegram needs a proxy, foreground testing can use the user's normal method or inline environment variables, but the background service still needs proxy environment variables persisted in the LaunchAgent. For `launchd`, proxy persistence, reload commands, and host-side verification, read [references/daemon-and-proxy.md](references/daemon-and-proxy.md).

## macOS install focus

- Keep the main path install-oriented and minimal.
- Do not move to config or daemon setup until `cc-connect` is installed and `cc-connect --version` works.
- Link to deeper references only at the step where they become relevant.
- Treat proxy persistence as part of setup only when the host actually needs a proxy for Telegram.
- Push debugging branches and edge cases into [references/troubleshooting.md](references/troubleshooting.md).

## Output expectations

When using this skill, produce:

- an explicit `cc-connect` install step and version check
- a minimal working config
- a foreground validation step
- a daemon setup path that starts only after the foreground path succeeds
- proxy guidance only when the network actually requires it
- a clear handoff to the relevant reference when the main path stops being straightforward

Keep recommendations concrete. Prefer exact commands, exact paths, and a small number of decision branches.
