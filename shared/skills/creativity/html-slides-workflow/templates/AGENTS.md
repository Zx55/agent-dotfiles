# HTML presentation workspace

## Sources of truth

- `storyboard.md` owns narrative, ordering, evidence mapping, and timing.
- `slides/template.html` is the blank starting structure for each page.
- `slides/theme.css` owns colors, typography, and common visual tokens.
- `slides/slide.css` owns canvas size, safe area, shared anchors, and print layout.
- `slides/slide-runtime.js` owns preview scaling and reads the CSS canvas size.
- `slides/slideNN.html` owns page-specific markup and layout.
- `notes/slideNN.md` contains only spoken text. Its full contents become speaker notes.
- `assets/slideNN/source.md` records sources, crop decisions, and factual caveats.
- `exports/` contains generated presentation copies. Fix their sources, not the copies.

## Creation and consistency

Start pages from the template, retain its common stylesheet/runtime links and page-number element, and use consecutive `slide01.html`, `slide02.html`, etc. Keep each visible page number in sync. Do not create unrequested empty pages.

Use theme variables for colors, fonts, type sizes, and weights in HTML and SVG. Do not restyle page numbers locally. Use shared title, subtitle, and takeaway anchors. Page-specific CSS belongs in that page until it is genuinely shared. Keep repeated diagrams and analogous headings aligned across transitions.

Preserve the 16:9 canvas. It is defined once in `slide.css`, not separately in preview or export code. All content fits within that canvas. Avoid shrinking text to solve crowding, stretching images, or hiding overflow as a layout fix. Crop paired evidence images into equal windows without removing essential context.

Keep local media under `assets/` and use relative paths. Do not depend on remote fonts, scripts, or images at export time. Use SVG for exact diagrams and charts, original source media for evidence, and generated imagery only for clearly identified illustration.

## Review and delivery

Discuss storyboard and layout when not already agreed. Implement approved layouts without repeatedly requesting approval. Update the storyboard when the narrative changes. Read adjacent notes to avoid redundant transitions. Keep notes free of titles, citations, timestamps, and layout commentary.

Render and visually inspect changed pages. Render the complete deck before final delivery. Validate page count, order, aspect ratio, assets, cross-page alignment, claims, equations, and chart units. Notes-only changes do not require PDF rerendering.

PDF is the default review format. Export static PPTX only when requested, using the current PDF manifest and latest full note files. Never bypass stale-PDF checks. Report environment limitations and unperformed checks honestly.
