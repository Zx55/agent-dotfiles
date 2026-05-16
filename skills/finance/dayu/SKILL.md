---
name: dayu
description: Use Dayu for dialogue-first listed-company research. Default to `dayu-cli prompt --label --ticker`, prepare clearer prompts when useful, manage Dayu labels, and relay Dayu CLI output without host-side rewriting unless the user explicitly asks. Upload only user-provided non-filing materials.
---

# Dayu Research

Use Dayu as the system of record for listed-company financial research.

## When To Use

Use this skill when the user:

- explicitly mentions `dayu`, `dayu-cli`, or `dayu-agent`
- asks to analyze a listed company through filings or earnings materials
- asks for public-company risk review, business analysis, financial explanation, or investment-research synthesis
- wants Dayu to consider user-provided non-filing materials such as transcripts, presentations, notes, or memos

Do not use this skill by default for:

- generic company introductions with no filing or research angle
- breaking-news monitoring
- private-company questions
- general web research that does not benefit from Dayu's filing workflow

## Workspace

Unless the user specifies another workspace, use:

```bash
~/.dayu/workspace
```

Pass it explicitly with `--base ~/.dayu/workspace`.

Before using Dayu, confirm:

- `dayu-cli` exists
- `~/.dayu/workspace` exists
- `~/.dayu/workspace/config` is populated

If setup is missing or broken, use [dayu-installation](../dayu-installation/SKILL.md).

## Responsibilities

Dayu owns:

- substantive company analysis
- filing discovery, filing download, and filing tool behavior when `--ticker` is supplied
- conversation continuity inside labeled prompt sessions

The host agent owns:

- resolving the ticker and market well enough to call Dayu
- preparing a clearer prompt from terse user input
- choosing, checking, and reusing labels
- relaying Dayu CLI output to the user
- reporting command failures or setup gaps separately from Dayu's answer

The host agent must not:

- run a second parallel financial analysis path
- pre-download or pre-upload filings for normal listed-company questions
- use `interactive`, `write`, or `download` as normal host-agent entrypoints
- rewrite, compress, translate, summarize, critique, or restructure Dayu output unless the user explicitly asks

## Standard Workflow

For analytical questions, use `prompt --label --ticker`:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared question>"
```

Default sequence:

1. Resolve ticker and market.
2. Prepare the user request into a clear financial-analysis prompt.
3. Run `dayu-cli conv --base ~/.dayu/workspace list`.
4. Reuse a label only for the same company and same analytical thread.
5. If a label's ownership is unclear, run `dayu-cli conv --base ~/.dayu/workspace status --label <LABEL>`.
6. Run `dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared question>"`.
7. Relay Dayu CLI output directly.

## Input Preparation

User questions may be short or lack financial-analysis conventions. Before calling Dayu, the host may lightly normalize the prompt.

Allowed additions:

- analysis scope
- comparison period
- materiality lens
- uncertainty handling
- requested output shape
- reminders to use filings and disclose evidence limits

Do not add:

- unsupported facts
- host-side conclusions
- valuation calls not requested by the user
- evidence claims that Dayu has not produced
- a different company, ticker, time horizon, or risk appetite from the user's intent

Ask a brief clarification when the company, ticker, time horizon, or requested decision frame is materially ambiguous.

## Output Relay

Relay the relevant `dayu-cli prompt` output directly in chat.

Preserve Dayu's:

- wording
- structure
- numbers
- caveats
- source mentions
- uncertainty language

If the user asks for a summary, translation, rewrite, extraction, or a specific report format, prefer putting that transformation request into the Dayu prompt. If a host-side transformation is still needed, clearly separate it from the relayed Dayu output.

Host-side notes should be limited to command failure, missing setup, or a short limitation note when Dayu did not produce an answer. Put those notes outside the relayed Dayu output.

## Label Rules

Labels are Dayu's reusable conversation handle.

- Always use labeled prompts for reusable research state.
- Run `dayu-cli conv --base ~/.dayu/workspace list` before creating a label.
- Use stable, descriptive labels such as `<ticker>-<topic>` or `<ticker>-<YYYYMMDD>-<topic>`.
- Avoid vague labels such as `test` or `default`.
- Reuse a label only when continuing the same company and same analytical thread.
- Create a new label for materially different topics.
- Use `dayu-cli conv --base ~/.dayu/workspace status --label <LABEL>` when ownership is unclear.
- Use `dayu-cli conv --base ~/.dayu/workspace remove --label <LABEL>` only when the user asks to retire or clear that label.

## Waiting And Failure

- Prefer explicit Dayu completion or failure signals over elapsed-time heuristics.
- Keep the original `dayu-cli prompt --label` process open while it is active.
- Use Dayu's progress and status output as the primary liveness signal.
- Do not enable reasoning-stream output by default.
- While a run remains active, do not cancel it, restart the same prompt, switch models, or add limiting flags such as `--max-iterations` unless the user explicitly asks for that tradeoff.

For detailed waiting checks and intent routing, read [references/routing.md](references/routing.md).

## References

- Read [references/routing.md](references/routing.md) for prompt routing, labels, follow-ups, waiting, and failure handling.
- Read [references/materials.md](references/materials.md) only for user-provided non-filing materials and supplemental-document upload.
- Read [references/reporting.md](references/reporting.md) only when the user explicitly asks for report-shaped output or an export artifact.
