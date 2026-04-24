---
name: paper-survey
description: Run an end-to-end, topic-driven literature survey workflow across multiple academic papers. Use when the user wants a survey of a research topic across multiple papers rather than a summary or deep reading of a single paper, with optional Zotero capture.
---

# Paper Survey

Use this skill when the user wants a literature survey rather than a single-paper summary.

This skill covers:

- turning a topic into multiple search queries
- broad retrieval and triage
- shortlist construction
- deep reading of core papers
- comparison and synthesis
- optional Zotero lookup or capture

This skill does not require Zotero. Zotero is optional support for library lookup, dedupe, and capture.

## Main-Agent References

The main agent should read [references/workflow.md](references/workflow.md) first.

Then load other references only as needed:

- [references/reading-depth.md](references/reading-depth.md) for skim, comparison, and deep-reading rules
- [references/subagent-prompting.md](references/subagent-prompting.md) when spawning search or deep-reading subagents
- [references/zotero-integration.md](references/zotero-integration.md) only when Zotero lookup, dedupe, tagging, or capture is needed

Before running the survey workflow, initialize a task-local survey workspace with:

- `python <skill-dir>/scripts/init_survey_workspace.py --topic "<topic>"`

Use these source templates during workspace initialization:

- [templates/search_report.template.md](templates/search_report.template.md) for broad-search outputs
- [templates/deep_reading_report.template.md](templates/deep_reading_report.template.md) for core-paper deep reading
- [templates/final_report.template.md](templates/final_report.template.md) for the final synthesis

During execution, subagents should use the materialized task-local templates inside the initialized survey workspace, not the source templates inside this skill.

## Orchestration Model

The main agent owns:

- understanding the user topic
- designing a small set of complementary queries
- orchestrating search and deep-reading subtasks
- deduplicating and clustering candidates
- selecting core papers
- building the comparison matrix
- writing the final report

Subagents own narrowly scoped local work:

- broad retrieval for one query
- deep reading for one core paper
- optional lightweight comparison of a small number of gap-filling papers

Do not ask subagents to improvise the entire workflow. Give them a bounded input, a narrow task, and a fixed output template.

## Subagent Contract

Default subagent settings:

- model: `gpt-5.5`
- reasoning effort: `high`
- `fork_context=false`

Behavior rules:

- search subagents only do broad retrieval and triage
- deep-reading subagents only do one core-paper reading task
- do not reuse a search subagent for deep reading
- once a subagent writes its report artifact, close it
- the main agent should consume report artifacts, not rely on long free-form chat output

## Output Contract

Default final deliverable: Markdown.

Use:

- `search_reports/*.md` for query-level search and triage
- `deep_read_reports/*.md` for one core paper each
- `final_report.md` for the full synthesis

Generate slides only if the user explicitly wants a presentation or speaking deck.
