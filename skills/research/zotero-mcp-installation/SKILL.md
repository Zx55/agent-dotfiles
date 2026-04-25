---
name: zotero-mcp-installation
description: Install, update, and configure Zotero MCP for Codex on macOS, including the bundled zotero-mcp-wrapper binary, the Zotero Add Local File plugin, local add-from-file token setup, Codex MCP configuration, and smoke tests for search and PDF import. This skill currently supports Codex and macOS only.
---

# Zotero MCP Installation

Use this skill when setting up or repairing Zotero MCP for Codex on macOS.

This workflow is local-first:

- `zotero-mcp-wrapper` is the Codex MCP command.
- The wrapper forwards normal MCP traffic to `zotero-mcp`.
- If `ZOTERO_ADD_LOCAL_FILE_TOKEN` is configured, the wrapper intercepts `zotero_add_from_file` and calls the Zotero Add Local File plugin so PDFs are imported through Zotero Desktop storage and Zotero's own recognizer.

Do not use this skill for daily Zotero library operations, Claude Desktop setup, Linux, or Windows.

## Assets

Bundled files are relative to this skill directory:

- Wrapper binary: `assets/bin/macos/zotero-mcp-wrapper`
- Zotero plugin XPI: `assets/plugin/zotero-add-local-file-plugin.xpi`

Copy assets from the skill directory; do not rebuild them during normal installation unless the user asks to develop the tools.

## Manual Prerequisites

These steps require the user to operate Zotero or zotero.org. Do not pretend they can be fully automated.

1. Ensure Zotero Desktop is installed and running.
   - Supported target: Zotero 9 on macOS.
   - In Zotero settings, enable local app communication: `Settings -> Advanced -> Allow other applications on this computer to communicate with Zotero`.

2. Install the Zotero Add Local File plugin.
   - Give the user `assets/plugin/zotero-add-local-file-plugin.xpi`.
   - In Zotero: `Tools -> Plugins`, install the XPI.
   - Disable automatic updates for this plugin in the plugin manager.
   - Restart Zotero after installing or updating the plugin.

3. Create a `ZOTERO_ADD_LOCAL_FILE_TOKEN` value and set the matching Zotero preference.
   - Generate a strong random token locally, for example:

     ```bash
     python - <<'PY'
     import secrets
     print(secrets.token_urlsafe(32))
     PY
     ```

   - In Zotero Config Editor, set string pref `extensions.zoteroAddLocalFile.token` to that token.
   - The same token must later be passed to Codex MCP as `ZOTERO_ADD_LOCAL_FILE_TOKEN`.
   - Never print the token in final answers.

4. Create a Zotero write API key on zotero.org.
   - URL: `https://www.zotero.org/settings/keys/new`
   - Grant write access to the relevant library.
   - Keep the key private. If using web-mode setup or web-backed write features, pass it to `zotero-mcp setup --no-local --api-key ...` or configure it as `ZOTERO_API_KEY` with the needed library ID/type.
   - For the local-first Codex path below, Zotero Desktop local API is primary; the write API key is still part of the complete setup checklist because upstream `zotero-mcp` supports web API mode and some installations may need it.

Stop after these prerequisites if the user has not completed them. Continue only after they confirm Zotero was restarted and the token/API key are ready.

## Agent Installation

Run these after the manual prerequisites are complete.

### Install upstream zotero-mcp

Prefer `uv`:

```bash
uv tool install --upgrade zotero-mcp
```

Configure `zotero-mcp`. For local-first Codex use:

```bash
zotero-mcp setup --no-claude
```

If the user explicitly wants web API mode, use the key and library info they provide:

```bash
zotero-mcp setup --no-local --api-key "$ZOTERO_API_KEY" --library-id "$ZOTERO_LIBRARY_ID" --library-type user --no-claude
```

### Install wrapper binary

From this skill directory:

```bash
mkdir -p ~/.local/bin
cp assets/bin/macos/zotero-mcp-wrapper ~/.local/bin/zotero-mcp-wrapper
chmod 755 ~/.local/bin/zotero-mcp-wrapper
```

Confirm:

```bash
test -x ~/.local/bin/zotero-mcp-wrapper
file ~/.local/bin/zotero-mcp-wrapper
```

### Configure Codex MCP

Use the wrapper as the MCP command. Include the local-file token from the user/Zotero config.

```bash
codex mcp add zotero \
  --env ZOTERO_MCP_BIN="$HOME/.local/bin/zotero-mcp" \
  --env ZOTERO_MCP_ARGS=serve \
  --env ZOTERO_AUTO_LAUNCH=true \
  --env ZOTERO_APP_PATH=/Applications/Zotero.app \
  --env ZOTERO_LOCAL_HOST=127.0.0.1 \
  --env ZOTERO_LOCAL_PORT=23119 \
  --env ZOTERO_LOCAL=true \
  --env ZOTERO_EMBEDDING_MODEL=default \
  --env ZOTERO_ADD_LOCAL_FILE_TOKEN="$ZOTERO_ADD_LOCAL_FILE_TOKEN" \
  -- "$HOME/.local/bin/zotero-mcp-wrapper"
```

If the user needs web API mode, also include:

```bash
--env ZOTERO_API_KEY="$ZOTERO_API_KEY" \
--env ZOTERO_LIBRARY_ID="$ZOTERO_LIBRARY_ID" \
--env ZOTERO_LIBRARY_TYPE=user \
```

Ask the user to restart Codex after changing MCP configuration.

## Verification

Run verification in this order.

### 1. Plugin ping

This checks Zotero Desktop, local API, plugin installation, and token presence:

```bash
curl -s http://127.0.0.1:23119/zotero-add-local-file/ping
```

Expected:

- `ok: true`
- `plugin: "zotero-add-local-file-plugin"`
- `tokenConfigured: true`
- `features.recognizeImportedFiles: true`

If ping fails, stop and fix Zotero/plugin setup before testing MCP.

### 2. MCP query

After restarting Codex, use Zotero MCP tools to run a real library query, such as recent items or a title search.

Expected:

- MCP handshake succeeds.
- A Zotero result is returned.

### 3. PDF import smoke test

Use `zotero_add_from_file` on a real local PDF.

Expected:

- The returned stored path is under `~/Zotero/storage/<attachmentKey>/`.
- The file exists on disk.
- For recognizable PDFs, Zotero metadata is populated by Zotero's recognizer: authors, DOI/arXiv URL, Extra, and abstract when available.

Good follow-up checks:

```bash
test -f "/path/from/zotero_add_from_file"
```

Then call `zotero_get_item_metadata` on the returned parent item key.

## Troubleshooting

If the normal flow fails, read `references/troubleshooting.md`.
