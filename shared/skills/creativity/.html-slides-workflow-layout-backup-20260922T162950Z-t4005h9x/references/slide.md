# HTML composition and visual review

Create each `slides/slideNN.html` from `slides/template.html`. The template is a genuinely blank 16:9 canvas with only its common page-number element. Do not turn a completed cover or content page into the universal template.

The default canvas is 1600 × 900 CSS pixels. `slide.css` owns its size. Preview JavaScript and the PDF exporter read the computed CSS dimensions. Print page size is injected from the same dimensions, so there is no separate hardcoded export size to maintain.

## Shared design

- Choose a palette once. Use `theme.css` variables for HTML and inline SVG colors, text families, sizes, and weights. Add semantic tokens when needed rather than copying raw color values into individual pages.
- Use shared `.slide-title`, `.slide-subtitle`, `.slide-takeaway`, and `.slide-number` anchors. Their position and weight should not drift across pages. Keep secondary headings aligned on neighboring pages with similar compositions.
- If a shared heading moves, rebalance its whole content group, including diagrams and equations. Moving only the title can leave the page visually off-center.
- Keep the main content readable at presentation distance. Enlarge cramped tool labels and diagram captions by revising the layout, not merely enlarging every image.
- Preserve meaningful whitespace. If one side is crowded and another empty, adjust column widths and connector space before adding content or scaling pictures.
- Keep a title's selective accent styling consistent across the deck. Avoid accidental forced line breaks, unexplained underlines, or symbols such as `<<` to mean a conceptual gap.

## Choosing and preparing visuals

Prefer the original source figure or images extracted from a supplied PDF/PPTX when they contain evidence. Inspect the selected crop visually. When comparing two images, use equal display windows and aspect ratios without stretching. Crop expendable margins while retaining the objects, labels, context, and axes essential to the claim.

Use inline SVG for precise geometry, arrows, labels, model/tool icons, and quantitative charts. A diagram must be semantically right, not merely attractive. Check origins, arrow direction, viewpoint, rotation, coordinate conventions, and whether an object labeled “back-left” is actually drawn there. Use generation tools only when an illustrative scene or visual exploration benefits from them. Do not replace evidence or exact mathematical diagrams with plausible generated imagery.

Record original sources, figure/page numbers, asset licenses where available, crop decisions, and “generated illustration” status in `assets/slideNN/source.md`. Preserve any necessary visible attribution. Full research bookkeeping does not belong in the spoken notes.

For plots, retain units, baseline identities, absolute-versus-relative changes, and error bars when applicable. Axis normalization must be disclosed, especially if radar-chart axes use different maxima. A model-generated tool sequence must not be illustrated as a fixed, hand-written pipeline if the method's point is dynamic orchestration.

## Render and review

Use relative, local asset paths. Download essential assets only when authorized and needed, and keep the exported presentation self-contained. Avoid external font/CDN dependencies. The PDF renderer is offline and rejects files outside the workspace.

Render the page, then inspect it visually. Check overlap, clipping, legibility, crop context, mathematical meaning, and balance. Compare neighboring slides for title, subtitle, page-number, takeaway, and repeated-diagram alignment. The exporter checks canvas and media readiness but cannot prove semantic correctness or all forms of overlap.

If the PDF renderer reports a slide number mismatch or missing resource, fix HTML/assets first. Do not repair the generated PDF as a parallel source of truth.
