# Storyboard and narrative

Start with the authoritative materials supplied by the user. For research talks, read the paper and inspect existing figures, supplementary material, website, and video slides as relevant. Existing slides are reusable assets, not proof that their pacing fits a longer talk.

Agree on the audience's assumed knowledge, target duration, main claim, and what the audience should retain. Use a provisional page count based on content and speaking time, not one minute per page as a rigid rule. Some visual transitions take 20 seconds, while a mathematical example may need 90 seconds.

Write `storyboard.md` using the template. Each page needs a single purpose, proposed title, key content, visual structure, evidence/assets, approximate duration, and a distinct role relative to adjacent pages. Record open factual questions. Put full narration in `notes/`, not in the storyboard.

## Lessons for a coherent talk

- A broad motivation page and a scoped problem-definition page should do different jobs. Do not prematurely narrow the opening just to preview the next page.
- Reuse one running example when it reduces cognitive load. Do not repeat the full input photographs and query on every page without a new purpose.
- A progressive reveal across consecutive HTML pages can keep the same diagram coordinates while adding annotations or replacing the formula. Explicitly record which elements remain fixed.
- Distinguish problem formulation, proposed method, worked example, and empirical evidence. Do not call an explanatory analogy an official method term.
- Preserve historical context for motivating model weaknesses. “At the time of our experiments” is different from a claim about today's strongest model.
- Give a case study enough room for its setup and execution. Merge sparse experiment pages when they answer the same question, instead of adding decoration to fill space.
- Avoid default audience voting or interactions unless they serve the user's setting.

When the number or order of pages changes, update filenames, visible numbers, notes, asset references, and storyboard together. Exporters require a continuous sequence beginning at 1. Do not leave an obsolete `slideNN.html` in the active slides directory.

If the user asks only for layout, provide a compact composition and content plan first. Do not silently implement the entire deck. If a layout is already approved, continue implementation without another approval loop.
