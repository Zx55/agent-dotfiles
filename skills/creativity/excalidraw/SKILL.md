---
name: excalidraw
description: Create hand-drawn style diagrams using Excalidraw JSON format. Generate editable .excalidraw files for architecture diagrams, flowcharts, sequence diagrams, concept maps, and planning visuals.
---

# Excalidraw Diagram Skill

Create diagrams by writing standard Excalidraw element JSON and saving as `.excalidraw` files. These files can be drag-and-dropped onto [excalidraw.com](https://excalidraw.com) for viewing and editing.

## Workflow

1. Write the elements JSON: an array of Excalidraw element objects
2. Save the file as `.excalidraw`
3. Optionally upload for a shareable link using `scripts/upload.py`

### Saving a Diagram

Wrap your elements array in the standard `.excalidraw` envelope:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "codex",
  "elements": [ ...your elements array here... ],
  "appState": {
    "viewBackgroundColor": "#ffffff"
  }
}
```

Save to any path, for example `~/diagrams/my_diagram.excalidraw`.

### Uploading for a Shareable Link

Run the upload script from this skill's `scripts/` directory:

```bash
python /Users/chenzeren/.codex/skills/creativity/excalidraw/scripts/upload.py ~/diagrams/my_diagram.excalidraw
```

This uploads to excalidraw.com and prints a shareable URL. It requires the `cryptography` package.

## Element Format Reference

### Required Fields

`type`, `id`, `x`, `y`, `width`, `height`

### Defaults

- `strokeColor`: `"#1e1e1e"`
- `backgroundColor`: `"transparent"`
- `fillStyle`: `"solid"`
- `strokeWidth`: `2`
- `roughness`: `1`
- `opacity`: `100`

Canvas background is white.

### Element Types

**Rectangle**

```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 100 }
```

**Ellipse**

```json
{ "type": "ellipse", "id": "e1", "x": 100, "y": 100, "width": 150, "height": 150 }
```

**Diamond**

```json
{ "type": "diamond", "id": "d1", "x": 100, "y": 100, "width": 150, "height": 150 }
```

**Labeled shape (container binding)**

Do not use `"label": { "text": "..." }` on shapes. Use a bound `text` element:

```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 80,
  "roundness": { "type": 3 }, "backgroundColor": "#a5d8ff", "fillStyle": "solid",
  "boundElements": [{ "id": "t_r1", "type": "text" }] },
{ "type": "text", "id": "t_r1", "x": 105, "y": 110, "width": 190, "height": 25,
  "text": "Hello", "fontSize": 20, "fontFamily": 1, "strokeColor": "#1e1e1e",
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "r1", "originalText": "Hello", "autoResize": true }
```

**Arrow**

```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0,
  "points": [[0,0],[200,0]], "endArrowhead": "arrow" }
```

### Arrow Bindings

```json
{
  "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
  "points": [[0,0],[150,0]], "endArrowhead": "arrow",
  "startBinding": { "elementId": "r1", "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "r2", "fixedPoint": [0, 0.5] }
}
```

`fixedPoint` coordinates: `top=[0.5,0]`, `bottom=[0.5,1]`, `left=[0,0.5]`, `right=[1,0.5]`

### Drawing Order

- Array order is z-order
- Emit progressively: background zones, shape, bound text, arrows, then the next shape
- Place the bound text element immediately after its container shape

### Sizing Guidelines

- Minimum `fontSize`: 16 for body text and labels
- Minimum `fontSize`: 20 for titles
- Minimum shape size: 120x60 for labeled rectangles and ellipses
- Leave 20-30px gaps between elements

### Color Palette

See `references/colors.md` for full tables. Quick reference:

| Use | Fill Color | Hex |
|-----|-----------|-----|
| Primary / Input | Light Blue | `#a5d8ff` |
| Success / Output | Light Green | `#b2f2bb` |
| Warning / External | Light Orange | `#ffd8a8` |
| Processing / Special | Light Purple | `#d0bfff` |
| Error / Critical | Light Red | `#ffc9c9` |
| Notes / Decisions | Light Yellow | `#fff3bf` |
| Storage / Data | Light Teal | `#c3fae8` |

### Tips

- Use the color palette consistently
- Text contrast matters; avoid light gray on white
- Do not use emoji in diagram text
- For dark mode diagrams, see `references/dark-mode.md`
- For larger examples, see `references/examples.md`
