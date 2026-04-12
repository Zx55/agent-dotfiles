---
name: telegram-codex-bot
description: Install a Telegram bot that controls a local Codex agent through cc-connect on macOS. Use when the user wants to set up, configure, connect, or debug a Codex bot from Telegram, including installing cc-connect, bringing the bot online, and installing the macOS launchd service.
---

# Telegram Codex Bot

Install `cc-connect` on macOS so Telegram can talk to a local `Codex` CLI, then make the bot durable enough to survive logins and restarts.

Keep the main workflow in this file. Load the reference files only when their details are needed:

- For `config.toml` structure and field choices, read [references/config.md](references/config.md).
- For macOS daemon setup and proxy persistence, read [references/daemon-and-proxy.md](references/daemon-and-proxy.md).
- For verification steps and common failures, read [references/troubleshooting.md](references/troubleshooting.md).

## Core Workflow

1. Confirm prerequisites.
   Make sure `codex`, `npm`, and `cc-connect` are installed. Confirm the machine can either reach `api.telegram.org` directly or has a working proxy path.

2. Build the minimal `cc-connect` config.
   Create one `[[projects]]` entry with `type = "codex"` and one Telegram platform entry. Prefer a narrow `work_dir` instead of a broad directory.

3. Start with safe agent permissions.
   Prefer `mode = "suggest"` for the first working version. Only recommend `auto-edit`, `full-auto`, or `yolo` after the user understands the tradeoffs.

4. Validate in the foreground first.
   Start `cc-connect` manually before installing the daemon. This isolates config and Telegram issues from launchd issues.

5. Lock down Telegram access after bootstrap.
   If needed, begin with `allow_from = "*"`, then get the user's Telegram numeric id with `/whoami` and replace it with that id.

6. Install the daemon only after the foreground test passes.
   On macOS, prefer `cc-connect daemon install --work-dir ~/.cc-connect`. Do not assume `--config ~/.cc-connect/config.toml` behaves the same during daemon install.

7. Treat proxy setup as a service concern, not just a shell concern.
   First ask whether the host needs a proxy for Telegram, what the proxy address is, and how the user normally enables it. If Telegram needs a proxy, foreground testing can use the user's normal method or inline environment variables, but the background service still needs proxy environment variables persisted in the LaunchAgent.

8. Verify from Telegram and from the host.
   Use `/status` in Telegram and check daemon status plus logs on the host. A bot can appear installed but still fail during Telegram auth.

## macOS Install Focus

- Keep the main path install-oriented. Prefer the shortest sequence that gets the bot online, verified in Telegram, and durable through `launchd`.
- Keep the initial config minimal. Explain only the tradeoffs that block installation, such as `work_dir`, `mode`, or whether Telegram needs a proxy.
- Treat proxy persistence as part of installation on macOS when the host cannot reach Telegram directly.
- Move debugging branches, failure analysis, and repeated edge-case handling to [references/troubleshooting.md](references/troubleshooting.md).

## Reference Map

- `references/config.md`
  Use for minimal and tightened `config.toml` examples, field explanations, and rollout advice for `allow_from`, `work_dir`, and `mode`.

- `references/daemon-and-proxy.md`
  Use for macOS `launchd`, `daemon install --work-dir`, proxy persistence in the LaunchAgent plist, and reload commands.

- `references/troubleshooting.md`
  Use for `curl` checks, log inspection, startup signatures, and the most common failure patterns.

## Output Expectations

When using this skill, produce:

- a minimal working config first
- a clear foreground validation step
- a daemon setup path only after the foreground path succeeds
- proxy persistence guidance only when the network actually requires it
- a macOS-specific install path that ends with a working `launchd` service
- troubleshooting guidance only by linking or switching to `references/troubleshooting.md` when the install path stops being straightforward

Keep recommendations concrete. Prefer exact commands, exact paths, and a small number of decision branches.
