---
name: academic-poster-draft
description: Create academic research poster concepts and human-editable poster guidance from papers, templates, screenshots, and source assets. Use for conference poster planning, imagegen-based layout and style drafts, visual narrative selection, figure recommendations, scientific helper assets such as radar charts or rendered paper figures, section copy polishing, case-study storyboarding, and QA feedback on human-made poster screenshots. This skill stops at draft direction and human-assist assets rather than owning an automated final deck build.
---

# Academic Poster Draft

Use this skill to design an academic research poster before and during human assembly. The main outputs are a selected visual direction, a compact style/layout contract, and practical assets or text blocks the human can place in PowerPoint, Keynote, Figma, Illustrator, or another poster editor.

This skill is not a deck-generation backend. It should not treat a generated slide file or machine-readable layout spec as the default source of truth. If a future project needs full poster automation, use or create a separate implementation-focused skill.

## Defaults

- Default goal: concept design plus human production support.
- Default visual workflow: plan the poster story, then use `$imagegen` to generate 2-4 layout/style draft images for user selection.
- If the user has already selected a visual direction or provides current poster screenshots, skip the concept-draft loop and enter human-assist mode directly.
- Default draft fidelity: visually faithful layout concepts with placeholder scientific figures when exact assets are not ready.
- Default source handling: read the paper, supplement, LaTeX, tables, original figures, existing slides, screenshots, templates, and user-provided assets before drafting.
- Default durable outputs: planning notes, draft prompts, selected draft image, style/layout contract, asset provenance, helper charts/figures, and polished section copy.
- Default final editor: the human edits the real poster in PowerPoint, Keynote, Figma, Illustrator, or another chosen design tool.

Do not generate official logos, university seals, conference marks, or fake scientific data. Use user-provided identity assets or leave explicit placeholders.

## Workflow

1. Identify the intended poster artifact, target size, conference constraints, available source files, and the editor the human is likely to use.
2. Read the paper and source materials enough to separate evidence, interpretation, and poster recommendations. Prefer primary sources such as the paper PDF, LaTeX, tables, and original figure files.
3. Create lightweight planning artifacts in the poster workspace when the decisions have durable value:
   - `planning/story-plan.md` for narrative, section roles, and talking points.
   - `planning/figure-candidates.json` for figures, tables, provenance, and recommended use.
   - `planning/draft-prompts.md` for imagegen prompt history and selected direction.
   - `planning/style-layout-contract.md` for the selected human-editable design contract.
   - `assets/provenance.json` for user-provided, recreated, rendered, cropped, or generated assets.
4. Generate 2-4 concept drafts with `$imagegen`. Drafts should explore layout, hierarchy, style, section rhythm, and placeholder figure placement. They are not the final scientific poster.
5. Stop for user selection after visual drafts. The user may choose one draft, merge parts of drafts, or request another round.
6. Convert the selected direction into a short style/layout contract that a human can implement:
   - canvas and grid
   - section order and relative emphasis
   - title/header treatment
   - colors, typography, line style, and panel style
   - figure slots and intended evidence
   - known placeholders and unfinished areas
7. After selection, assist the human rather than trying to own the full poster build:
   - recreate needed charts from trusted data, such as radar plots or compact result summaries
   - render or crop source figures when exact assets are useful
   - polish section titles, captions, bullets, and talk-track text
   - storyboard case-study panels in the chosen style
   - critique screenshots from the human-made poster and suggest precise layout fixes
   - prepare small replacement assets that fit the selected style
8. Preserve decisions and generated helper assets in the workspace so later manual editing is auditable.

## Manual Assembly Support Patterns

After a visual direction is selected, keep support concrete and local to the section the human is editing. Do not restart concept generation or switch to full-slide automation unless the user explicitly asks for that workflow.

Useful human-assist artifacts include:

- low-fidelity layout mockups for one section or one sub-region
- compact chart reconstructions from trusted tables or plotted source data
- cropped, re-rendered, or simplified source figures for direct placement in the editor
- section-level copy blocks matched to the poster's chosen writing style
- screenshot critiques focused on hierarchy, density, alignment, spacing, cropping, contrast, and readability

For manual layout decisions, lightweight Python/PIL or matplotlib mockups are encouraged. Keep them low-fidelity and section-scoped. They should communicate spatial structure, relative scale, and information grouping rather than final graphic polish. Treat these mockups as disposable editing aids, not as the final scientific figures or the layout source of truth. Save useful mockups under `assets/figures/` and record them in `assets/provenance.json` as human-assist layout mockups.

## Imagegen Draft Rules

