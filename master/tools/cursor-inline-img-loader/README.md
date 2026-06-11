# cursor-inline-img-loader

`cursor-inline-img-loader` is a tiny stdio MCP server for Cursor. It loads a
local PNG/JPEG/GIF/WebP file and returns it as MCP `ImageContent` so Cursor can
render the tool result as an image.

This is a Cursor display adapter, not a cross-agent image workflow. The stable
handoff for generated images should still include the filesystem path.

## Tool

`load_image`

Arguments:

- `path`: absolute or cwd-relative local image path.
- `cwd`: optional base directory for relative paths.
- `max_bytes`: optional byte limit. Defaults to 15 MiB.

The tool returns only MCP `content` blocks: a short text block and one image
block. It intentionally does not return `structuredContent`, because several
MCP clients treat structured output as higher priority and may hide native image
blocks.

## Install

From `~/Documents/agent-dotfiles`:

```sh
uv tool install --force ./master/tools/cursor-inline-img-loader
```

## Cursor MCP Config

```json
{
  "mcpServers": {
    "cursor-inline-img-loader": {
      "type": "stdio",
      "command": "${userHome}/.local/bin/mcp-launcher",
      "args": ["--", "~/.local/bin/cursor-inline-img-loader"]
    }
  }
}
```

Restart Cursor after changing MCP configuration.
