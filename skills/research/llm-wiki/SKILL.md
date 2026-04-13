---
name: llm-wiki
description: Build and maintain a personal markdown-first LLM wiki for AI research work. Use this skill when the user wants to capture or organize papers, deep research outputs, meeting summaries, product explorations, recurring questions, or other high-value research knowledge into the wiki, or when the user wants to query, lint, or maintain that wiki.
metadata:
  short-description: Maintain a personal research wiki
---

# LLM Wiki

This skill manages the personal research wiki stored at `~/Documents/codex-workspace/llm-wiki`.

Within this skill, prefer `~/...` path notation in prose. Resolve it mentally to the user's home directory at runtime.

Use this skill when work should be preserved as part of a long-lived knowledge base instead of staying as a one-off chat result.

## When To Use

Use this skill when the user is:

- reading or discussing papers
- doing deep research worth preserving
- collecting important articles
- exploring a new AI tool, product, framework, benchmark, or harness
- reviewing meeting summaries or transcripts with lasting technical value
- asking for help querying or maintaining the existing wiki

Do not use this skill for trivial lookups, ephemeral chatter, or work that clearly does not belong in the long-term wiki.

## What This Skill Owns

This skill is the workflow orchestrator for the wiki.

It should:

- decide whether something belongs in the wiki
- orient to the current wiki before changing it
- create or update the right markdown pages
- preserve cross-links and topic maps
- keep knowledge incremental and structured

This skill should not be the final authority for deterministic setup or validation. For initialization and structural validation, use `wiki_cli`. Install it from the repo at `~/Documents/codex-workspace/llm-wiki/tools/wiki-cli/`.

## First Reads

Before doing substantial wiki work, read:

1. `~/Documents/codex-workspace/llm-wiki/AGENTS.md`
2. the relevant files under `references/` for this skill

Read additional wiki files as needed:

- `index.md` when it exists
- recent files under `logs/`
- relevant pages under `pages/`
- relevant registries under `meta/`

## Core Rules

- Treat the wiki as markdown-first. Do not design as if a database already exists.
- Prefer updating an existing page over creating a near-duplicate.
- Treat meetings as valid sources when they contain meaningful technical content.
- Use `topic-map` and `synthesis` pages to preserve cross-topic knowledge.
- Use the wiki as a memory layer for non-time-sensitive domain questions.
- Verify time-sensitive or latest-changing facts on the web before answering.
- If a new external finding has durable value, ingest it back into the wiki.

## Directory Model

The wiki has two major roots of concern:

- `~/Documents/codex-workspace/llm-wiki` for the actual knowledge base
- `~/Documents/codex-workspace/llm-wiki/tools/wiki-cli` for the `wiki_cli` package and deterministic maintenance tooling

For the current wiki architecture, read `references/architecture.md`.

## Default Operations

### Initialize

Use initialize when the wiki does not exist yet, is only partially bootstrapped, or is missing its expected directory contract.

Initialization is structural setup, not content generation.

For the detailed contract, read `references/init.md`.

### Ingest

Use ingest when new information should become part of the wiki as durable knowledge.

Examples include papers, articles, deep research results, meeting material with lasting technical value, and tool or product explorations.

For the detailed workflow, read `references/operations.md`.

### Query

Use query when the user wants to retrieve or synthesize knowledge that may already live in the wiki.

For query priority and web-vs-wiki behavior, read `references/operations.md` and `references/query-policy.md`.

### Lint

Use lint for deterministic structural validation.

Structural validation should default to `wiki_cli`, not LLM judgment.

For checks and behavior, read `references/operations.md`.

### Maintain

Use maintenance for periodic cleanup and consolidation after lint or scheduled review indicates it is needed.

For the maintenance playbook, read `references/maintenance.md`.

## Page Types

The durable page types are:

- `source-note`
- `concept`
- `entity`
- `artifact`
- `question`
- `synthesis`
- `topic-map`

If a request pushes beyond these types, keep the extension minimal and consistent with the existing wiki design.

## References

Read these files only when needed:

- `references/architecture.md` for directory layout, object model, IDs, and metadata
- `references/init.md` for bootstrapping and initialization behavior
- `references/operations.md` for ingest, query, lint, and maintenance triggers
- `references/maintenance.md` for the maintenance playbook and completion rules
- `references/frontmatter.md` for page metadata rules and field semantics
- `references/page-types.md` for what each durable page type should contain
- `references/query-policy.md` for when to use the wiki first versus web search first

## Integration Prompts

The `prompts/` directory is for integration snippets such as scheduled maintenance prompts and root `AGENTS.md` trigger guidance.

Do not treat `prompts/` as a substitute for `references/` during normal wiki work.
