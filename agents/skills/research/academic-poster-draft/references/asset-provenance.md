# Asset Provenance

Use this reference before adding logos, conference marks, school seals, sponsor marks, QR codes, templates, recreated charts, or generated helper visuals.

## Identity Asset Priority

1. User-provided official template or asset
2. Official conference, university, lab, or publisher source
3. Omit the asset and rely on text or a neutral placeholder

Do not generate official identity assets with imagegen.

## Provenance Record

Record assets in `assets/provenance.json`:

```json
{
  "id": "main-results-radar",
  "path": "assets/figures/main-results-radar.png",
  "source": "tables/tab1_main_results.tex",
  "source_type": "recreated chart from paper table",
  "created_at": "2026-05-17",
  "notes": "Radar axes use per-benchmark maxima as the outer limit."
}
```

For user-provided files, use `source_type: "user-provided"`.

## Recreated Scientific Assets

For charts, tables, diagrams, or case-study panels recreated from source material, record:

- source file or page
- values or crop used
- transformation or normalization
- output path
- uncertainty or manual edits still needed

Never invent missing numbers or unsupported claims.
