# LLM Wiki Operations

## Purpose

This document defines the default operational behavior for the `llm-wiki` skill.

It covers four main operations:

- ingest
- query
- lint
- maintain

## Orientation

Before doing substantial wiki work:

1. read `~/Documents/codex-workspace/llm-wiki/AGENTS.md`
2. inspect relevant pages under `pages/`
3. inspect relevant registries under `meta/` when they exist
4. inspect logs when recent activity matters

Do not create new pages blindly when related ones may already exist.

## Initialize

Initialization is a valid operation for this skill.

Default initialize order:

1. install the CLI from `~/Documents/codex-workspace/llm-wiki/tools/wiki-cli` with `pip install -e .` when needed
2. use `wiki_cli init --wiki-path ~/Documents/codex-workspace/llm-wiki` to bootstrap the wiki
3. ensure the wiki is structurally ready before any ingest work begins
4. treat initialization as a deterministic setup operation governed by `references/init.md`

Use initialization to create the workspace contract, not to create speculative knowledge content.

## Ingest

Use ingest when information should become part of the long-term wiki.

Common ingest inputs:

- papers
- article clippings
- meeting summaries
- transcripts
- research notes
- product evaluations
- deep research outputs

Default ingest sequence:

1. Capture the source under the correct `raw/` subtype.
2. Assign a stable `source_id`.
3. Register the source in `meta/source-registry/`.
4. Create or update the matching `source-note`.
5. Update affected durable pages.
6. Update topic maps if the knowledge crosses themes.
7. Log meaningful changes.

Preferred update pattern:

- update an existing page if the concept already exists
- create a new page only if the knowledge has durable standalone value
- record naming variants as aliases rather than spawning duplicate pages

## Query

The wiki is both a reading surface and a memory layer for agents.

Default query order:

1. check `question`, `synthesis`, and `topic-map` pages first
2. check supporting `concept`, `artifact`, `entity`, and `source-note` pages
3. use web search if the wiki clearly lacks coverage or the question is time-sensitive
4. ingest durable new findings when appropriate

Use the web first when the user asks about:

- latest releases
- current pricing
- recent product changes
- current benchmark standings
- anything obviously time-sensitive

Use the wiki first when the user asks about:

- established concepts
- recurring research themes
- prior comparisons or syntheses
- meeting-derived context
- earlier work already preserved in the wiki

## Lint

Lint is primarily a deterministic operation.

Default to `wiki_cli lint --wiki-path ~/Documents/codex-workspace/llm-wiki`.

Lint scope should include:

- required directory checks
- required starter file checks
- maintenance state validation
- frontmatter presence
- required field validation
- `page_id` uniqueness
- page type validation
- list field validation
- non-standard `page_id`, `source_refs`, and `related_pages` detection
- wikilink validation
- orphan detection
- duplicate title candidate detection
- dynamic maintenance context, including latest content change time and whether content changed since the last maintenance

Use LLM judgment only for semantic review tasks that are not reliably programmable.

## Maintain

Maintenance is periodic and should remain incremental. When maintenance is actually required, follow `references/maintenance.md`.

Default maintenance trigger rules:

- Updating or ingesting content does not count as maintenance by itself.
- If `wiki_cli lint` reports errors, fix them promptly and enter maintenance when needed to restore structural health.
- If content was added or updated but `wiki_cli lint` reports no errors, do not force immediate maintenance.
- Use scheduled maintenance to fold clean new content into topic maps, syntheses, and other higher-level pages.
- Use manual maintenance when the user explicitly asks for cleanup, consolidation, or a wiki refresh.

## Scope Control

Avoid making the wiki noisy.

Do not:

- create pages for passing mentions
- create duplicate pages because naming differs slightly
- turn every meeting into many shallow pages
- use maintenance as an excuse for full rewrites

The right behavior is to keep the wiki compact, cumulative, and navigable.
