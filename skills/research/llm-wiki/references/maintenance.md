# LLM Wiki Maintenance

This document defines how to perform maintenance on the wiki once maintenance is already required or explicitly requested.

## Purpose

Maintenance is about consolidating and repairing existing knowledge structures, not just adding new source material. 

Do not use maintenance as a synonym for ingest.

## Inputs

Before maintenance begins, read:

1. `~/Documents/codex-workspace/llm-wiki/AGENTS.md`
2. `~/Documents/codex-workspace/llm-wiki/meta/stats/maintenance-state.yaml`
3. the latest `wiki_cli lint --json --wiki-path ~/Documents/codex-workspace/llm-wiki` result when available
4. the recent files or pages that motivated maintenance

Useful additional context includes:

- recent files under `logs/`
- recently updated content under `raw/`, `pages/`, and `meta/`
- relevant `topic-map`, `synthesis`, `question`, and `source-note` pages

## Defining Maintenance

Use ingest to capture new source material and update the most directly affected pages.

Use maintenance to consolidate accumulated changes into higher-level structure and repair drift across the wiki.

These actions do not count as maintenance by themselves:

- capturing a new raw source
- creating a new page during normal ingest
- making a small factual correction
- running `wiki_cli lint`

Those actions may create the need for maintenance, but they are not maintenance on their own.

Examples:

- Reading one new paper, creating a `source-note`, and updating one related `concept` page is ingest.
- Folding a week of new papers and meeting notes into `topic-map` and `synthesis` pages is maintenance.
- Cleaning up a duplicate page or repairing a structural issue reported by lint is targeted maintenance.

## Typical Work

Maintenance usually means some combination of:

- refreshing stale `synthesis` pages
- improving or repairing `topic-map` pages
- folding meeting conclusions into durable pages
- repairing naming drift and alias gaps
- merging duplicate or near-duplicate pages
- splitting pages whose scope has become too broad
- tightening cross-links between related concepts, artifacts, and questions

Prefer targeted maintenance over broad rewrites.

## Recommended Workflow

1. Read the current maintenance state.
2. Review the latest lint output and the files that changed since the last maintenance.
3. Decide whether the task is `scheduled`, `manual`, or `targeted`.
4. Plan the smallest useful set of wiki updates.
5. Perform the maintenance edits.
6. Re-run `wiki_cli lint --wiki-path ~/Documents/codex-workspace/llm-wiki`.
7. If the wiki is healthy enough to conclude maintenance, update `meta/stats/maintenance-state.yaml`.

## Maintenance State

The machine-readable maintenance state lives at `~/Documents/codex-workspace/llm-wiki/meta/stats/maintenance-state.yaml`.

Read this file before maintenance so you understand the last known maintenance status.

Current fields:

- `state_version`
- `last_maintenance_at`
- `last_maintenance_kind`

Use one of these maintenance kinds:

- `scheduled` for periodic maintenance windows
- `manual` when the user explicitly asks for maintenance
- `targeted` for focused repair work tied to a specific lint issue or local wiki problem

Choose the narrowest kind that fits the task.

Rules:

- `wiki_cli lint` may read this file but must not update it.
- Only update this file after maintenance has actually completed.
- When maintenance completes, set both `last_maintenance_at` and `last_maintenance_kind`.

## Scope Control

Avoid turning maintenance into a full rewrite.

Do not:

- rewrite large sections of the wiki without a clear reason
- create many shallow pages just because new material exists
- treat every meeting as a reason to fan out multiple new pages
- use maintenance to reformat healthy pages for style alone

The goal is to keep the wiki compact, cumulative, and navigable.
