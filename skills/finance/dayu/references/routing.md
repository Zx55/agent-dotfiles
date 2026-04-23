# Routing Guide

This reference maps user intent to Dayu behavior.

## Default path

For many single-turn questions, use:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --thinking "<question>"
```

Then return Dayu's final answer directly in chat by default.

Default posture:

- start with `prompt`, not `interactive`
- do not assume a fresh `prompt` call remembers the previous `prompt` answer
- if a later follow-up still fits in one clean question, use another `prompt` and restate the needed context yourself
- only escalate to `interactive` when the user clearly wants Dayu-managed multi-turn continuity

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
4. default to `prompt`; choose `interactive` only when continuity is clearly worth the added session state
5. let Dayu answer the analytical question
6. relay Dayu's final answer directly unless the user explicitly asks for a summary or rewrite

Do not append a second host-originated analysis stage after step 5.

### User asks a follow-up after a prior `prompt`

Examples:

- "上面那个保守情景是怎么假设的"
- "基于刚才的结论，再展开说下现金流"
- "继续追一下海外风险"

Default path:

1. keep using `prompt` for one or two follow-up turns when the next question can be framed cleanly
2. include a concise recap in the new prompt:
   - company / ticker
   - which filing or material was used
   - the prior Dayu conclusion that matters for this follow-up
   - the user's new question
3. do not assume `prompt` is resuming the previous Dayu-side thread
4. if the user keeps drilling down and each next turn depends heavily on the prior answer, switch to `interactive --new-session --thinking`

Do not switch to `interactive` merely because a single follow-up happened.

## Waiting rule

For `dayu-cli prompt` in particular:

### Waiting posture

- do not treat a short silent period as proof of failure
- do not use elapsed time by itself as the failure test
- pass `--thinking` by default so the host has reasoning/tool-visible output as the first liveness clue
- keep the original `dayu-cli prompt --thinking` session open and watch its output before starting side checks
- prefer waiting on the original session over opening sidecar sleep commands or replacement runs
- if `--thinking` continues to produce output, treat the run as active and keep waiting
- while `dayu-cli runs` still shows the run as active, do not cancel it, do not rerun the same question, do not switch models, and do not add `--max-iterations` unless the user explicitly asked for a shorter or faster tradeoff
- treat `final_answer` plus stream or command completion as the success signal
### Check sequence

When output appears stuck, use this order:

1. wait on the original Dayu command session and read newly arrived `--thinking` or answer output first
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

If the user wants many linked follow-ups on the same company, prefer `interactive`.

Use `prompt` instead if you only need one or two clearly framed turns that can be returned directly.

If Dayu's first answer is incomplete, continue the same analytical path by asking Dayu follow-up questions.

When the host decides to switch into Dayu-side continuity:

- prefer `dayu-cli interactive --base ~/.dayu/workspace --new-session --thinking`
- do not rely on bare `interactive` resuming some unknown previous local session
- use the first interactive message to restate the working context:
  - ticker / company
  - materials already available
  - the previous answer's key conclusion
  - the next question to investigate

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
