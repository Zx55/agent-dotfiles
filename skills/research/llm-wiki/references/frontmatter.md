# LLM Wiki Frontmatter

## Purpose

This document defines the frontmatter contract for durable pages inside `~/Documents/codex-workspace/llm-wiki/pages/`.

The goal is to keep pages readable to humans while preserving enough structure for deterministic tooling and future indexing.

## Applies To

This contract applies to durable pages under:

- `pages/source-notes/`
- `pages/concepts/`
- `pages/entities/`
- `pages/artifacts/`
- `pages/questions/`
- `pages/syntheses/`
- `pages/topic-maps/`

It does not need to apply to raw sources under `raw/`.

## Minimum Frontmatter

Each durable page should contain YAML frontmatter with at least:

```yaml
---
page_id: pg-concept-example
title: Example Title
type: concept
status: active
created_at: 2026-04-12
updated_at: 2026-04-12
aliases: []
domains: []
source_refs: []
related_pages: []
confidence: working
review_state: draft
---
```

## Field Meanings

### `page_id`

- stable unique page identity
- should use lowercase kebab-case
- should not change casually after creation

Format:

- `pg-type-short-name`

Examples:

- `pg-concept-mixture-of-experts`
- `pg-artifact-openai-agents-sdk`
- `pg-question-what-makes-agent-evals-reliable`

### `title`

- the human-readable title of the page
- may contain capitalization and punctuation when useful

### `type`

Must be one of:

- `source-note`
- `concept`
- `entity`
- `artifact`
- `question`
- `synthesis`
- `topic-map`

### `status`

Suggested values:

- `active`
- `archived`
- `superseded`

Use a small stable vocabulary. Do not create ad hoc status values casually.

### `created_at`

- the page creation date
- keep it stable once set
- use `YYYY-MM-DD`

### `updated_at`

- the last meaningful update date
- update this when the content materially changes
- use `YYYY-MM-DD`

### `aliases`

- naming variants, abbreviations, or alternate spellings
- use this to absorb naming drift instead of creating duplicate pages

Examples:

- `["MoE"]`
- `["OpenAI Agents SDK", "agents-sdk"]`

### `domains`

- broad topic buckets used for grouping and future indexing
- keep them fairly high-level

Examples:

- `["llm", "architecture", "scaling"]`
- `["agents", "tool-use", "evals"]`
- `["research-workflow", "meetings"]`

Prefer reusing existing domain labels instead of inventing slightly different variants.

### `source_refs`

- stable `source_id` values that support the page
- use IDs, not filenames or prose citations

Examples:

- `["src-20260412-paper-switch-transformer"]`
- `["src-20260412-meeting-moe-reading-group", "src-20260410-article-moe-survey"]`

### `related_pages`

- stable `page_id` references when useful
- not every page needs a long list
- use for strong relationships, not every incidental mention

### `confidence`

Suggested values:

- `low`
- `working`
- `high`

This is a lightweight signal for how settled the page content is.

### `review_state`

Suggested values:

- `draft`
- `reviewed`
- `needs-review`

Keep this simple. The purpose is maintenance visibility, not heavy workflow tracking.

## Optional Fields

Optional fields may be introduced when there is clear value and they remain stable.

Reasonable examples:

- `canonical_name`
- `source_type`
- `meeting_date`
- `participants`
- `artifact_kind`
- `question_state`

Do not expand the schema casually. Prefer fewer stable fields over many low-signal ones.

## Source IDs

Pages use `page_id`, but source-linked content also depends on stable `source_id`.

Recommended format:

- `src-YYYYMMDD-kind-short-name`

Examples:

- `src-20260412-paper-switch-transformer`
- `src-20260412-meeting-moe-reading-group`
- `src-20260412-article-openai-agents-sdk`

## Style Rules

- Use lowercase kebab-case for IDs.
- Keep frontmatter compact and predictable.
- Do not store prose explanations in frontmatter.
- Do not use filenames as identity.
- Do not use freeform tags as a substitute for stable fields.

## Lint Contract

`wiki_cli lint` should validate:

- frontmatter exists
- required fields exist
- `page_id` values are unique
- `type` is valid
- list-like fields are actually lists
- `source_refs` look like stable source IDs
- `related_pages` do not obviously point to impossible values

## Practical Guidance

When unsure whether a field belongs in frontmatter or body text, use this rule:

- if tooling or future indexing needs it, it probably belongs in frontmatter
- if it mainly helps a human understand the content, it belongs in the body
