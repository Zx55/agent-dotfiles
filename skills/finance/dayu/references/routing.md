# Routing Guide

This reference maps user intent to Dayu behavior.

## Default path

For many single-turn questions, use:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> "<question>"
```

Then return Dayu's final answer directly in chat by default.

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
4. choose `prompt` or `interactive`
5. let Dayu answer the analytical question
6. relay Dayu's final answer directly unless the user explicitly asks for a summary or rewrite

Do not append a second host-originated analysis stage after step 5.

## Waiting rule

For `dayu-cli prompt` in particular:

### Waiting posture

- do not treat a short silent period as proof of failure
- do not use elapsed time by itself as the failure test
- keep the original `dayu-cli prompt` session open and give it an initial wait window of at least 180 seconds
- prefer waiting on the original session over opening sidecar sleep commands or replacement runs
- while `dayu-cli runs` still shows the run as active, do not cancel it, do not rerun the same question, do not switch models, and do not add `--max-iterations` unless the user explicitly asked for a shorter or faster tradeoff
- treat `final_answer` plus stream or command completion as the success signal
### Check sequence

When output appears stuck, use this order:

1. wait on the original Dayu command session for the initial 180-second window
2. poll the original Dayu command session again and read any newly arrived output
3. if it is still quiet, check active runs:

```bash
dayu-cli runs --base ~/.dayu/workspace
```

4. if you need a broader host view, check:

```bash
dayu-cli host --base ~/.dayu/workspace status
```

5. if Dayu still shows an active run, continue waiting on the original command output and do not perform another status check for at least 60 seconds
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

If the user wants many linked follow-ups on the same company, prefer `interactive`.

Use `prompt` instead if you only need one or two clearly framed turns that can be returned directly.

If Dayu's first answer is incomplete, continue the same analytical path by asking Dayu follow-up questions.

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
