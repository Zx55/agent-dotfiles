---
name: dayu
description: Use Dayu for dialogue-first research on listed companies. Use when the user mentions Dayu or asks public-company earnings, filings, risk, business-model, or investment-research questions where Dayu's filing workflow is useful. Default to returning Dayu's answer directly in chat, use US filing download when appropriate, and ask for uploads for A-share or Hong Kong materials.
---

# Dayu Research

Use Dayu as a dialogue-first listed-company research tool inside a general AI coding or agent environment.

## When To Use

Use this skill when the user:

- explicitly mentions `dayu`, `dayu-cli`, or `dayu-agent`
- asks to analyze a listed company through filings or earnings materials
- asks for public-company risk review, business analysis, financial explanation, or investment-research style synthesis
- wants to prepare or ingest filings and related materials before asking research questions

Do not use this skill by default for:

- general company introductions with no filing or research angle
- breaking-news monitoring
- private-company questions
- normal web research that does not benefit from Dayu's filing workflow

## Default Workspace

Unless the user explicitly specifies another workspace, use:

```bash
~/.dayu/workspace
```

Pass it explicitly to Dayu commands with `--base ~/.dayu/workspace`.

## Core Rules

### Analysis Ownership

- Dayu is the system of record for substantive company analysis
- the host may prepare inputs, choose commands, and relay outputs, but should not start a second parallel analysis path
- narrow framing checks are fine, but "cross-checking" must not become host-side financial analysis
- if Dayu's first answer is incomplete, ask Dayu a narrower follow-up question

### Default Output

- return Dayu's final answer directly in chat by default
- do not paraphrase, summarize, translate, critique, or restructure it unless the user explicitly asks
- do not generate reports unless the user explicitly asks for a report, draft, markdown, docx, html, or pdf

### Session Continuity

- default to `dayu-cli prompt` for the first analytical question; do not default to `interactive`
- do not assume a new `dayu-cli prompt` call remembers prior `prompt` turns
- if the user asks one or two follow-up questions after a prior `prompt`, keep using `prompt` but include a short recap of the prior Dayu answer and the current question in the new prompt
- only switch to `interactive` when the user clearly wants a sustained multi-turn Dayu-side thread or the follow-up chain is strongly dependent on prior answers
- when the host starts `interactive`, prefer `dayu-cli interactive --base ~/.dayu/workspace --new-session` unless you are intentionally resuming a skill-owned interactive session from the same workflow
- when switching from `prompt` to `interactive`, seed the first interactive message with a compact recap: ticker, materials used, prior conclusion, and the new question
- remember that `interactive` is a terminal TTY workflow; it is not the default path for normal single-turn skill use

### Waiting and Failure

- prefer explicit Dayu completion or failure signals over elapsed-time heuristics
- for `dayu-cli prompt`, wait on the original session first; the detailed 180-second initial wait and low-frequency status-check rules live in [references/routing.md](references/routing.md)
- while a run remains active, do not cancel it, do not restart the same prompt, do not switch models, and do not add limiting flags such as `--max-iterations` unless the user explicitly asked for that tradeoff
- for Hong Kong or A-share PDF conversion failures such as `Docling 转换失败`, follow the Markdown fallback in [references/materials.md](references/materials.md)

## Readiness Check

Before using Dayu, confirm the installation is healthy:

- `dayu-cli` exists
- the default workspace exists at `~/.dayu/workspace`
- `~/.dayu/workspace/config` is populated

If any of that is missing or broken, use the sibling skill [dayu-installation](../dayu-installation/SKILL.md).

## Reference Map

- Read [references/routing.md](references/routing.md) for the single-turn path, waiting checks, and market routing.
- Read [references/materials.md](references/materials.md) for upload commands, minimum metadata, and PDF-to-Markdown fallback.
- Read [references/ah_share_download.md](references/ah_share_download.md) only when the target is A-share or Hong Kong and the official documents still need to be downloaded.
- Read [references/interactive.md](references/interactive.md) when the user wants Dayu-side multi-turn continuity.
- Read [references/reporting.md](references/reporting.md) only when the user explicitly asks for a report or export artifact.

## Output Expectations

When using this skill, return Dayu's final answer directly in chat. Add source or limitation notes only when they materially help, for example when Dayu relied on downloaded SEC filings, uploaded PDFs, or incomplete local materials.
