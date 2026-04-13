# LLM Wiki Architecture

## Purpose

This document describes the current architecture of the personal research wiki at `~/Documents/codex-workspace/llm-wiki`.

This is a markdown-first system with metadata and registries designed to stay usable without a database while remaining compatible with future CLI and SQLite-assisted indexing.

## Architecture Layers

The wiki is organized into four layers:

1. `raw/`
   Captured source material.

2. `pages/`
   Human-readable, durable knowledge pages.

3. `meta/`
   Machine-readable registries and supporting metadata.

4. `tools/wiki-cli/`
   The repository that provides the `wiki_cli` command for initialization, lint, and later maintenance helpers.

## Expected Wiki Layout

```text
llm-wiki/
  AGENTS.md
  README.md
  index.md
  inbox.md
  logs/
  raw/
    papers/
    articles/
    meetings/
    notes/
    products/
    assets/
  pages/
    source-notes/
    concepts/
    entities/
    artifacts/
    questions/
    syntheses/
    topic-maps/
  meta/
    source-registry/
    entity-registry/
    artifact-registry/
    aliases/
    topic-registry/
    query-registry/
    stats/
  templates/
  tools/
    wiki-cli/
```

Not every directory must exist on day one, but this is the target contract.

## Raw Layer

Everything enters the system first as a source.

Expected source classes:

- papers
- articles
- meetings
- notes
- products
- assets

`raw/` is append-only. Corrections belong in derived pages rather than rewrites of source material.

Meetings are valid sources when they contain substantive technical content.

## Page Layer

The page layer is the main human-facing knowledge surface.

Approved durable page types:

- `source-note`
- `concept`
- `entity`
- `artifact`
- `question`
- `synthesis`
- `topic-map`

Use `artifact` for models, datasets, benchmarks, frameworks, products, tools, and harnesses.

Use `topic-map` to connect cross-cutting themes that do not belong in a single folder or page type.

## Metadata Layer

The metadata layer exists to support deterministic maintenance and future extraction into structured indexes.

Core registries:

- `source-registry`
- `entity-registry`
- `artifact-registry`
- `aliases`
- `topic-registry`
- `query-registry`
- `stats`

In the current design, these registries can stay file-based.

## Stable IDs

Stable IDs are mandatory from the beginning.

Recommended formats:

- source: `src-YYYYMMDD-kind-short-name`
- page: `pg-type-short-name`

Examples:

- `src-20260412-paper-switch-transformer`
- `src-20260412-meeting-moe-reading-group`
- `pg-concept-mixture-of-experts`
- `pg-artifact-openai-agents-sdk`

Filenames are not the durable identity layer.

## Required Frontmatter

Durable pages under `pages/` should include at least:

- `page_id`
- `title`
- `type`
- `status`
- `created_at`
- `updated_at`
- `aliases`
- `domains`
- `source_refs`
- `related_pages`
- `confidence`
- `review_state`

Key rules:

- `page_id` must be unique
- `type` must be valid
- `source_refs` should store stable `source_id` values
- `aliases` should capture naming variants instead of creating duplicate pages

## Topic Maps

Folders are not enough for organization.

Cross-topic structure should live in:

- wikilinks
- aliases
- topic maps
- syntheses

Use topic maps when a theme spans papers, products, meetings, and questions.

## Role Of Obsidian

Obsidian is the preferred human reading and navigation interface for the wiki.

Obsidian is not the system of record. The markdown files are.

The intended split is:

- markdown files are the durable asset
- Obsidian is the human browser
- agents read and update the same markdown files
- tooling validates structure around those files

## Role Of The CLI

The CLI is not the main knowledge surface.

Its job is to provide deterministic maintenance for things that should not depend on LLM judgment, especially:

- init
- lint
- registry rebuilding
- stats
- maintenance helpers

Install it from `~/Documents/codex-workspace/llm-wiki/tools/wiki-cli` with `pip install -e .`, then use the global command `wiki_cli`.

## SQLite Boundary

SQLite is a future helper layer, not part of the base architecture.

When introduced, it should support:

- indexing
- joins across registries
- recall support for queries
- duplicate analysis
- validation support

It should not replace markdown as the primary human-facing system.
