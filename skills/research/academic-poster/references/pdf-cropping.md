# PDF Cropping

Paper figures, tables, formulas, and result panels should usually come from the source PDF.

## Default Asset Policy

For each selected region:

1. Crop the source PDF page to a new PDF master.
2. Render the cropped PDF master to a PNG derivative at the target DPI.
3. Place the PNG derivative into PPTX.
4. Preserve the PDF master and provenance in `poster-spec.json`.

Do not make direct PDF embedding into PPTX the default. It is not reliable across PowerPoint export, platform rendering, and print workflows.

If the PNG looks soft after placement, rerender from the PDF master at a higher DPI, then rebuild the PPTX.

## Coordinate System

Store bounding boxes as PDF points:

```json
"bbox": [72, 120, 520, 390]
```

The order is `[left, top, right, bottom]` in page coordinates after normalization by the crop script. The script records the source page size so the region can be audited later.

## User Confirmation

If the region is ambiguous, render a page preview and ask the user to confirm the intended region before final cropping.

## Naming

Use stable ids:

```text
regions/method-diagram.pdf
regions/method-diagram-300dpi.png
```

Avoid generic names such as `crop1.pdf`.

## Region Record

Each region in `poster-spec.json` should include:

```json
{
  "id": "method-diagram",
  "source_pdf": "paper.pdf",
  "page": 4,
  "bbox": [72, 120, 520, 390],
  "master_pdf": "regions/method-diagram.pdf",
  "rendered_png": "regions/method-diagram-300dpi.png",
  "dpi": 300,
  "notes": "Main method diagram for the center column"
}
```
