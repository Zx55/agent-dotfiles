---
name: frontend-designs
description: Use DESIGN.md brand references for frontend work. When a user asks for a landing page, promo page, homepage, or a recognizable visual style, pick a fitting design inspiration, fetch the corresponding DESIGN.md on demand, adapt it into an implementation brief, and use it to guide UI work. Supports both one-off reference mode and persistent project mode with optional AGENTS.md integration.
---

# Frontend Designs

Use this skill when a frontend task needs stronger visual direction than the current prompt provides.

This skill is not a brand-cloning tool. It uses `DESIGN.md` as a visual reference for layout rhythm, typography, spacing, color relationships, component feel, and overall page atmosphere.

## Use This Skill For

- brand-inspired landing pages, promo pages, and marketing homepages
- requests like "make it feel like Apple", "reference Stripe", or "use a premium developer-tool aesthetic"
- frontend tasks where the user describes the page goal but not the visual system
- projects that already contain a `DESIGN.md`
- requests to persist a design direction for future UI work

## Do Not Use This Skill For

- minor UI bug fixes that should stay inside an established local design system
- tasks where the user only wants functional implementation with no visual direction change
- requests that would copy third-party logos, product imagery, brand copy, or highly specific branded layouts

## Workflow

1. Check whether the project already has a local `DESIGN.md`.
2. If it does, prefer it unless the user explicitly asks for a different brand reference.
3. If the user explicitly names a brand, use that brand.
4. Otherwise infer a fitting brand from:
   - page archetype
   - product category
   - tone and ambition
5. Fetch the chosen `DESIGN.md` only when needed:
   - `scripts/fetch_design.sh <brand>`
6. Read the fetched `DESIGN.md` and produce an implementation brief before coding.
7. Build within the project's existing stack and component boundaries.
8. Only move into project mode when the user wants the design direction to persist across future work.

## Modes

### Reference Mode

Default mode for one-off tasks.

Use the selected `DESIGN.md` for the current page, feature, or redesign only. Do not modify project-level guidance files automatically.

### Project Mode

Use this mode only when the user clearly wants the design direction to persist, for example:

- "use this style for future marketing pages"
- "make this project's UI work reference DESIGN.md from now on"
- "wire this design direction into the project workflow"

In project mode:

1. fetch or confirm the local `DESIGN.md`
2. update the project's `AGENTS.md` with a short note describing how to use it
3. keep the note narrow and implementation-friendly

See `references/project-mode.md`.

## Implementation Brief

Before coding, write a short internal brief that answers:

- why this brand was chosen
- which traits to borrow
- which page structure fits the user's request
- how the reference should be adapted to the current project
- what must not be copied literally
- how the page should behave on mobile

The brief should translate brand language into implementation choices. Example:

- not just "Apple"
- but "high-contrast hero, restrained blue CTAs, product-first imagery, generous vertical pacing, minimal chrome"

## Boundaries

Treat `DESIGN.md` as visual guidance, not as permission to reproduce a brand identity.

Do not copy:

- logos
- trademarks
- marketing copy
- product imagery
- signature illustrations
- exact layouts when imitation would be too literal

Prefer adaptation over replication:

- borrow hierarchy, pacing, weight, contrast, and component character
- map those traits onto the user's actual content and existing codebase
- preserve reusable local components when possible

If the project already has strong UI conventions, adapt the inspiration into those conventions instead of replacing them wholesale unless the user explicitly asks for a broader redesign.

## Brand Selection

Read `references/brand-selection.md` when:

- the user does not name a brand
- multiple brands could fit
- you need a fallback option

## Page Archetypes

Read `references/page-archetypes.md` when you need to translate the design reference into page structure for:

- hardware and phone promo pages
- SaaS landing pages
- marketing homepages
- docs entry pages
- dashboards
- pricing or comparison pages

## Adaptation Rules

Read `references/adaptation-rules.md` when:

- the reference is visually strong and easy to over-copy
- the project already has a component library
- the page must work across mobile and desktop without losing the intended feel

## Prompt Patterns

Read `references/prompt-patterns.md` for examples of:

- explicit brand requests
- inferred brand selection
- existing local `DESIGN.md` reuse
- switching from reference mode to project mode

## Notes

- Prefer one strong primary brand reference over blending many brands together.
- If the match is ambiguous, choose one recommended reference and at most one fallback.
- If no brand is a good fit, say so and stay within the local project design language.
- For browser verification or visual QA, pair this skill with `playwright` when helpful.
