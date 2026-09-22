# Per-page layout plans

Save a page's layout in `layouts/slideNN.md`, starting from `layouts/template.md`. The initializer copies this blank planning template, but does not invent per-page plans. The Markdown layout is a design and decision record, not the rendered slide and not the spoken script.

## Workflow and ownership

After the storyboard establishes the narrative, propose a composition for the requested page or coherent batch. Write the proposal into the corresponding layout files and show the user the essential arrangement and open decisions. If implementation is already authorized, do not introduce another approval gate. Mark a layout as approved only when the user has approved it or delegated the design decision.

Implement the approved plan in `slides/slideNN.html`, using the blank HTML template and shared theme. Write full narration only in `notes/slideNN.md`. When the user requests a visual adjustment, update the HTML and the affected layout decisions together. Record the current arrangement rather than accumulating contradictory old proposals. Notes-only edits do not require layout changes.

`storyboard.md` owns narrative and order. `layouts/slideNN.md` owns the page's intended composition, asset treatment, and cross-page continuity decisions. HTML remains the visual source of truth for rendering. If the plan and HTML disagree, inspect both and reconcile the difference rather than assuming either is an approved redesign.

## What to capture

- The page's one main point and its different role from adjacent pages.
- Proposed visible title, subtitle, key labels, and takeaway. Specify theme emphasis without hardcoding a new palette.
- A small wireframe or a clear spatial description, followed by useful region dimensions. Read shared anchors from the workspace styles rather than duplicating their current numeric values into every plan.
- The dominant visual, text hierarchy, column balance, and connector meaning. Distinguish moving a content group from scaling its images.
- For precise diagrams, arrow origins/destinations, reference conventions, and whether coordinates are global canvas positions or local SVG positions.
- Asset paths, whether a source figure or SVG is appropriate, and crop/display geometry. For paired images, specify equal display windows and retained context. Detailed provenance stays in `assets/slideNN/source.md`.
- Elements that remain fixed on the previous/next page, and elements that change during a progressive reveal.
- Pending decisions and actual review status. Do not label an unrendered page visually verified.

Use only sections that materially help implementation. A simple title slide does not need an elaborate grid specification. Do not paste an entire speaker script or research dossier into the layout.

## Consecutive pages and revisions

Related pages may be discussed together, but each keeps its own `layouts/slideNN.md`. Cross-link companion plans instead of maintaining a second combined plan that can go stale. Keep shared illustrations, titles, subtitles, lower takeaway lines, and page numbers aligned when continuity is intended. If a section title moves, consider its diagram/formula group as well.

When merging or renumbering pages, update the layouts alongside HTML, notes, storyboard links, and relevant asset paths. A layout-only change does not alter exported visuals until the corresponding HTML is implemented. PDF freshness checks therefore do not hash layout Markdown.
