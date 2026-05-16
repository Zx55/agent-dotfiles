# Poster Planning

Use this reference before generating visual drafts or writing `poster-spec.json`.

## Planning Outputs

Create these planning notes inside the poster workspace:

- `planning/story-plan.md`
- `planning/figure-candidates.json`
- `planning/draft-prompts.md`

Do not ask the user to preselect figures or style. Infer a first plan from the paper, optional existing poster, and conference context. The user chooses after seeing visual drafts.

## Story Plan

A poster should communicate one take-home message in a short walk-up interaction.

Identify:

- the research problem
- the method or system contribution
- the main empirical proof
- one or two supporting results
- the implication or takeaway

Prefer 4-6 major sections:

- Header
- Motivation or Problem
- Method
- Results
- Qualitative or Case Study, when useful
- Takeaway, QR, References, and Acknowledgments

## Figure Candidate Selection

For each candidate, record:

- source PDF
- page
- rough description
- why it belongs on the poster
- intended section
- priority: `must`, `should`, or `optional`
- whether the region needs user-confirmed bbox

Prefer original PDF regions for plots, architecture diagrams, formulas, and tables. A figure should earn space by supporting the take-home message.

## Visual Drafts

Use `$imagegen` to make 2-4 overall poster draft images. These are layout and style comps only. They should use placeholder blocks for exact paper figures and readable pseudo-labels rather than trying to reproduce every paper detail.

Draft prompts should specify:

- landscape or portrait
- academic AI/ML or domain-specific tone
- approximate section layout
- density level
- color system
- where figure-heavy regions should sit
- no fake logos
- no final scientific text

After the user chooses a draft, translate the chosen layout into `poster-spec.json`.

## Layout Heuristics

- Put the title, authors, affiliations, logos, and QR in the header.
- Keep section bars and repeated section grammar consistent.
- Give results the largest visual area.
- Avoid more than 800-1000 total words unless the conference requires dense content.
- Use text to label and interpret figures, not to repeat the paper.
- Keep enough whitespace for print readability.

## Orientation

Use the conference template or requirement when available. Otherwise:

- landscape for ML, CS, and figure/table-heavy posters
- portrait for walk-up conference boards, thesis events, or vertical template requirements

Record the reason in `manifest.json`.
