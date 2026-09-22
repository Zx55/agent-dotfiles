---
name: html-slide-workflow
description: Develop presentation decks as fixed-size HTML slides with a shared theme, storyboard, and speaker notes. Use for an HTML-first slide workflow, iterative page layout, PDF review exports, or image-based PPTX delivery with notes. Not for editing native PowerPoint objects.
---

# HTML Slide Workflow

Make HTML the visual source of truth. PDF is the default review artifact. Export a static, image-based PPTX with speaker notes only when requested. Do not promise editable slide objects or animations.

## Route by the current task

- Plan a talk or revise its narrative → read [references/storyboard.md](references/storyboard.md).
- Design, implement, or adjust pages → read [references/slide.md](references/slide.md).
- Write, clean, or time narration → read [references/note.md](references/note.md).
- Initialize dependencies, render, export, or diagnose export failures → read [references/export.md](references/export.md).

Read only the references needed for the current request. For an existing deck, inspect its `AGENTS.md`, storyboard, shared styles, and relevant neighboring pages before changing it.

## Default workflow

1. Establish audience, duration, main message, source materials, and delivery language. Reuse choices already given by the user.
2. Discuss a storyboard before implementing a new deck. For each page, decide its purpose, evidence, composition, and approximate speaking time. Do not prescribe a fixed page count.
3. Initialize a new workspace with `scripts/init_workspace.py <workspace>`. It **copies** templates and export helpers. It never consumes skill resources or overwrites an existing workspace.
4. Agree on the theme and blank template, then discuss layouts and implement pages with their notes. Work page-by-page or in coherent batches. An explicit request to implement an already-discussed layout is sufficient approval.
5. Render changed pages to PDF and inspect the result. Before handoff, render the complete deck. Notes-only edits do not require rerendering the visuals.
6. If requested, export PPTX from current validated PDFs and the latest full note files. Do not hand-edit exported files to fix a source problem.

## Ownership

| File | Owns |
| --- | --- |
| `storyboard.md` | Narrative, page order, evidence mapping, timing |
| `slides/template.html` | Blank page structure and page-number element |
| `slides/theme.css` | Colors, typography, common visual tokens |
| `slides/slide.css` | Canvas, print layout, shared alignment anchors |
| `slides/slide-runtime.js` | Browser preview scaling |
| `slides/slideNN.html` | Individual page composition |
| `notes/slideNN.md` | Only the words to speak |
| `assets/slideNN/source.md` | Provenance, crop choices, factual caveats |
| `exports/` | Generated artifacts, not editable sources |

Use the templates as a coherent starting point, not a requirement to preserve their sample palette forever. Change deck-wide decisions centrally. Keep project-specific scientific terms, figures, numbers, and narrative out of the reusable skill.

## Completion

Verify the requested artifact, not merely that a command exited successfully. Check visual readability, cross-page continuity, page count/order, and note correspondence. Report any unperformed checks. If browser launch is blocked by the execution environment, provide the same command for the user's terminal rather than bypassing restrictions.
