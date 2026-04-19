# Routing Guide

This reference maps user intent to Dayu behavior.

## Default path

For many single-turn questions, use:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> "<question>"
```

Then summarize the answer conversationally.

Important rule:

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
6. summarize Dayu's answer conversationally

Do not append a second host-originated analysis stage after step 5.

## Waiting rule

When Dayu is running, waiting a few minutes is normal.

For `dayu-cli prompt` in particular:

- 2-3 minutes of runtime can be normal
- do not treat a short silent period as proof of failure
- do not switch to host-side fallback just because the command feels slow

Only treat the run as blocked when there is real failure evidence such as:

- the process exits with an error
- Dayu emits explicit error output
- the runtime is well beyond normal waiting behavior with no sign of progress

### User asks to prepare documents

Examples:

- "把苹果财报拉下来"
- "把这份港股财报导进去"
- "把电话会纪要也放进去"

Path:

- US listing -> `download`
- A-share / HK / local PDF -> download guidance from [ah_share_download.md](ah_share_download.md), then upload flow from [materials.md](materials.md)

### User asks for continuing back-and-forth analysis

Examples:

- "我们持续聊这家公司"
- "接下来我会连着追问几个问题"

If the user wants many linked follow-ups on the same company, prefer `interactive`.

Use `prompt` instead if you only need one or two clearly framed turns.

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
- tell them the minimum useful set, such as latest annual report plus latest interim report if available
- optionally help locate an official IR or exchange page, but keep that separate from Dayu's native ingestion path

Once the material is ready, return to Dayu for the actual analysis rather than analyzing the downloaded document directly outside Dayu.

## When not to use Dayu

Skip Dayu when:

- the question is generic and not filing-driven
- the company is private
- the task is pure news search
- the user wants a quick answer that does not need local filing context
