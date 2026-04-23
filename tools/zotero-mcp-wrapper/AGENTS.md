# zotero-mcp-wrapper

## Goal

`zotero-mcp-wrapper` is a small macOS-only request-aware stdio proxy for `zotero-mcp`.

The wrapper exists to solve one concrete problem:

- when a client sends an MCP request that needs Zotero local API, ensure Zotero Desktop is available before forwarding that request to `zotero-mcp`

## Source Of Truth

The working design for this repository comes from the discussion in this workspace and should remain consistent with these current boundaries:

- macOS only
- stdio only
- wraps `zotero-mcp` only
- transparent forwarding by default
- no business-level interpretation of Zotero tool semantics

If implementation pressure conflicts with these constraints, prefer keeping the scope narrow instead of widening the design.

## Non-Negotiable Boundaries

The wrapper should own:

- launching the real `zotero-mcp` child process
- minimal MCP frame parsing needed for safe forwarding
- request-time Zotero availability checks
- Zotero Desktop auto-launch attempts on macOS
- clear local errors when Zotero cannot be made ready

The wrapper should not own:

- Zotero library policy
- paper-reading workflow policy
- report generation logic
- generic MCP framework features
- long-running keepalive behavior unless explicitly added later

## Implementation Style

- keep the code path transparent and auditable
- prefer stdlib-first Python
- avoid abstractions that imply future platform support before it exists
- do not rewrite MCP payloads except where strictly necessary to inspect request kind or emit a clear wrapper-owned error
- preserve the upstream `zotero-mcp` protocol behavior as much as possible

## Project Structure

The initial structure is:

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

Current ownership:

- `cli.py` wires the runtime together
- `config.py` owns env-driven runtime configuration
- `framing.py` owns MCP stdio JSON-line parsing
- `child_process.py` owns the wrapped `zotero-mcp` subprocess
- `zotero_runtime.py` owns macOS Zotero launch and readiness checks
- `proxy.py` owns request-aware forwarding semantics
- `tests/` should stay focused on deterministic unit coverage for these blocks

As implementation grows, prefer adding focused modules under `zotero_mcp_wrapper/` rather than letting `proxy.py` or `cli.py` absorb too many responsibilities.

## Development Notes

- use `uv` for local environment management
- keep packaging simple so a future installation skill can ship a built binary
- keep source execution and packaged execution as separate paths:
  - source work and unit tests should run from the Python project
  - live smoke tests should target `dist/zotero-mcp-wrapper`
- do not optimize for Linux or Windows before there is a real use case
- if you need a temporary local launcher while developing, make it explicitly `cd` into the repository root before running `.venv/bin/python3 -m zotero_mcp_wrapper.cli`; do not rely on external cwd