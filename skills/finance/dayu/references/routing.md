# Routing Guide

This reference maps user intent to Dayu behavior.

## Default path

For analytical questions, use a labeled prompt:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<question>"
```

Then return Dayu's final answer directly in chat by default.

Default posture:

- use `prompt --label` for both the first question and follow-up turns
- let the label carry Dayu-side continuity instead of reconstructing context in the host
- rely on Dayu's progress/status output for liveness

Before creating a new label, check active labeled conversations:

```bash
dayu-cli conv --base ~/.dayu/workspace list
```

If the desired label already exists, reuse it only when the user is continuing that same research thread. Otherwise choose a distinct descriptive label.

## Core rule

- the host prepares the request and relays the result
- Dayu performs the substantive company analysis
- if the first Dayu answer is not enough, ask Dayu a better follow-up instead of starting a separate analysis track
- a narrow framing check is fine, but "cross-validation" must not turn into a second substantive analysis outside Dayu

## Intent map

### Public-company analysis question

Examples:

- "看下英伟达最新财报的主要风险"
- "拼多多这季度利润率为什么变了"
- "阿里值得继续深研吗"

Default path:

1. resolve ticker and market
2. inspect whether local materials already exist under `~/.dayu/workspace/portfolio/<ticker>`
3. if US-listed and local filings are missing, run `download`
4. choose or create a non-conflicting label for this research thread
5. let Dayu answer the analytical question
6. relay Dayu's final answer directly unless the user explicitly asks for a summary or rewrite

Do not append a second host-originated analysis stage after step 5.

### Label management

Use labels as the skill-owned conversation handle.

Label rules:

- list existing labels before creating a new one
- choose labels that identify the company and thread, for example `aapl-risk`, `nvda-margin`, or `1810hk-fy2025`
- reuse an existing label only for the same company and same analytical thread
- when the user starts a materially different topic, create a new label instead of overloading the old one
- if a label needs to be retired, use `dayu-cli conv --base ~/.dayu/workspace remove --label <LABEL>` only when the user asks to release it

Useful checks:

```bash
dayu-cli conv --base ~/.dayu/workspace list
dayu-cli conv --base ~/.dayu/workspace status --label <LABEL>
```

### User asks a follow-up after a prior labeled prompt

Examples:

- "上面那个保守情景是怎么假设的"
- "基于刚才的结论，再展开说下现金流"
- "继续追一下海外风险"

Default path:

1. keep using the same label when the follow-up belongs to the same thread
2. pass the new question through `dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<question>"`
3. let Dayu use the labeled conversation state; do not run a parallel host-side recap analysis
4. if the follow-up starts a materially different topic, create a new checked label

## Waiting rule

For `dayu-cli prompt` in particular:

### Waiting posture

- do not treat a short silent period as proof of failure
- do not use elapsed time by itself as the failure test
- keep the original `dayu-cli prompt --label` session open and watch its progress/status output before starting side checks
- prefer waiting on the original session over opening sidecar sleep commands or replacement runs
- if progress/status output continues, treat the run as active and keep waiting
- while `dayu-cli runs` still shows the run as active, do not cancel it, do not rerun the same question, do not switch models, and do not add `--max-iterations` unless the user explicitly asked for a shorter or faster tradeoff
- treat `final_answer` plus stream or command completion as the success signal

### Check sequence

When output appears stuck, use this order:

1. wait on the original Dayu command session and read newly arrived progress, status, or answer output first
2. if the original session has been quiet for a materially long period, poll that same command session again before opening side checks
3. if it is still quiet, check active runs:

```bash
dayu-cli runs --base ~/.dayu/workspace
```

4. if you need a broader host view, check:

```bash
dayu-cli host --base ~/.dayu/workspace status
```

5. if Dayu still shows an active run, continue waiting on the original command output and keep status checks low-frequency
6. only move to failure handling when the run no longer appears active and there is explicit failure evidence

### Failure evidence

Only treat the run as blocked when there is real failure evidence such as:

- the process exits with an error
- Dayu emits explicit error output
- Dayu emits explicit cancelled output such as timeout cancellation
- the run disappears from the active list and the command output confirms cancellation or failure

Important exception for filing ingestion:

- if `upload_filing` reports explicit PDF conversion failure such as `Docling 转换失败`, do not keep retrying the same PDF upload path
- for Hong Kong or A-share filings, switch to the Markdown filing fallback in [materials.md](materials.md)
- this is still a Dayu ingestion path, not host-side financial analysis

### User asks to prepare documents

Examples:

- "把苹果财报拉下来"
- "把这份港股财报导进去"
- "把电话会纪要也放进去"

Path:

- US listing -> `download`
- A-share / HK / local PDF -> download guidance from [ah_share_download.md](ah_share_download.md), then upload flow from [materials.md](materials.md)
- if a Hong Kong / A-share filing PDF fails in Dayu conversion, follow the Markdown fallback in [materials.md](materials.md) before trying broader workarounds

### User asks for continuing back-and-forth analysis

Examples:

- "我们持续聊这家公司"
- "接下来我会连着追问几个问题"

Use the same `prompt --label` conversation for the whole thread. If Dayu's first answer is incomplete, continue the same analytical path by asking Dayu follow-up questions under the same label.

### User asks for a report

Examples:

- "写一份买方分析报告"
- "出个 markdown 草稿"
- "导成 pdf"

Read [reporting.md](reporting.md).

Do not default into report generation if the user only asked a research question.

## Market routing

### US-listed

Prefer Dayu native download first:

```bash
dayu-cli download --base ~/.dayu/workspace --ticker <TICKER>
```

### Hong Kong or A-share

Prefer upload-first. Do not silently build a custom downloader in the skill.

If the user does not have documents ready:

- follow [ah_share_download.md](ah_share_download.md) to locate an official filing source
- ask them to upload the filing PDF or supporting material
- use [materials.md](materials.md) for the minimum useful set and upload flow

Once the material is ready, return to Dayu for the actual analysis rather than analyzing the downloaded document directly outside Dayu.

## When not to use Dayu

Skip Dayu when:

- the question is generic and not filing-driven
- the company is private
- the task is pure news search
- the user wants a quick answer that does not need local filing context
