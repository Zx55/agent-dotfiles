---
name: p5js
description: Production pipeline for interactive and generative visual art using p5.js. Use when the user wants browser-based sketches, generative art, interactive visualizations, motion graphics, or lightweight creative prototypes in HTML.
---

# p5.js Production Pipeline

## Creative Standard

This is visual art rendered in the browser. The canvas is the medium; the algorithm is the brush.

Before writing code, articulate the creative concept. The user's prompt is a starting point, not the final aesthetic.

First-render excellence matters. If the result looks like a p5.js tutorial exercise, rethink it before shipping.

Go beyond the reference vocabulary. The noise functions, particle systems, color palettes, and shader effects in the references are a starting vocabulary.

Be proactively creative. Add one meaningful visual detail the user did not ask for when it improves the piece.

Dense, layered, considered. Avoid flat white backgrounds, generic demo aesthetics, and unrelated effects.

## Modes

| Mode | Input | Output | Reference |
|------|-------|--------|-----------|
| Generative art | Seed / parameters | Procedural visual composition | `references/visual-effects.md` |
| Data visualization | Dataset / API | Interactive charts and custom displays | `references/interaction.md` |
| Interactive experience | None | Mouse, keyboard, or touch-driven sketch | `references/interaction.md` |
| Animation / motion graphics | Timeline / storyboard | Timed sequences and transitions | `references/animation.md` |
| 3D scene | Concept description | WebGL geometry and materials | `references/webgl-and-3d.md` |
| Image processing | Image file(s) | Pixel manipulation and filters | `references/visual-effects.md` |
| Audio-reactive | Audio file / mic | Sound-driven generative visuals | `references/interaction.md` |

## Stack

Single self-contained HTML file per project unless the existing repo structure suggests otherwise.

| Layer | Tool | Purpose |
|-------|------|---------|
| Core | p5.js 1.11.3 (CDN) | Canvas rendering, math, transforms, event handling |
| 3D | p5.js WebGL mode | 3D geometry, camera, lighting, GLSL shaders |
| Audio | p5.sound.js (CDN) | FFT analysis, amplitude, mic input |
| Export | `saveCanvas()` / `saveGif()` / `saveFrames()` | PNG, GIF, frame sequence output |
| Capture | CCapture.js (optional) | Deterministic video capture |
| Headless | Puppeteer + Node.js (optional) | Automated high-res rendering, MP4 via ffmpeg |
| SVG | p5.js-svg (optional) | Vector output |

### Version Note

Use p5.js 1.x by default unless the project truly requires 2.x features. See `references/core-api.md`.

## Pipeline

```text
CONCEPT -> DESIGN -> CODE -> PREVIEW -> EXPORT -> VERIFY
```

1. Concept: define mood, color world, motion vocabulary, and what makes the piece unique
2. Design: choose mode, canvas size, interaction model, color system, and export format
3. Code: write a self-contained HTML sketch with a clear structure
4. Preview: verify in a browser and refine until it feels intentional
5. Export: capture the right artifact for the task
6. Verify: check quality, resolution, and performance

## Creative Direction

### Aesthetic Dimensions

| Dimension | Options | Reference |
|-----------|---------|-----------|
| Color system | HSB/HSL, RGB, procedural harmony, gradients | `references/color-systems.md` |
| Noise vocabulary | Perlin, simplex, fractal, domain warp, curl noise | `references/visual-effects.md` |
| Particle systems | Physics, flocking, trails, attractors, flow fields | `references/visual-effects.md` |
| Shape language | Primitives, custom vertices, bezier curves, SVG paths | `references/shapes-and-geometry.md` |
| Motion style | Eased, spring-based, noise-driven, lerped, stepped | `references/animation.md` |
| Typography | Loaded fonts, `textToPoints()`, kinetic type | `references/typography.md` |
| Shader effects | GLSL, post-processing, feedback loops | `references/webgl-and-3d.md` |
| Interaction model | Mouse, keyboard, scroll, mic input | `references/interaction.md` |

### Per-Project Variation Rules

- Use a custom color palette
- Use a deliberate background treatment
- Vary motion speeds across primary, secondary, and ambient elements
- Add at least one invented element specific to the piece

## Workflow

### Step 1: Creative Vision

Before any code, articulate:

- mood and atmosphere
- visual story over time
- color world
- shape language
- motion vocabulary
- what makes this sketch different

### Step 2: Technical Design

- mode
- canvas size
- renderer: `P2D` or `WEBGL`
- frame rate
- export target
- interaction model
- viewer UI

For interactive generative art with seed exploration and parameter tuning, start from `templates/viewer.html`. For simple sketches or video export, use a smaller bare HTML file.

### Step 3: Code the Sketch

