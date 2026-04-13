# Root AGENTS Prompt Snippet

Use the $llm-wiki skill when work should be preserved in the long-lived research wiki instead of staying as a one-off chat result.

Typical trigger conditions include:

- the user finishes or requests a deep research pass with durable value
- the user explicitly asks to add something to the wiki
- a paper discussion produces reusable concepts, comparisons, or conclusions
- a meeting summary or transcript contains lasting technical value
- a tool, product, benchmark, or framework exploration produces reusable notes
- an article or external finding should become part of the long-term knowledge base

When one of these triggers is met:

- use the $llm-wiki skill, follow skill's `references/` as needed
- orient to `~/Documents/codex-workspace/llm-wiki/AGENTS.md`
- prefer incremental updates over broad rewrites

Do not trigger the skill for trivial lookups, ephemeral discussion, or content that clearly does not belong in the wiki.
