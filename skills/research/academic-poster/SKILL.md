---
name: academic-poster
description: Build academic research posters from papers, templates, and source assets. Use for conference posters, poster planning, visual draft selection with imagegen, PDF figure/table cropping, PPTX-first poster generation, print-quality PDF/PNG export, and resumable poster workflows.
---

# Academic Poster

Use this skill to create or revise an academic poster as a PPTX-first artifact. The main output is an editable PowerPoint poster plus print-ready PDF and PNG exports.

## Defaults

- Default backend: PPTX generated from `poster-spec.json` with `pptxgenjs`.
- Default source of truth: `poster-spec.json`, not the generated PPTX.
- Default print target: 300 DPI unless the user or conference specifies dimensions or final pixels.
- Default final exports: `.pptx`, `.pdf`, and `.png`.
- Default visual workflow: the agent plans the story and figure candidates, then uses `$imagegen` to create 2-4 visual drafts for the user to choose from.
- Default paper asset path: crop regions from the source PDF. Save cropped PDF regions as master assets, render PNG derivatives for PPTX placement, and rerender at higher DPI if the placed image looks soft.

Do not use LaTeX as the poster backend. If a local formula, table, or algorithm block is easier to create with LaTeX, render that block as a PDF/PNG asset and place it into the PPTX workflow.

## Runtime Dependencies

Install only when the workflow reaches the relevant stage:

```bash
npm install pptxgenjs
python3 -m pip install pypdf PyMuPDF Pillow
```

PDF/PPTX export may also need a local renderer such as LibreOffice. If final export rendering is unavailable, still produce the PPTX and say exactly which renderer is missing.

## Workflow

1. Initialize a poster workspace with `scripts/init_workspace.py`. This creates `manifest.json`, `poster-spec.json`, and the expected folders.
2. Read the paper, optional existing poster, optional conference template, and optional logo or institutional assets.
3. Plan the poster story, section structure, candidate PDF regions, and likely orientation. Read `references/planning.md`.
4. Generate 2-4 visual drafts with `$imagegen` for style and layout selection. Draft images are not final scientific content.
5. After the user picks a direction, encode it in `poster-spec.json`.
6. Crop source paper figures, tables, and equations from PDF pages. Read `references/pdf-cropping.md`.
7. Build the editable PPTX with `scripts/build_poster_pptx.mjs`. Read `references/pptxgenjs-backend.md`.
8. Export PDF and PNG with `scripts/render_poster_outputs.py`. Read `references/print-export.md`.
9. Run QA with `scripts/qa_poster_outputs.py`.
10. Iterate by editing `poster-spec.json`, then rebuild and rerender.

For any long or interrupted job, read `references/workflow-recovery.md` and resume from `manifest.json`.

## Asset Rules

- User-provided conference templates and logos take priority.
- If online lookup is needed for a conference logo, university seal, or template, use official sources and record provenance.
- Do not generate official logos, seals, mascots, or conference marks with imagegen.
- Read `references/asset-provenance.md` before adding any brand or identity asset.

## Key Files

- `poster-spec.json`: canonical poster layout, assets, crop regions, and export paths.
- `manifest.json`: workflow state, inputs, completed stages, and resumability metadata.
- `regions/*.pdf`: cropped PDF master assets.
- `regions/*.png`: rendered derivatives used in PPTX.
- `exports/*.pptx`, `exports/*.pdf`, `exports/*.png`: final user-facing outputs.

## When To Ask The User

Ask for user input when:

- A conference template or size requirement is missing and cannot be inferred.
- A PDF crop region is ambiguous.
- The user must choose between visual drafts.
- A required official asset cannot be verified.

Prefer making a conservative first draft when the missing choice only affects style and can be changed later.
