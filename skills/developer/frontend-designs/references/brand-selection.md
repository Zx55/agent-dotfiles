# Brand Selection

Use this guide to choose a `DESIGN.md` reference when the user has not already provided one.

## Selection Order

1. If the project already has a local `DESIGN.md`, prefer it.
2. If the user explicitly names a brand, use that brand.
3. Otherwise infer a brand from:
   - page archetype
   - product category
   - tone
4. If the match is unclear, choose one primary recommendation and at most one fallback.

## The Three Axes

### Page Archetype

- promo page
- marketing homepage
- docs entry page
- dashboard
- pricing or comparison page

### Product Category

- hardware
- fintech
- developer tool
- AI product
- content or productivity

### Tone

- premium
- technical
- playful
- editorial
- minimal
- cinematic

## Fast Mapping

Use these as defaults, then adjust for the actual prompt.

| Request Pattern | Primary Reference | Fallback |
|---|---|---|
| phone or hardware promo page | Apple | BMW |
| premium consumer product page | Apple | SpaceX |
| SaaS landing page | Stripe | Vercel |
| developer tool homepage | Vercel | Linear |
| dark technical dashboard | Linear | Sentry |
| developer platform with infrastructure feel | Vercel | Supabase |
| fintech marketing page | Stripe | Coinbase |
| docs or knowledge-driven site | Mintlify | Notion |
| playful creative tool | Figma | Framer |
| high-end motion-forward marketing site | Framer | Apple |
| AI product landing page | Claude | Vercel |
| content-first editorial product page | Notion | Sanity |

## Heuristics

### Apple

Choose when the page should feel:

- premium
- product-first
- hardware-oriented
- sparse and controlled
- cinematic rather than busy

Good fits:

- phones
- laptops
- devices
- premium accessories
- launch or keynote-style product pages

### Stripe

Choose when the page should feel:

- polished
- trustworthy
- technical
- financially credible
- clean but not sterile

Good fits:

- SaaS
- fintech
- developer-focused marketing pages
- enterprise product storytelling

### Vercel

Choose when the page should feel:

- sharp
- developer-native
- modern
- dark or neutral
- product-led without too much ornament

Good fits:

- developer tools
- infrastructure products
- AI tooling for builders
- technical landing pages

### Linear

Choose when the page should feel:

- precise
- minimal
- dark
- focused
- product-systematic

Good fits:

- dashboards
- productivity tools
- product feature pages
- premium dark interfaces

### Notion or Mintlify

Choose when the page should feel:

- readable
- content-led
- calm
- editorial
- documentation-friendly

Good fits:

- docs homepages
- knowledge products
- template galleries
- content-heavy software sites

## When Not To Pull A New Brand

Do not fetch a new `DESIGN.md` when:

- the project already has a strong established design system and the task is local or incremental
- the user is only asking for a bug fix or small component adjustment
- the requested page tone conflicts strongly with the most obvious brand reference
- the user wants originality more than recognizable inspiration

## Choosing A Fallback

Only offer a fallback when the user prompt is genuinely ambiguous or the first brand may be too strong.

Examples:

- hardware promo page: `Apple`, fallback `BMW`
- developer tool launch page: `Vercel`, fallback `Linear`
- docs-heavy product marketing: `Mintlify`, fallback `Notion`

Avoid listing many brands unless the user explicitly asks for options.
