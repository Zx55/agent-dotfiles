# Poster Draft Planning

Use this reference before generating visual drafts, writing a style/layout contract, or helping a human revise a poster screenshot.

## Planning Outputs

Create these files inside the poster workspace when the decisions have durable value:

- `planning/story-plan.md`
- `planning/figure-candidates.json`
- `planning/draft-prompts.md`
- `planning/style-layout-contract.md`
- `assets/provenance.json`

Do not ask the user to preselect every figure or style. Infer a first plan from the paper, template, existing slides, screenshots, and conference context. The user chooses after seeing visual drafts.

## Story Plan

A poster should support a short walk-up explanation. Identify:

- the research problem
- the method or system contribution
- the main empirical proof
- one or two supporting analyses
- a qualitative example or case study when it helps the audience understand the method

Prefer 4-6 major sections. Keep the poster presentation-oriented instead of copying the paper structure.

## Figure Candidate Selection

For each candidate, record:

- source path and source type
- rough description
- why it belongs on the poster
- intended section
- priority: `must`, `should`, or `optional`
- whether it is exact source evidence, a recreated helper chart, or a placeholder

A figure should earn space by supporting the poster story.

## Visual Drafts

Use `$imagegen` to make 2-4 overall poster draft images. These are layout and style comps only. They should use placeholder blocks for exact paper figures unless a source figure is explicitly included as a reference.

Draft prompts should specify:

- poster size and orientation
- academic AI/ML or domain-specific tone
- approximate section layout
- density level
- color system and header grammar
- figure-heavy regions and empty placeholders
- no fake logos
- no fake scientific data
- no final scientific text unless provided by the user

After the user chooses a draft, write a style/layout contract instead of treating an automated deck spec as the source of truth.

## Style/Layout Contract

Record:

- canvas and grid
- section order and relative emphasis
- title/header treatment
- colors, typography, line style, and panel style
- exact figure slots and source evidence
- unfinished areas that the human will complete manually

## Screenshot Feedback

When the user provides a screenshot from PowerPoint, Keynote, Figma, or another editor, critique concrete visual issues:

- hierarchy
- alignment
- spacing
- cropping and figure scale
- contrast
- section-title consistency
- readability at poster distance
