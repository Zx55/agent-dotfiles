# Routing Guide

This reference maps user intent to Dayu commands.

## Canonical Command

For listed-company research, use:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared question>"
```

This is the normal host-agent entrypoint for:

- first-turn research
- follow-up questions
- report-shaped answers
- filing preparation requests for a listed company

Do not pre-run `download` or `upload_filing` for normal research questions. With `--ticker`, Dayu owns filing discovery, download, and filing-tool behavior.

## Request Preparation

Prepare terse user input into a clear Dayu prompt when useful.

Good prompt preparation may add:

- scope, such as risk, margin, cash flow, segment, valuation sensitivity, or governance
- comparison period, such as latest quarter, year over year, or last annual report
- materiality lens, such as what matters for investment judgment
- uncertainty handling, such as call out missing filings or weak evidence
- output shape, such as bullets, table, conservative/base/upside cases, or watchlist

Do not add:

- facts not provided by the user or Dayu
- your own financial conclusion
- valuation calls not requested by the user
- evidence claims before Dayu has produced evidence
- a changed company, ticker, time horizon, or risk appetite

Ask a brief clarification when the ticker, company identity, time horizon, or decision frame is materially ambiguous.

## Label Registry

Before creating a label:

```bash
dayu-cli conv --base ~/.dayu/workspace list
```

Reuse an existing label only when the user is continuing the same company and the same analytical thread.

If a label name looks familiar but ownership is unclear:

```bash
dayu-cli conv --base ~/.dayu/workspace status --label <LABEL>
```

Create a new label when:

- the company changes
- the analytical topic changes materially
- the prior label's ownership is unclear after inspection

Retire a label only when the user asks:

```bash
dayu-cli conv --base ~/.dayu/workspace remove --label <LABEL>
```

## Default Research Flow

Examples:

- "看下英伟达最新财报的主要风险"
- "拼多多这季度利润率为什么变了"
- "阿里值得继续深研吗"

Steps:

1. Resolve ticker and market.
2. Prepare the user's question into a clear Dayu prompt.
3. Check labels with `conv list`.
4. Reuse or create a label.
5. Run `dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared question>"`.
6. Keep the original command open until Dayu completes or fails.
7. Relay Dayu output directly, unless the user explicitly asked for a transformation.

Do not append a second host-originated analysis stage after Dayu answers.

## Follow-Ups

Examples:

- "上面那个保守情景是怎么假设的"
- "基于刚才的结论，再展开说下现金流"
- "继续追一下海外风险"

Use the same label when the follow-up belongs to the same analytical thread:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared follow-up>"
```

Create a new label if the follow-up starts a materially different topic.

If Dayu's first answer is incomplete, ask Dayu a narrower follow-up under the same label instead of starting a host-side analysis path.

## Document Preparation Requests

Examples:

- "把苹果财报准备好"
- "把这家公司最新财报拉一下"
- "先检查一下有没有可用财报"

For listed-company filings, still use `prompt --label --ticker` and ask Dayu to prepare or check the filings:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared filing-prep request>"
```

If Dayu says filing access failed or the filing is unavailable, report that result directly. Do not build a separate host-side download path.

If the user provides a local non-filing material, use [materials.md](materials.md).

## Report Requests

Examples:

- "写一份买方分析报告"
- "出个 markdown 草稿"
- "按投资备忘录格式输出"

Use `prompt --label --ticker` and put the requested report shape into the Dayu prompt. Read [reporting.md](reporting.md) for export boundaries.

Do not switch to `write` as a host-agent entrypoint.

## Market And Ticker Routing

Use `prompt --label --ticker` for US, A-share, and Hong Kong analysis.

Ticker examples:

- US: `BABA`
- Hong Kong: `9988.HK`
- A-share: `688981`

Use CSV aliases only when Dayu needs a canonical ticker plus known aliases:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker BABA,9988,9988.HK --label baba-hk-us "<prepared question>"
```

## Waiting Rule

For `dayu-cli prompt`:

- Do not treat a short silent period as proof of failure.
- Do not use elapsed time alone as the failure test.
- Keep the original command session open and watch its progress, status, and answer output.
- Prefer waiting on the original session over opening sidecar sleep commands or replacement runs.
- If progress or status output continues, treat the run as active.
- While `dayu-cli runs` shows the run as active, do not cancel it, rerun the same prompt, switch models, or add limiting flags unless the user explicitly asked for that tradeoff.
- Treat `final_answer` plus stream or command completion as the success signal.

When output appears stuck:

1. Wait on the original Dayu command session and read new output first.
2. Poll that same command session again after a materially long quiet period.
3. If it is still quiet, check active runs:

```bash
dayu-cli runs --base ~/.dayu/workspace
```

4. If you need a broader host view, check:

```bash
dayu-cli host --base ~/.dayu/workspace status
```

5. Continue waiting if Dayu still shows an active run.
6. Move to failure handling only when there is explicit failure evidence.

Failure evidence includes:

- the process exits with an error
- Dayu emits explicit error output
- Dayu emits explicit cancellation output
- the run disappears from the active list and the command output confirms cancellation or failure

## When Not To Use Dayu

Skip Dayu when:

- the question is generic and not filing-driven
- the company is private
- the task is pure news search
- the user wants a quick answer that does not need local filing context
