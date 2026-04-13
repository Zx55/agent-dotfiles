# LLM Wiki Page Types

## Purpose

This document explains what each durable page type is for and what kind of content it should usually contain.

The goal is to prevent page sprawl, type confusion, and accidental duplication.

## General Rule

Prefer one canonical durable page for each enduring concept, artifact, or question.

If a page would only repeat another page with slightly different wording, update the existing page and add aliases rather than spawning a new one.

## `source-note`

Use `source-note` for one source-focused interpretation page tied to a paper, article, meeting, note, or product exploration.

Typical contents:

- what the source is
- why it matters
- key takeaways
- notable claims or observations
- related concepts, artifacts, and questions
- next actions or follow-ups when relevant

Use `source-note` when:

- the input is a concrete source artifact
- you want a durable summary tied to that source
- you want to preserve how this source affected the wiki

Do not use `source-note` as the main long-term home for a broad concept. Move enduring knowledge into `concept`, `artifact`, `question`, or `synthesis` pages.

## `concept`

Use `concept` for methods, ideas, problem framings, architectures, paradigms, or technical topics.

Typical contents:

- short definition
- why the concept matters
- major variants or sub-ideas
- common tradeoffs
- links to supporting artifacts and source-notes
- open questions if they are tightly coupled to the concept

Examples:

- chain-of-thought
- mixture of experts
- tool-use reliability
- verifier-guided search

Do not use `concept` for a specific model, dataset, or product. Those usually belong under `artifact`.

## `entity`

Use `entity` for people, labs, organizations, companies, projects, or named groups.

Typical contents:

- who or what the entity is
- why it matters in the current wiki
- relationships to relevant concepts and artifacts
- notable contributions or roles
- supporting sources

Examples:

- Anthropic
- OpenAI
- Sakana AI
- a research lab or project group

Do not force models, products, or benchmarks into `entity` if `artifact` is a better fit.

## `artifact`

Use `artifact` for tangible research or product objects.

This includes:

- models
- datasets
- benchmarks
- frameworks
- products
- tools
- harnesses

Typical contents:

- what the artifact is
- intended use
- important capabilities or limitations
- relationships to concepts and entities
- relevant comparisons
- source references

Examples:

- GPT-4.1
- SWE-bench
- OpenAI Agents SDK
- Claude Code
- a custom evaluation harness

`artifact` is especially important in this wiki because a lot of AI work does not fit cleanly into only `concept` or `entity`.

## `question`

Use `question` for recurring or unresolved questions worth tracking over time.

Typical contents:

- the question itself
- why it matters
- current hypotheses
- relevant evidence so far
- linked source-notes and syntheses
- what would change your mind

Examples:

- what makes agent evaluations reliable
- when should model behavior be judged with process supervision versus outcome supervision
- how should meeting-derived knowledge be folded into long-term research memory

Do not use `question` for trivial one-off lookups that have no long-term value.

## `synthesis`

Use `synthesis` for curated conclusions, comparisons, or periodic summaries.

Typical contents:

- a framing of the problem or comparison
- the main conclusion or current best view
- key evidence from multiple sources
- uncertainties and caveats
- links to topic maps, questions, and supporting pages

Examples:

- current landscape of agent harnesses
- tradeoffs of tool-use prompting strategies
- what recent meetings imply about a research direction

Use `synthesis` when information from multiple pages needs to be pulled together into a coherent judgment.

## `topic-map`

Use `topic-map` for navigation across a broad or cross-cutting theme.

Typical contents:

- the theme name
- the key concepts
- the key artifacts
- the key source-notes
- active questions
- recent syntheses

Examples:

- topic map for agent evals
- topic map for reasoning models
- topic map for research workflow tooling

`topic-map` is not mainly for conclusions. It is for orientation and discovery.

## Choosing Between Types

Use this quick rule:

- a concrete source goes to `source-note`
- an enduring idea goes to `concept`
- a person or organization goes to `entity`
- a model, tool, product, benchmark, or dataset goes to `artifact`
- a recurring unresolved line of inquiry goes to `question`
- a multi-source conclusion goes to `synthesis`
- a navigational overview goes to `topic-map`

## Common Mistakes

Avoid these mistakes:

- using `source-note` as a dumping ground for all durable knowledge
- creating a `concept` page for every named product
- using `entity` for models and tools
- turning one meeting into many shallow pages
- creating both a `concept` and `artifact` page for the same thing without a real distinction
- confusing `topic-map` with `synthesis`