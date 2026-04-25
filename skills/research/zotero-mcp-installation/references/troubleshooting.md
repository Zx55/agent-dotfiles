# Troubleshooting

Use this file only when normal installation or verification does not work.

## Zotero local API is not available

Symptoms:

- `curl http://127.0.0.1:23119/...` fails.
- MCP search fails even though the server starts.

Check:

- Zotero Desktop is running.
- Zotero setting `Allow other applications on this computer to communicate with Zotero` is enabled.
- Zotero was restarted after changing the setting.

## Plugin ping fails

Symptoms:

- `/zotero-add-local-file/ping` returns 404.
- Ping returns old plugin version or missing `features`.

Check:

- The installed XPI is `assets/plugin/zotero-add-local-file-plugin.xpi`.
- Zotero was restarted after installing or updating the plugin.
- The plugin is enabled in `Tools -> Plugins`.
- Automatic updates for the plugin are disabled.

## tokenConfigured is false

Symptom:

- `/ping` returns `tokenConfigured: false`.

Fix:

- In Zotero Config Editor, create or update string pref `extensions.zoteroAddLocalFile.token`.
- Restart Zotero.
- Use the same token in Codex MCP env as `ZOTERO_ADD_LOCAL_FILE_TOKEN`.

## add-from-file works but metadata is sparse

Likely causes:

- The plugin is old and does not call Zotero's recognizer.
- Zotero recognizer could not identify the PDF.
- Zotero has no network path to arXiv/DOI metadata.

Check:

- `/ping` includes `features.recognizeImportedFiles: true`.
- Direct plugin responses include `metadataSource: "zotero-recognizer"` for recognizable PDFs.
- For arXiv PDFs, Zotero should usually populate DOI, URL, Extra, authors, and abstract.

## MCP startup failed

Typical symptom:

- `handshaking with MCP server failed`

Check:

- `~/.local/bin/zotero-mcp` exists and is executable.
- `~/.local/bin/zotero-mcp-wrapper` exists and is executable.
- Codex MCP config uses the wrapper as the command.
- `ZOTERO_MCP_BIN` points to the real upstream `zotero-mcp`.
- Restart Codex after changing MCP config.
