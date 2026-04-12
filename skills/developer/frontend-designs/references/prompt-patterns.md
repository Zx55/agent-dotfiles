# Prompt Patterns

Use these examples to recognize when the skill applies and which mode to use.

## Explicit Brand Request

User:

```text
Make a phone product page that feels like Apple.
```

Response pattern:

- choose `Apple`
- use `reference mode`
- fetch `DESIGN.md` if missing
- produce an implementation brief
- build the page

## Implicit Brand Inference

User:

```text
Make a phone promo page for our new flagship device.
```

Response pattern:

- infer `Apple` as the primary reference
- optionally keep `BMW` as a fallback if the tone needs to feel more engineered than consumer-tech
- use `reference mode`

## SaaS Marketing Page

User:

```text
Build a polished landing page for our developer billing product.
```

Response pattern:

- infer `Stripe` first
- consider `Vercel` as fallback if the product leans more developer-tool than fintech
- use `reference mode`

## Existing Local DESIGN.md

User:

```text
Add a pricing page to this project.
```

Response pattern:

- check for local `DESIGN.md`
- if present, reuse it
- do not fetch a new brand unless the user asks
- use `reference mode`

## Switch To Project Mode

User:

```text
Use this visual direction for future marketing pages too.
```

Response pattern:

- keep the selected local `DESIGN.md`
- move into `project mode`
- update local `AGENTS.md` with a concise design-reference note

## Safe Internal Brief Example

```text
Chosen reference: Apple
Why it fits: The task is a premium phone promo page and needs a product-first, cinematic presentation.
Traits to borrow: Large hero scale, sparse copy, restrained blue CTAs, strong contrast, generous vertical pacing.
Traits to avoid copying: Apple brand copy, logo use, proprietary product imagery, and one-to-one section replication.
Page structure: Hero, feature sequence, camera/performance sections, specs summary, closing CTA.
Mobile adaptation: Preserve the narrative order and premium spacing, but stack imagery and copy more aggressively.
Codebase constraints: Use the project's existing frontend stack and reusable layout primitives.
```
