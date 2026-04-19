# Upload-First Material Flows

Use this reference when the target is A-share, Hong Kong, or any case where the user already has local files.

If the user does not yet have the files, first read [ah_share_download.md](ah_share_download.md).

## Principle

Dayu's stable native downloader is the US SEC flow. For A-share and Hong Kong, default to uploading local documents instead of inventing a downloader inside this skill.

## Filing upload

Use `upload_filing` for a financial report PDF or filing package.

Command shape:

```bash
dayu-cli upload_filing \
  --base ~/.dayu/workspace \
  --ticker <TICKER> \
  --files <FILE1> [FILE2 ...] \
  --fiscal-year <YEAR> \
  --fiscal-period <Q1|Q2|Q3|Q4|FY|H1>
```

Useful optional fields:

- `--filing-date`
- `--report-date`
- `--company-name`
- `--infer`
- `--overwrite`
- `--amended`

## Minimum metadata to collect from the user

When the user uploads a filing, try to confirm:

- ticker
- fiscal year
- fiscal period
- file path

If the workspace does not already know the company, you may also need:

- company name
- or `--infer` if the ticker is good enough for FMP-based enrichment

## Supplementary materials

Use `upload_material` for:

- earnings call transcripts
- investor presentations
- memos
- non-filing research material the user wants included

Command shape:

```bash
dayu-cli upload_material \
  --base ~/.dayu/workspace \
  --ticker <TICKER> \
  --action create \
  --forms <FORM_TYPE> \
  --material-name "<NAME>" \
  --files <FILE1> [FILE2 ...]
```

Examples of reasonable `material-name` values:

- `2025Q1 earnings call transcript`
- `FY2024 investor presentation`
- `management commentary notes`

## Batch import

If the user has a whole folder of filings or materials, use:

```bash
dayu-cli upload_filings_from --base ~/.dayu/workspace --ticker <TICKER> --from <DIR>
```

This generates an upload script rather than fully ingesting everything by itself. Use it when the folder is large or mixed.

## After upload

Once the relevant documents are present, switch back to the normal conversational path:

```bash
dayu-cli prompt --base ~/.dayu/workspace --ticker <TICKER> "<question>"
```
