# Adaptation Rules

Use these rules to keep inspiration useful without turning it into imitation.

## Core Principle

Borrow design language. Do not borrow brand identity.

Good borrowing:

- section rhythm
- visual density
- spacing behavior
- typography hierarchy
- color relationships
- component character
- animation restraint or boldness

Bad borrowing:

- logos
- proprietary imagery
- slogans or campaign copy
- trademarked phrases
- highly recognizable one-to-one page structure
- brand-specific iconography

## Adapt The Reference Into The Project

If the project already has:

- a component library
- tokens
- typography utilities
- layout primitives

then map the reference into those systems instead of replacing them.

Examples:

- use the local button component with new token choices rather than hand-building a brand-copy button
- use local spacing primitives to reproduce pacing instead of hardcoding arbitrary numbers everywhere
- reuse the project's breakpoint strategy even if the reference site uses different ones

## Keep One Primary Design Story

Choose one strong primary inspiration.

Avoid:

- Apple hero plus Stripe cards plus Notion typography plus Framer motion all on one page

If you need a second influence, limit it to a small role such as:

- primary brand for overall page feel
- fallback brand for one subpattern like pricing cards or docs navigation

## Translate Brand Language Into Implementation Language

When reading a `DESIGN.md`, convert it into implementation choices like:

- headline scale
- contrast model
- card radius
- CTA weight
- section padding
- screenshot treatment
- mobile collapse pattern

This is more useful than repeating descriptive prose.

## Respect The User's Content

The user's product, copy, and audience should drive the final page.

Do not force a reference where it makes the content feel false. Example:

- a playful low-cost consumer promo page should not automatically become sparse Apple minimalism

## Responsive Rule

Do not mechanically shrink desktop compositions.

Instead:

1. preserve the narrative order
2. preserve the emphasis hierarchy
3. preserve the mood through spacing, contrast, and typography
4. simplify ornament before sacrificing clarity

## When To Stay Local

Stay within the local project design language when:

- the task is an incremental addition
- the project already has clear brand guidelines
- the external reference would cause visual inconsistency across the app
- the user's request is more about implementation than visual direction

## Safe Summary Template

Before coding, summarize the reference in this shape:

- chosen reference:
- why it fits:
- traits to borrow:
- traits to avoid copying:
- page structure:
- mobile adaptation:
- codebase constraints:
