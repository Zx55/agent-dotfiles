# Visual Assets

Use visual assets in deep-reading reports only when they clarify the paper's method, pipeline, taxonomy, benchmark setup, or key result. Do not add decorative images.

## Default Policy

Every core-paper deep read must include a `Visual Anchor` decision.

Prefer visual sources in this order:

1. Original paper figure or cropped region from the PDF.
2. Inline agent-created deterministic schematic, usually Mermaid, when the paper has no useful figure or the original figure is too dense to clarify the comparison.
3. Generated or hand-authored image asset, such as SVG or `$imagegen`, only when an actual image file would add value and the content can be verified against the paper.

When the asset is not copied from the paper, label it clearly as `agent-created schematic` or `generated illustration, not from the paper`.

For architecture, system, tokenizer, training-pipeline, benchmark, and empirical model papers, the default is to include one useful anchor. Use `none` only when:

- the paper has no informative figure or table
- rendering/cropping remains unavailable after the setup check below, or a crop would not clarify the claim
- an agent-created schematic would duplicate the text without clarifying the comparison

When using `none`, explain the reason concretely in the deep-reading report.

## Setup Check

Before assigning deep-reading tasks that may need PDF crops, the main agent should check whether at least one rendering path works:

```bash
python - <<'PY'
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("fitz") else 1)
PY
```

If PyMuPDF is missing and package installation is acceptable in the current environment, install it before deep reading:

```bash
python -m pip install pymupdf
```

If installation is blocked, use Poppler (`pdftoppm`) or manual screenshot. Record a concrete reason only if every reasonable rendering path is unavailable or the paper figure would not help.

## Asset Location And Path Style

Store survey-local assets under:

```text
<survey workspace>/assets/
```

Use `assets/` only for image or media assets that need to be embedded from the report, such as PDF crops, screenshots, generated PNGs, or hand-authored SVGs. Do not store Mermaid or Markdown schematics as separate `.md` assets by default; put them inline in the deep-reading report.

Recommended names:

- `<paper_slug>_pipeline.png`
- `<paper_slug>_architecture.png`
- `<paper_slug>_benchmark_table.png`
- `<paper_slug>_schematic.svg`

Reference assets from a deep-reading report with paths relative to that report, for example:

```md
![Mobile-O pipeline](../assets/mobile_o_pipeline.png)
```

All Markdown links and local file references inside survey artifacts should be relative to the artifact that contains them. Avoid absolute workspace paths in reports because the entire survey directory may be moved.

## What To Capture

Good visual anchors:

- architecture or pipeline figure
- training objective diagram
- tokenizer / representation diagram
- benchmark setup figure
- headline result table when it directly supports a key strength or limitation

Avoid capturing:

- decorative teaser images
- large tables that are not used in the report
- figures that cannot be connected to a specific claim

## Simple PDF Screenshot Methods

Use whichever method is available and fastest in the current environment.

### Manual Screenshot

1. Open the local PDF.
2. Navigate to the target page and zoom so the figure is readable.
3. Screenshot the figure region.
4. Save it under `<survey workspace>/assets/<paper_slug>_<figure_slug>.png`.
5. Record the source location in the deep-reading report, such as `PDF p.4, Fig. 2`.

### Command-Line Full Page Render

If Poppler is installed, render a page to PNG:

```bash
pdftoppm -f <page> -singlefile -png -r 180 <paper.pdf> <survey workspace>/assets/<paper_slug>_page_<page>
```

Then crop manually if needed.

### PyMuPDF Crop

If PyMuPDF is available, render a page crop by normalized coordinates. Coordinates are fractions of page width and height: `x y width height`.

```bash
python <skill-dir>/scripts/render_pdf_asset.py \
  --pdf <paper.pdf> \
  --page <page> \
  --crop 0.10 0.18 0.80 0.42 \
  --out <survey workspace>/assets/<paper_slug>_pipeline.png
```

Use a full-page render first when crop coordinates are unknown:

```bash
python <skill-dir>/scripts/render_pdf_asset.py \
  --pdf <paper.pdf> \
  --page <page> \
  --out <survey workspace>/assets/<paper_slug>_page_<page>.png
```

## Deep-Reading Report Requirements

In `Visual Anchor`, record:

- embedded image link, inline Mermaid/Markdown schematic, or `none`
- source location, such as `PDF p.4, Fig. 2`
- asset type: original paper figure, original paper crop, agent-created schematic, generated illustration, or none
- why the visual matters for this survey
- if no visual is used, the concrete reason it was not useful or not feasible

If the visual anchor is an agent-created Mermaid or Markdown schematic, place the schematic directly in the `Visual Anchor` section. Do not point to a separate `.md` file under `assets/`.

When a strength or limitation relies on a figure or table, cite that same figure or table in the relevant evidence location.
