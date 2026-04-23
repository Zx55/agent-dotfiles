---
name: zotero-mcp-installation
description: Install, update, and configure Zotero MCP for Codex on macOS. Use when the user wants to set up Zotero MCP, install the bundled zotero-mcp-wrapper binary, wire Zotero into Codex via `codex mcp add`, or debug basic local setup issues. This skill currently supports Codex and macOS only.
---

# Zotero MCP Installation

Use this skill when the user wants to install or configure Zotero MCP for Codex on macOS.

This skill is intentionally narrow. It helps with:

- installing or updating `zotero-mcp` with `uv`
- installing the bundled `zotero-mcp-wrapper` binary into `~/.local/bin/`
- configuring Codex to use the wrapper as the Zotero MCP command
- checking the required Zotero Desktop local API setting

Do not use this skill for:

- daily Zotero library operations
- Claude Desktop setup
- Linux or Windows setup

## Quick Flow

1. Confirm Zotero Desktop is installed on macOS.
2. Confirm Zotero has `Allow other applications on this computer to communicate with Zotero` enabled.
3. Install or update `zotero-mcp` with `uv`.
4. Copy the bundled wrapper binary into `~/.local/bin/zotero-mcp-wrapper`.
5. Configure Codex with `codex mcp add`.
6. Restart Codex and run a real Zotero query.

## Install and Setup zotero-mcp

Prefer `uv` to install `zotero-mcp`:

```bash
uv tool install --upgrade zotero-mcp
```

Then setup the `zotero-mcp`:

```bash
zotero-mcp setup
```

## Install the Wrapper Binary

The wrapper is recommended because it provides a more stable Codex startup path and can auto-launch Zotero Desktop before forwarding requests to `zotero-mcp`.

Copy the bundled binary with:

```bash
mkdir -p ~/.local/bin
cp ./assets/bin/macos/zotero-mcp-wrapper ~/.local/bin/zotero-mcp-wrapper
chmod 755 ~/.local/bin/zotero-mcp-wrapper
```

## Configure Codex

Install the Codex MCP using the wrapper:

```bash
codex mcp add zotero \
  --env ZOTERO_MCP_BIN=~/.local/bin/zotero-mcp \
  --env ZOTERO_MCP_ARGS=serve \
  --env ZOTERO_AUTO_LAUNCH=true \
  --env ZOTERO_APP_PATH=/Applications/Zotero.app \
  --env ZOTERO_LOCAL_HOST=127.0.0.1 \
  --env ZOTERO_LOCAL_PORT=23119 \
  --env ZOTERO_LOCAL=true \
  --env ZOTERO_EMBEDDING_MODEL=default \
  -- ~/.local/bin/zotero-mcp-wrapper
```

## Verify

After installation:

1. Restart Codex.
2. Run one real Zotero query.

Good validation prompts include:

- `Use zotero mcp to search for <title>`
- `Use zotero mcp to find <title>`

## Troubleshooting

Read:

- `references/troubleshooting.md`
