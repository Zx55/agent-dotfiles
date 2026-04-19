---
name: dayu
description: Use Dayu for dialogue-first research on listed companies. Use when the user mentions Dayu or asks public-company earnings, filings, risk, business-model, or investment-research questions where Dayu's filing workflow is useful. Default to conversational answers, use US filing download when appropriate, and ask for uploads for A-share or Hong Kong materials.
---

# Dayu Research

Use Dayu as a dialogue-first listed-company research tool inside a general AI coding or agent environment.

Default behavior:

- when Dayu is engaged, treat Dayu's output as the analytical source of truth and do not perform a separate host-side company analysis
- answer in normal conversation, not as a generated report
- choose between `dayu-cli prompt` and `dayu-cli interactive` based on whether the work is single-turn or ongoing multi-turn research
- only use Dayu report generation when the user explicitly asks for a report, draft, markdown, docx, html, or pdf
- let Dayu do the company analysis; the host should orchestrate inputs and relay outputs, not run a second independent analysis path
- expect `dayu-cli` analysis calls to take real time; waiting 2-3 minutes is normal and should not be treated as a hang by itself

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

## Guardrail: Dialogue First

This skill is primarily for dialogue-first usage. Even when Dayu is used internally:

- return the result as a normal answer in this chat
- summarize what Dayu found instead of dumping raw CLI output
- avoid generating reports unless the user explicitly asks for one

If you use Dayu writing or render commands internally for synthesis, consume the result yourself and answer conversationally unless the user asked to receive the artifact.

## Operating Rules

When this skill is active:

- Dayu is the system of record for substantive company analysis
- the host may prepare inputs, choose commands, and summarize outputs, but should not start a second parallel analysis path
- narrow framing checks are fine, but "cross-checking" must not become host-side financial analysis
- if Dayu's first answer is incomplete, ask Dayu a narrower follow-up question
- waiting 2-3 minutes for `dayu-cli` analysis is normal; do not treat a short silent period as a hang
- only fall back outside Dayu when there is real failure evidence, and clearly separate that fallback from Dayu-originated conclusions

Read [references/routing.md](references/routing.md) for the detailed execution contract behind these rules.

## Readiness Check

Before using Dayu, confirm the installation is healthy:

- `dayu-cli` exists
- the default workspace exists at `~/.dayu/workspace`
- `~/.dayu/workspace/config` is populated

If any of that is missing or broken, use the sibling skill [dayu-installation](../dayu-installation/SKILL.md).

## Routing Workflow

### 1. Decide whether Dayu is the right tool

If the user is asking about a public company in a filing-driven or research-driven way, Dayu is a good fit.

If the user is only asking for generic background or current news, do not force Dayu.

### 2. Identify the company and market

Resolve the company into a likely ticker and market.

Use the lightest path that is reliable:

- if the user gives a ticker, use it
- if the market is obvious from ticker shape, infer it
- if the company name is ambiguous, do a quick search to confirm listing market

Prefer these routing rules:

- likely US listing: `AAPL`, `NVDA`, `MSFT`, `BABA` style tickers
- likely Hong Kong listing: `.HK` suffix or well-known HK tickers like `9988.HK`
- likely A-share listing: `600519`, `000001.SZ`, `600036.SH` style forms

If the market is still ambiguous after a quick check, ask the user one short clarifying question.

### 3. Check whether local materials already exist

Before downloading or asking for upload, inspect whether the workspace already appears to have company materials under:

```bash
~/.dayu/workspace/portfolio/<ticker>
```

Look for existing filings or supporting materials first. If relevant local materials already exist, prefer using them immediately instead of downloading or asking the user to upload again.

### 4. Route by market

For US-listed companies:

- if relevant filings are not already available locally, prefer Dayu's native download flow
- then use Dayu for question answering
- do not download the same materials again for a second host-side analysis path once Dayu has the needed inputs

For A-share or Hong Kong companies:

- do not invent a custom downloader as the default path
- ask the user to upload the filing PDF or supporting materials
- tell the user what minimum material is most useful, such as the latest annual report, interim report, or earnings deck/transcript
- once documents are uploaded, use Dayu for question answering
- do not independently read and analyze those same PDFs outside Dayu unless Dayu is blocked

Dayu's current stable download advantage is US SEC filings. Treat A-share and Hong Kong support as upload-first unless the user explicitly wants help finding source documents.

### 5. Choose the execution mode

Choose the mode based on interaction shape.

Use `prompt` when:

- the user asked one concrete question
- you want a clean single result to summarize back
- you are integrating Dayu into a broader external conversation

Use `interactive` when:

- the user wants to stay on one company for a while
- the plan involves many follow-up questions
- keeping Dayu's own multi-turn session state is useful
- the user explicitly wants Dayu's terminal chat mode

Both are first-class modes. `prompt` is the default for single-turn integration, while `interactive` is the default for genuine Dayu-side multi-turn work.

Before asking Dayu, it is acceptable to do one narrow framing check such as clarifying whether "latest complete fiscal year" means FY2025 versus the latest quarter. After that, let Dayu do the substantive analysis.

### 6. Answer conversationally

After using Dayu:

- explain the result directly in chat
- cite what kind of material Dayu used when helpful, for example downloaded SEC filings or uploaded PDFs
- mention any important limitations, such as missing local filings or the need for upload on A-share or Hong Kong names

## Primary Command Patterns

### Conversational research

Use `prompt` for single-turn research:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> "<question>"
```

Omit `--ticker` only when the prompt already clearly identifies the subject and that is intentional. In most cases, pass the ticker explicitly.

### US filing download

When the company is US-listed and filings are not already available:

```bash
dayu-cli download --base ~/.dayu/workspace --ticker <TICKER>
```

### Multi-turn terminal mode

Use `interactive` for ongoing company research:

```bash
dayu-cli interactive --base ~/.dayu/workspace
```

Read [references/interactive.md](references/interactive.md) for session behavior, reuse, and exit caveats.

### More detail

- Read [references/routing.md](references/routing.md) for the intent-to-command map.
- Read [references/materials.md](references/materials.md) for upload-first flows and minimum metadata.
- Read [references/ah_share_download.md](references/ah_share_download.md) when the target is A-share or Hong Kong and documents still need to be downloaded manually or with browser help.
- Read [references/interactive.md](references/interactive.md) for multi-turn terminal use.
- Read [references/reporting.md](references/reporting.md) only when the user explicitly asks for a report or export artifact.

## Output Expectations

When using this skill, produce:

- a conversational answer derived from Dayu's output, not a parallel host-side analysis
- the resolved company or ticker when relevant
- whether Dayu used downloaded US filings, uploaded local materials, or neither
- any missing-material limitation that affects confidence
- a short next-step suggestion only when it materially helps
