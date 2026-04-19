# Explicit Report Mode

Use this reference only when the user explicitly asks for a report, draft, markdown, docx, html, or pdf output.

## Default rule

Do not generate reports by default. The normal mode for this skill is dialogue-first research.

## Writing

Dayu exposes report writing through `write`.

Typical command:

```bash
dayu-cli write --base ~/.dayu/workspace --ticker <TICKER>
```

Useful options:

- `--chapter <NAME>` for one chapter
- `--resume` to continue previous output
- `--fast` to skip audit and repair stages
- `--summary` to inspect the last write pipeline result
- `--infer` to run company facet inference without full writing
- `--output <DIR>` to override the draft directory

## How to use report mode from a host agent

Even in explicit report mode, decide whether the user wants:

- the artifact itself
- a conversational summary based on the artifact
- both

If the user asked for analysis and only loosely mentioned a report, it is acceptable to generate the draft internally, read it, and reply conversationally.

If the user clearly asks for the report output, give them the artifact path.

## Rendering

Use `dayu-render` only when the user explicitly wants export formatting.

Current install verification suggests the binary prints usage when invoked without arguments. Exact argument handling may vary by release, so verify with:

```bash
dayu-render
```

before relying on a specific invocation shape.

## Suggested workflow

1. Make sure the relevant company materials already exist in `~/.dayu/workspace`.
2. Run `dayu-cli write`.
3. Inspect the produced markdown or summary.
4. Only then decide whether to render or simply answer in chat.