- Use `$imagegen` for visual concept drafts and style exploration.
- Draft prompts must state that official logos are placeholders unless user-provided assets are explicitly included.
- Draft prompts must state that scientific figures may be placeholders unless the exact figure is being inserted or referenced.
- Prefer a few large expressive figures over dense paper copy-paste.
- Keep poster drafts presentation-oriented. They should give the human tools for a 5-10 minute explanation, not reproduce the paper layout.
- Avoid inventing benchmark numbers, equations, method steps, or conclusions not supported by the source.

## Human-Assist Asset Rules

- For recreated charts, record the exact source table or data file and the transformation used.
- For reusable charts or mockups, prefer a PDF/vector master when practical and include a PNG preview for quick inspection or direct editor placement.
- For rendered or cropped figures, preserve the source path, page or source file, crop if any, DPI, and output path.
- For text polishing, keep claims faithful to the paper. Mark uncertain wording as a suggestion rather than evidence.
- For case studies, separate available raw material from recommended story structure. Do not imply a multi-step trace exists unless it is in the source or provided by the user.
- For screenshots of human-made posters, give concrete visual feedback on hierarchy, alignment, spacing, contrast, cropping, and readability.

## Common Assembly Pitfalls

- Do not paste dense paper figures into the poster unchanged when the poster slot is much smaller or has a different narrative role. Recompose, crop, simplify, or recreate the visual when needed.
- Do not let a selected concept draft become a rigid final specification. Treat it as a style and layout contract, then adjust each section against the actual human-made poster screenshot.
- Do not create figure walls without analysis. Pair evidence visuals with short, explicit takeaways when the section promises analysis or interpretation.
- Do not over-explain every subcomponent equally. Let the paper's core contribution and the poster story determine visual emphasis.
- Do not repeat the same example across many sections when a later section needs a fresh walkthrough. Reuse examples only when the repetition strengthens the story.
- Do not introduce terminology that drifts from the paper's central framing. Poster copy should stay aligned with the paper's chosen terms even when simplified.
- Do not overfill case studies with every available intermediate artifact. Select the minimum trace that shows query, formalization or plan, key evidence, computation, and answer.
- Do not use final-answer cards as large filler. If space remains, prefer a concise conclusion, computation summary, or traceability takeaway that supports the poster narrative.

## Final QA Pass

Before treating a human-assembled poster as ready, review the latest screenshot or export for:

- source and claim integrity: no fake numbers, unsupported claims, unverified logos, or terminology drift from the paper
- export cleanliness: no spellcheck underlines, editor selection handles, placeholder boxes, clipped text, or accidental UI artifacts
- visual hierarchy: section titles, figures, captions, and analysis text have clear priority from poster-viewing distance
- consistency: colors, borders, icon style, math notation, capitalization, and figure labels are aligned across sections
- print readiness: source figures are high enough resolution, charts have vector/PDF masters when practical, and small text remains legible after export
- provenance: generated, recreated, rendered, cropped, and user-provided assets are recorded in `assets/provenance.json`

## References

- Read `references/planning.md` before concept drafts, style contracts, or screenshot critique.
- Read `references/figure-assets.md` when creating or adapting scientific helper assets.
- Read `references/asset-provenance.md` before adding logos, templates, recreated charts, generated assets, or user-provided media.

## Optional Helper Scripts

This folder may keep small scripts for rendering source figures or extracting figure regions. Use them only when they directly help create a human-assist asset. They are optional tools, not the default workflow and not the source of truth.

If a helper needs unavailable dependencies, either use a simpler local method or state exactly what is missing. Do not install implementation-backend dependencies unless the user explicitly asks for a new automation path.

## Confirmation Gates

Default mode is interactive at design gates and source-ambiguity gates. Do not ask for every small helper asset.

### Must Stop For User Confirmation

Stop and ask the user when:

- Visual drafts are ready and a design direction must be selected.
- The conference size, orientation, or required template cannot be inferred.
- A source figure region or case-study source is ambiguous and affects scientific meaning.
- An official identity asset cannot be verified.
- A recreated chart would require guessing missing data.

### No Confirmation Needed

Proceed without asking for:

- reading source materials
- drafting planning notes
- generating imagegen draft prompts
- creating low-risk helper charts from explicit trusted tables
- polishing short section titles, captions, and bullets
- giving feedback on a user-provided poster screenshot
- leaving logo or case-study placeholders when assets are not available

## Output Checklist

For a concept-design pass, finish with:

- the draft images or their saved paths
- the recommended direction and why it fits the poster story
- the selected style/layout contract if the user has chosen a direction
- the next human-editing tasks

For a human-assist pass, finish with:

- the generated asset paths or revised text blocks
- the source evidence used
- any uncertainty or manual follow-up needed
