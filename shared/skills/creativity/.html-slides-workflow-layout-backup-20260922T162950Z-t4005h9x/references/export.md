# Workspace initialization and exports

## Initialize

Run the skill's `scripts/init_workspace.py /absolute/path/to/workspace` with Python 3. It accepts a new or empty directory and refuses a nonempty one before copying anything. It copies `templates/` and the reusable exporters, leaving skill resources intact. Do not initialize on top of an existing deck to migrate it.

The resulting workspace has this structure:

```text
workspace/
  AGENTS.md
  storyboard.md
  package.json
  assets/common/
  slides/template.html
  slides/theme.css
  slides/slide.css
  slides/slide-runtime.js
  notes/
  scripts/export-pdf.mjs
  scripts/export-pptx.mjs
  scripts/lib/common.mjs
  scripts/verify_pptx.py
  exports/
```

Create `slides/slideNN.html`, `notes/slideNN.md`, and `assets/slideNN/` as content is approved. No fixed page count or empty content slides are created by initialization. Number slides continuously from 1. Use at least two digits, including three digits for decks over 99 pages. The exporter sorts by numeric ID and rejects duplicates or gaps.

## Runtime setup

The scripts are ES modules for Node.js 20+ and use Playwright, pdf-lib, and (only for PPTX) `@oai/artifact-tool`. Python 3.9+ standard library validates PPTX XML, images, relationships, and notes. Poppler's `pdftoppm` renders the PDF pages to PNG.

Prefer available workspace dependencies. In Codex, call `load_workspace_dependencies` and use its returned Node executable and `RUNTIME_NODE_MODULES` path. Do not hardcode a username, cache directory, or plugin version into generated scripts. Both exporters resolve workspace packages first, then `RUNTIME_NODE_MODULES` and `NODE_PATH`. No external presentation-skill directory or child-process finalizer is required. The PPTX is validated locally and reimported with Artifact Tool in the same process.

Outside a bundled runtime, install the declared workspace dependencies with the user's normal Node package manager. The optional Artifact Tool dependency must be available for PPTX, but is not required for PDF export. If it is unavailable from the configured registry, point `RUNTIME_NODE_MODULES` at an available runtime instead of silently changing the presentation engine. Do not install dependencies merely to discuss a layout.

For PDF rendering, use installed Chrome on macOS, Playwright Chromium, or `--browser /path/to/chrome`. For PPTX, `pdftoppm` must be on PATH or provided with `--pdftoppm`. Select Python with `--python`, `RUNTIME_PYTHON`, the workspace `.venv`, or the `python3` fallback. Respect the user's environment and installation permissions.

## Commands inside the initialized workspace

```bash
node scripts/export-pdf.mjs --check
node scripts/export-pdf.mjs --slides 2,4-6
node scripts/export-pdf.mjs
node scripts/export-pptx.mjs --check
node scripts/export-pptx.mjs
```

Scripts also work from another cwd when invoked by their absolute path. `--workspace DIR` supports an explicit workspace. `--out DIR` on the PDF exporter changes its export directory. Pass that same directory to PPTX via `--pdf-dir DIR` (the directory containing `manifest.json`, not its `pdf/` child). `--out FILE.pptx` changes the PPTX destination.

PDF outputs are `exports/pdf/slideNN.pdf`, `exports/presentation.pdf`, and `exports/manifest.json`. `--slides` writes a separate preview under `exports/preview/` without changing the full export. Preview manifests are deliberately not accepted as complete PPTX input. Rerender the full deck before final PPTX delivery.

PDF reruns replace their generated outputs after all pages validate. PPTX refuses to replace an existing file unless `--overwrite` is explicit. Use a new `--out` name to retain reviewed revisions. Exporters never delete unrelated old outputs, so a removed page's old PDF may still exist on disk, but the current manifest is authoritative and excludes it.

## What is checked

- Continuous page IDs and matching visible page numbers.
- One 16:9 HTML canvas per page, matching dimensions across the deck.
- Offline HTML/SVG image decoding, font readiness, failed resource loads and browser errors.
- One PDF page per HTML, expected dimensions and rotation, complete merged page count.
- A conservative hash snapshot of all non-Markdown files under `slides/` and `assets/`. Symlinks and visual resources outside those directories are rejected. The snapshot includes the blank template, even if its latest edit does not change existing pages.
- PDF hashes and input freshness before PPTX. Changes only to `notes/`, `storyboard.md`, or provenance Markdown do not invalidate PDF visuals. Any visual change requires a new full export.
- Exactly one full-slide image per PPTX page, expected canvas dimensions, ZIP/XML relationships, image bytes/order, and full note text, followed by Artifact Tool reimport.

Notes are not parsed as Markdown, abbreviated, or stripped of headings. Clean them before export if they contain non-spoken content. Only CRLF/CR line endings are normalized to LF. Missing/empty notes warn and produce blank notes, or fail under `--strict-notes`. Unsupported XML control characters fail instead of being silently removed.

PDF-to-PPTX is intentionally image-based. Each page becomes a 3200 × 1800 PNG, avoiding font substitutions and independent SVG/XML layout reconstruction inside PowerPoint. It sacrifices selectable/editable foreground content for visual fidelity. Speaker notes remain native text.

## Verification and failure handling

`--check` is preflight, not proof of browser rendering or visual quality. Inspect rendered pages at a presentation-like size, particularly dense figures and small labels. When available, render/open the final PPTX to inspect its appearance and notes in a presentation application as an additional check.

If browser launch is blocked, stop the rendering attempt and give the user the same export command to run in their terminal. Do not switch to UI automation or external screenshot services as an unrequested bypass. A launch failure does not justify modifying HTML.

Temporary staging directories are created with unique names and only those directories are cleaned. Existing final artifacts are not replaced on render/validation failure. Multi-file PDF publication commits the manifest last, and subsequent hash checks reject inconsistent artifacts if publication was interrupted. Back up exports separately when archival history is needed.

The fingerprint does not capture system font installation changes or renderer upgrades. Rerender after changing runtimes/fonts. Hash checks cannot replace visual review or source verification of scientific claims.

## Maintaining the skill

The reusable tests stay in the skill rather than being copied into every deck. With dependencies available through `RUNTIME_NODE_MODULES` and an appropriate Python selected through `RUNTIME_PYTHON`, run from the skill directory:

```bash
node --test scripts/tests/workflow.test.mjs
RUN_PPTX_TESTS=1 node --test scripts/tests/workflow.test.mjs
RUN_BROWSER_TESTS=1 node --test scripts/tests/workflow.test.mjs
```

The ordinary tests cover initialization, overwrite refusal, numeric ordering, and freshness. The optional PPTX test uses explicitly synthetic PDFs to isolate packaging and full-note verification from browser availability. It is not an HTML-rendering test. The browser test renders a real two-page HTML deck and a single-page preview. Tests use temporary workspaces and remove only their own generated fixtures.
