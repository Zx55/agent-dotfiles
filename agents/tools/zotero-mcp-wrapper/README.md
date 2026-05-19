# zotero-mcp-wrapper

`zotero-mcp-wrapper` is a small macOS-only stdio proxy that sits in front of `zotero-mcp`.

Its job is intentionally narrow:

- accept MCP stdio traffic from a local agent client
- launch and manage the real `zotero-mcp` child process
- check whether Zotero local API is available before request forwarding
- auto-launch Zotero Desktop when needed
- handle `zotero_add_from_file` through the local Zotero Add Local File plugin when configured
- forward MCP messages without changing their meaning

This project is not a general-purpose MCP framework. It is a focused wrapper for the Zotero local workflow discussed in this repository.

## Scope

Current V1 assumptions:

- macOS only
- stdio transport only
- wraps `zotero-mcp` only
- uses Zotero Desktop local API on port `23119`
- no message rewriting beyond minimal request inspection
- `zotero_add_from_file` may be handled locally to store attachments through Zotero Desktop instead of Web API upload

Out of scope for V1:

- Linux support
- Windows support
- generic MCP proxying for arbitrary servers
- long-running watchdog loops
- custom caching or telemetry

## Planned Shape

The preferred runtime path in this repository is:

```text
agent -> mcp-launcher -> zotero-mcp-wrapper -> zotero-mcp -> Zotero local API
```

`mcp-launcher` owns portable path and secret expansion before starting the
wrapper. If `mcp-launcher` is unavailable, the agent can run
`zotero-mcp-wrapper` directly as a machine-local fallback, but that should not
be the committed portable config.

The wrapper should check Zotero readiness when a real MCP request arrives. If Zotero is not ready, it should try to launch Zotero Desktop, wait for the local API to come up, and only then forward the request.

## Project Layout

```text
zotero-mcp-wrapper/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── scripts/
│   ├── build_macos_binary.sh
│   └── live_smoke_test.py
├── zotero_mcp_wrapper/
│   ├── __init__.py
│   ├── child_process.py
│   ├── cli.py
│   ├── config.py
│   ├── framing.py
│   ├── proxy.py
│   ├── types.py
│   └── zotero_runtime.py
└── tests/
```

The current implementation covers the MVP building blocks:

- child process startup for the real `zotero-mcp`
- MCP stdio JSON-line message parsing and writing
- request classification
- macOS Zotero launch and readiness checks
- transparent client-to-child request forwarding
- local `zotero_add_from_file` interception when `ZOTERO_ADD_LOCAL_FILE_TOKEN` is set
- basic unit tests for the core helpers

## Development

This project is intended to be managed with `uv`.

Typical first steps:

```bash
uv sync
uv run zotero-mcp-wrapper
uv run python -m unittest discover -s tests -v
```

## Packaging

Development and distribution use different entrypoints on purpose:

- source development and unit tests should run from the Python project
- live smoke tests and future skill distribution should use the packaged binary

Build the macOS binary with:

```bash
./scripts/build_macos_binary.sh
```

This produces:

```text
dist/zotero-mcp-wrapper
```

Run a live smoke test against the packaged binary with:

```bash
uv run python scripts/live_smoke_test.py
```

The smoke test talks newline-delimited JSON over stdio to the packaged wrapper and then exercises the real `zotero-mcp` child process.

## Environment Variables

The MVP reads these environment variables:

- `ZOTERO_MCP_BIN`
- `ZOTERO_MCP_ARGS`
- `ZOTERO_APP_PATH`
- `ZOTERO_LOCAL_HOST`
- `ZOTERO_LOCAL_PORT`
- `ZOTERO_STARTUP_TIMEOUT_SEC`
- `ZOTERO_CONNECT_TIMEOUT_SEC`
- `ZOTERO_AUTO_LAUNCH`
- `ZOTERO_READY_STABLE_POLLS`
- `ZOTERO_ADD_LOCAL_FILE_TOKEN`
- `ZOTERO_ADD_LOCAL_FILE_PATH`
- `ZOTERO_ADD_LOCAL_FILE_TIMEOUT_SEC`

Defaults are defined in `zotero_mcp_wrapper/config.py`.
