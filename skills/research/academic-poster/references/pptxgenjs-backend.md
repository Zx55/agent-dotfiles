# PPTXGenJS Backend

The poster backend uses `pptxgenjs` to generate one editable PPTX slide from `poster-spec.json`.

## Source Of Truth

Edit `poster-spec.json`, not the generated PPTX. Rebuild after each change.

Coordinates use inches. This keeps PPTX geometry, physical poster size, and DPI math aligned.

## Canvas

`poster-spec.json` must include:

```json
{
  "canvas": {
    "width_in": 52,
    "height_in": 39,
    "dpi": 300,
    "orientation": "landscape"
  }
}
```

The builder defines a custom PowerPoint layout with the same width and height.

## Supported Elements

The first implementation supports:

- `text`: text box with font, size, color, bold, alignment, bullets
- `rect`: filled or stroked rectangle
- `line`: simple line segment
- `image`: PNG/JPEG/SVG image placement
- `section_bar`: convenience rectangle plus text

Prefer PDF-cropped PNGs for paper figures and tables. Keep the cropped PDF master in `regions/`.

## Element Fields

Common fields:

```json
{
  "id": "method-figure",
  "type": "image",
  "x": 17.0,
  "y": 4.2,
  "w": 18.0,
  "h": 10.0
}
```

Text fields:

```json
{
  "type": "text",
  "text": "Introduction & Motivation",
  "fontFace": "Aptos",
  "fontSize": 28,
  "color": "FFFFFF",
  "bold": true,
  "align": "left",
  "valign": "mid"
}
```

Image fields:

```json
{
  "type": "image",
  "path": "regions/method-diagram-300dpi.png",
  "sizing": "contain"
}
```

Use `contain` by default for scientific figures. Use `crop` only when the crop is intentional and verified in the rendered preview.

## OOXML Fallback

Use `scripts/patch_pptx_ooxml.mjs` only when `pptxgenjs` cannot express a required PowerPoint property. Record the fallback in `manifest.json`.

Do not use OOXML fallback for routine geometry, colors, text, or image placement.

## Build Checks

After building:

- confirm the PPTX exists and is non-empty
- confirm it has one slide unless the user requested variants
- confirm all image paths resolved
- render PDF/PNG before considering the build valid
