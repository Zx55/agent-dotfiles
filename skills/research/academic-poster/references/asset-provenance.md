# Asset Provenance

Use this reference before adding logos, conference marks, school seals, sponsor marks, QR codes, or templates.

## Priority

1. User-provided official template or asset
2. Official conference, university, lab, or publisher source
3. Omit the asset and rely on text or neutral layout

Do not generate official identity assets with imagegen.

## Provenance Record

Record identity assets in `assets/provenance.json`:

```json
{
  "id": "iclr-logo",
  "path": "assets/iclr-logo.png",
  "source": "https://...",
  "source_type": "official conference website",
  "retrieved_at": "2026-05-16",
  "notes": "Used in poster header"
}
```

For user-provided files, use `source_type: "user-provided"`.

## Templates

If the user provides a conference PPTX template, inherit it by default. If no template is provided, use the skill's neutral templates.

When an official template is downloaded online, save it in the workspace and record provenance.

## QR Codes

QR codes can be generated locally for project pages, PDFs, GitHub repositories, or contact pages. Record the target URL in `poster-spec.json`.
