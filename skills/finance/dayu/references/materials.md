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
- `--company-id`
- `--infer`
- `--overwrite`
- `--amended`

If the workspace does not already know the company, `create` may require `--company-id`.

## Minimum metadata to collect from the user

When the user uploads a filing, try to confirm:

- ticker
- fiscal year
- fiscal period
- file path

If the workspace does not already know the company, you may also need:

- company id
- company name
- or `--infer` if the ticker is good enough for FMP-based enrichment

## PDF conversion fallback

Use this when the source file is an official Hong Kong or A-share PDF, but `upload_filing` fails on PDF conversion or clearly gets stuck in the same conversion step for that PDF.

Do not keep retrying the same PDF upload path once there is real conversion failure evidence such as `Docling 转换失败`.

Preferred fallback:

1. keep the official PDF as the source of record
2. extract the PDF text to a Markdown file locally
3. preserve page boundaries with headings such as `## Page 1`
4. add a short metadata header with:
   - company name
   - ticker
   - filing date
   - report date
   - fiscal year / period
   - original source URL when known
5. retry `upload_filing` using the `.md` file instead of the original PDF

Practical note:

- for Hong Kong and mainland filings, Markdown upload can be more reliable than direct PDF ingestion when the PDF conversion chain is unstable
- this fallback is still preferred over host-side analysis outside Dayu

Example shape:

```bash
dayu-cli upload_filing \
  --base ~/.dayu/workspace \
  --ticker 1810.HK \
  --files /tmp/xiaomi-2025-fy-results-announcement.md \
  --fiscal-year 2025 \
  --fiscal-period FY \
  --filing-date 2026-03-24 \
  --report-date 2025-12-31 \
  --company-id 1810.HK \
  --company-name "Xiaomi Corporation" \
  --overwrite
```

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
