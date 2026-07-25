---
name: dayu
description: Use Dayu for dialogue-first listed-company research. Default to `dayu-cli prompt --label --ticker --output`, prepare clearer prompts when useful, manage Dayu labels, and deliver 3–5 grounded takeaways plus a link to Dayu's complete Markdown artifact. Upload only user-provided non-filing materials.
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
- choosing a persistent Markdown output path for every prompt
- reading the completed artifact and summarizing it into 3–5 key takeaways
- linking the complete Markdown artifact for deep reading
- reporting command failures or setup gaps separately from Dayu's answer

The host agent must not:

- run a second parallel financial analysis path
- pre-download or pre-upload filings for normal listed-company questions
- use `interactive`, `write`, or `download` as normal host-agent entrypoints
- paste or restate the full Dayu answer in chat
- introduce conclusions that are not grounded in the Markdown artifact

## Standard Workflow

For analytical questions, use `prompt --label --ticker --output`:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> --output "<OUTPUT_MD>" "<prepared question>"
```

Default sequence:

1. Resolve ticker and market.
2. Prepare the user request into a clear financial-analysis prompt.
3. Run `dayu-cli conv --base ~/.dayu/workspace list`.
4. Reuse a label only for the same company and same analytical thread.
5. If a label's ownership is unclear, run `dayu-cli conv --base ~/.dayu/workspace status --label <LABEL>`.
6. Choose a new persistent output path under `~/.dayu/workspace/output/prompt/<TICKER>/`; include the label and a timestamp in the filename so follow-ups do not overwrite earlier answers.
7. Run `dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> --output "<OUTPUT_MD>" "<prepared question>"`.
8. Wait for the success line `Markdown 已保存: <absolute path>`, then read the complete Markdown file.
9. Deliver exactly 3–5 concise, artifact-grounded takeaways and a clickable link to the complete Markdown file.

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

## Output Delivery

Use `--output` for every Dayu prompt, regardless of expected answer length. The CLI writes the final answer to Markdown and suppresses the answer body from terminal output while retaining progress, warnings, label hints, and the final absolute path.

Choose a persistent path, not `/tmp`. Use this shape unless the user specifies another destination:

```text
~/.dayu/workspace/output/prompt/<TICKER>/<YYYYMMDD-HHMMSS>-<LABEL>.md
```

After the command completes:

1. Verify the file exists at the path printed by Dayu.
2. Read the complete file before summarizing it.
3. Write 3–5 concise takeaways in the user's language that preserve Dayu's key conclusions, numbers and periods, caveats, source limits, and uncertainty.
4. Link the artifact with an absolute local-file Markdown link, for example `[完整 Markdown 报告](/absolute/path/to/report.md)`.

Do not paste the report body or reproduce long sections in chat. The summary is a navigation layer, not a second financial-analysis pass. If the user asks for translation, restructuring, extraction, or another report shape, put that requirement into the Dayu prompt so the linked artifact remains the authoritative answer.

If Dayu exits successfully but the artifact is absent or unreadable, report that as a delivery failure. Do not reconstruct the complete answer from progress output.

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
