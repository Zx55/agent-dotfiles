# mcp-launcher

`mcp-launcher` starts MCP servers with predictable expansion for portable
Codex configuration.

It is intended for config that needs `~`, `$HOME`, or secret-backed variables
without relying on Codex to expand arbitrary MCP `env` strings.

## Convention

For MCP servers managed by this repository, pass server-specific environment
variables through `mcp-launcher --env` instead of Codex's
`[mcp_servers.<name>.env]` config block.

This keeps all MCP startup behavior in one argv path and ensures path and
variable expansion are handled consistently by `mcp-launcher`.

## Install

From this repository:

```sh
uv tool install ./master/tools/mcp-launcher
```

## Usage

```toml
[mcp_servers.zotero]
command = "mcp-launcher"
args = [
  "--env-file", "~/.secret",
  "--env", "ZOTERO_APP_PATH=/Applications/Zotero.app",
  "--env", "ZOTERO_MCP_BIN=~/.local/bin/zotero-mcp",
  "--env", "DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY",
  "--",
  "~/.local/bin/zotero-mcp-wrapper",
]
enabled = true
```

Expansion order:

1. inherit the current process environment
2. load `--env-file` values
3. apply `--env KEY=VALUE` values
4. expand the command and command arguments
5. replace the launcher process with the target command

Supported env-file syntax is intentionally small:

```sh
export TOKEN="value"
OTHER_TOKEN='value'
PLAIN_VALUE=value
```

Blank lines and comments are ignored. Shell commands, command substitution,
functions, and aliases are not evaluated.

By default, missing `$VAR` references fail fast. Use `--allow-missing-env` for
optional variables that should expand to an empty string.
