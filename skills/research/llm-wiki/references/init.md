# LLM Wiki Initialization

## Purpose

This document explains how the wiki should be initialized from an empty or partially prepared state.

## When Initialization Is Needed

Initialize when:

- `~/Documents/codex-workspace/llm-wiki` exists but is mostly empty
- required directories are missing
- core operating files are missing
- the wiki has never been bootstrapped before

Do not re-initialize a healthy wiki just because a few content pages are absent.

## Initialization Goal

After initialization, the wiki should be ready for ingest, query, lint, and maintenance.

It should have:

- a clear root operating guide
- the expected top-level directory structure
- places for raw material, pages, metadata, logs, templates, and tools
- minimal starter files where needed
- a machine-readable maintenance state file under `meta/stats/`

## Preferred Path

Preferred behavior:

1. install the CLI from `~/Documents/codex-workspace/llm-wiki/tools/wiki-cli` with `pip install -e .`
2. use `wiki_cli init`
3. create the expected wiki structure
4. avoid speculative content generation during init

The CLI is the right place for init because the directory contract is stable and deterministic.

## Minimum Bootstrapped Structure

At minimum, initialization should aim for:

```text
~/Documents/codex-workspace/llm-wiki/
  AGENTS.md
  README.md
  index.md
  inbox.md
  logs/
  raw/
  pages/
  meta/
  templates/
  tools/
```

Not every subdirectory must be populated immediately, but the structure should be obvious and ready to receive content.

## Init Contract

`wiki_cli init` should create:

1. the expected directory layout
2. `AGENTS.md`
3. minimal navigation files such as `README.md`, `index.md`, and `inbox.md`
4. the top-level containers needed for raw material, pages, metadata, logs, templates, and tools
5. `meta/stats/maintenance-state.yaml` as the initial machine-readable maintenance state
6. a workspace that is ready for the first real ingest

`wiki_cli init` should not create:

- many speculative concept pages
- placeholder content with no durable value
- database-only infrastructure
- structure that conflicts with the wiki architecture contract

## Output Contract

After `wiki_cli init`, the wiki should be structurally ready for:

- ingest
- query
- lint
- maintenance

Init should create a clean workspace, not fake knowledge.
