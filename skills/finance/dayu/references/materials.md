# Non-Filing Material Upload

Use this reference only when the user provides local non-filing material that Dayu should consider.

Examples:

- earnings call transcripts
- investor presentations
- management commentary
- notes or memos
- other supplemental research material

Do not upload financial reports as a default host-agent path. For listed-company filings, use `prompt --label --ticker` and let Dayu manage filing discovery and download.

## Required Context

Before upload, try to confirm:

- ticker
- file path
- material type
- material name
- fiscal year or period when relevant
- company name when the workspace does not already know the company

Use `--infer` when the ticker is good enough for enrichment and the user has not supplied all company metadata.

## Upload Command

Use `upload_material` for non-filing material:

```bash
dayu-cli upload_material \
  --base ~/.dayu/workspace \
  --ticker <TICKER> \
  --action create \
  --forms <FORM_TYPE> \
  --material-name "<NAME>" \
  --files <FILE1> [FILE2 ...]
```

Useful `material-name` examples:

- `2025Q1 earnings call transcript`
- `FY2024 investor presentation`
- `management commentary notes`

## After Upload

Return to the canonical prompt path:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> --label <LABEL> "<prepared question>"
```

Relay Dayu output directly.
