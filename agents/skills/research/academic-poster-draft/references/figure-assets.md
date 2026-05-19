# Figure Assets

Use this reference when the human needs clean scientific assets for a poster, such as a radar chart, compact result summary, rendered paper figure, figure crop, QR code, or case-study panel mockup.

## Asset Types

- Source figure render: convert an existing paper figure, table, or plot into a clean PNG/PDF for manual placement.
- Source figure crop: extract a meaningful region from a paper PDF or rendered figure.
- Recreated chart: rebuild a visual summary from trusted table data or source code.
- Style-matched helper visual: create a non-official design aid that fits the selected poster style.
- Case-study storyboard: organize user-provided evidence into panels without inventing missing trace details.

## Rules

- Prefer original paper assets, LaTeX tables, plot code, and user-provided files over screenshots.
- If a screenshot is the only source, say that the output may be soft and recreate from data when possible.
- Record exact data sources and transformations for recreated charts.
- Preserve source path, page or file, crop if any, DPI, and output path for rendered or cropped figures.
- Ask the user before making a crop when the intended region affects scientific meaning.
- Do not create fake benchmark values, unsupported method steps, official logos, or institutional marks.

## Naming

Use stable names under the project workspace:

```text
assets/figures/main-results-radar.png
assets/figures/teaser-clean.png
assets/figures/case-study-storyboard-draft.png
```

Avoid generic names such as `crop1.png` or `plot-new.png`.

## Provenance

Update `assets/provenance.json` or the project planning notes with:

- asset id
- output path
- source file or URL
- source type
- source page or table when relevant
- values or crop used
- transformation or normalization
- manual follow-up needed
