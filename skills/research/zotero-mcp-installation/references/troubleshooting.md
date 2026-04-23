# Troubleshooting

Use this file only when normal installation or configuration does not work.

## Zotero local API is not available

Symptom:

- real Zotero searches fail even though the MCP server appears installed

Check Zotero Desktop settings:

- `Settings -> Advanced`
- enable `Allow other applications on this computer to communicate with Zotero`

Then restart Zotero and retry a real query.

## MCP startup failed

Typical symptom:

- `handshaking with MCP server failed`

Likely causes:

- `zotero-mcp` path is wrong or missing
- wrapper binary missing or not executable

Check:

- `~/.local/bin/zotero-mcp` exists
- `~/.local/bin/zotero-mcp-wrapper` exists
- both are executable