Single HTML file. Recommended structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Name</title>
  <script>p5.disableFriendlyErrors = true;</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
  <style>
    html, body { margin: 0; padding: 0; overflow: hidden; }
    canvas { display: block; }
  </style>
</head>
<body>
<script>
const CONFIG = { seed: 42 };
const PALETTE = { bg: '#0a0a0f', primary: '#e8d5b7' };
let particles = [];

function preload() {}

function setup() {
  createCanvas(1920, 1080);
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  colorMode(HSB, 360, 100, 100, 100);
}

function draw() {}
function mousePressed() {}
function keyPressed() {}
function windowResized() { resizeCanvas(windowWidth, windowHeight); }
</script>
</body>
</html>
```

Key implementation patterns:

- seeded randomness via `randomSeed()` and `noiseSeed()`
- HSB color mode for intuitive control
- separate config, palette, and mutable state
- classes for particles or agents when helpful
- offscreen buffers via `createGraphics()` for layered composition

### Step 4: Preview and Iterate

- Open the HTML file in a browser
- For `loadImage()` or `loadFont()` with local assets, use `scripts/serve.sh` or `python3 -m http.server`
- Test at target resolution, not just the default browser window
- Adjust until the output matches the concept from Step 1

### Step 5: Export

| Format | Method | Command |
|--------|--------|---------|
| PNG | `saveCanvas('output', 'png')` | Press a key or call directly |
| High-res PNG | Puppeteer headless capture | `node scripts/export-frames.js sketch.html --width 3840 --height 2160 --frames 1` |
| GIF | `saveGif('output', 5)` | Press a key or call directly |
| Frame sequence | `saveFrames()` | Then stitch with ffmpeg |
| MP4 | Puppeteer frame capture + ffmpeg | `bash scripts/render.sh sketch.html output.mp4 --duration 30 --fps 30` |
| SVG | `createCanvas(w, h, SVG)` | `save('output.svg')` |

### Step 6: Quality Verification

- Does it match the vision?
- Is it sharp at the target display size?
- Does it hold frame rate?
- Do the colors work together?
- What happens on resize and at the edges?

## Critical Implementation Notes

### Performance

Disable Friendly Error System before setup:

```javascript
p5.disableFriendlyErrors = true;
```

Use `Math.*` in hot loops when seed fidelity is not required.

### Seeded Randomness

Every generative sketch should be reproducible:

```javascript
function setup() {
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
}
```

### Color Mode

Prefer HSB for generative art:

```javascript
colorMode(HSB, 360, 100, 100, 100);
```

### createGraphics() for Layers

Use offscreen buffers for layered composition when the work benefits from trails, masks, or separated passes.

### Key Bindings Convention

```javascript
function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('output', 'png');
  if (key === 'g' || key === 'G') saveGif('output', 5);
  if (key === ' ') CONFIG.paused = !CONFIG.paused;
}
```

### Headless Video Export

For Puppeteer-based capture, the sketch should use `noLoop()` in setup and set `window._p5Ready = true`. The bundled `scripts/export-frames.js` uses that for deterministic frame capture.

## Agent Workflow

When building p5.js sketches:

1. Create the HTML file
2. Open it in a browser and verify visual quality
3. Use a local server when the sketch depends on local fonts or images
4. Add export controls if the user wants artifacts
5. Use `node scripts/export-frames.js` for headless frame export
6. Use `bash scripts/render.sh` for MP4 rendering
7. Refine iteratively after each preview
8. Load only the reference files relevant to the current sketch

## Performance Targets

| Metric | Target |
|--------|--------|
| Frame rate (interactive) | 60fps sustained |
| Frame rate (animated export) | 30fps minimum |
| Canvas resolution | Up to 3840x2160 export, 1920x1080 interactive |
| Load time | Under 2s to first frame |

## References

| File | Contents |
|------|----------|
| `references/core-api.md` | Canvas setup, coordinate system, draw loop, offscreen buffers |
| `references/shapes-and-geometry.md` | Primitives, curves, custom shapes, vectors |
| `references/visual-effects.md` | Noise, flow fields, particles, texture generation |
| `references/animation.md` | Timing, easing, sequencing, transitions |
| `references/typography.md` | Text rendering, loaded fonts, kinetic typography |
| `references/color-systems.md` | Color modes, palettes, blend modes, gradients |
| `references/webgl-and-3d.md` | WEBGL, 3D primitives, shaders, post-processing |
| `references/interaction.md` | Mouse, keyboard, touch, DOM controls, audio input |
| `references/export-pipeline.md` | PNG, GIF, frame capture, ffmpeg workflows |
| `references/troubleshooting.md` | Performance profiling, browser issues, memory traps |
| `templates/viewer.html` | Interactive viewer template with seed navigation and parameter controls |
