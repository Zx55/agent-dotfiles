# Explicit Report Requests

Use this reference only when the user explicitly asks for report-shaped output or an export artifact.

## Default Boundary

Do not generate reports by default. Normal Dayu usage is dialogue-first research through:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared question>"
```

Do not switch to `write` as a host-agent entrypoint.

## Report-Shaped Prompt

Put the requested report shape into the Dayu prompt:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared report request>"
```

Examples of report-shape constraints to include when the user asks:

- buy-side memo
- markdown draft
- risk memo
- thesis, key evidence, risks, and watchlist
- conservative, base, and upside cases

Relay Dayu output directly. If the user asked for a different language, format, or extraction, put that requirement into the Dayu prompt whenever possible.

## Export Artifacts

Use `dayu-render` only when the user explicitly wants export formatting such as HTML or PDF.

Verify invocation shape before relying on it:

```bash
dayu-render
```

Suggested flow:

1. Choose or reuse the correct label.
2. Run `dayu-cli prompt --label --ticker` with the report request.
3. Relay Dayu output directly.
4. Render only if the user explicitly asks for an export artifact.
