---
name: paper-survey
description: Run an end-to-end, topic-driven literature survey workflow across multiple academic papers. Use when the user wants a survey of a research topic across multiple papers rather than a summary or deep reading of a single paper, with default Zotero capture for selected core papers.
---

# Paper Survey

## When To Use

Use this skill when the user wants a literature survey rather than a single-paper summary.

Use it for topic-driven work across multiple papers, including:

- deriving a survey topic from text, PDFs, images, or their combination
- turning a topic into multiple search queries
- broad retrieval and triage
- shortlist construction
- deep reading of core papers
- comparison and synthesis
- default Zotero dedupe and capture for selected core papers

## Invocation Mode

Default execution is single-agent. The main agent should run the workflow itself and write all artifacts unless the user explicitly asks for multi-agent execution, delegation, subagents, or parallel agent work.

Use multi-agent execution only when the user's request clearly opts in, for example:

- "use multi-agent"
- "use subagents"
- "run the survey in parallel"
- "delegate search/deep-reading tasks"

If the user opts into multi-agent execution, follow the subagent orchestration and prompt contracts in this skill. If the user does not opt in, do not spawn subagents; treat all subagent-oriented references as artifact and task-structure guidance for the main agent.

## Start Here

The main agent should read [references/workflow.md](references/workflow.md) first.

Before running the survey workflow, initialize a task-local survey workspace:

- `python <skill-dir>/scripts/init_survey_workspace.py --topic "<topic>"`

The workspace materializes task-local templates and creates the report directories. During execution, use the task-local templates inside that workspace, not the source templates inside this skill.

Use the generated `manifest.md` as the task-local progress checklist. The main agent updates its required gates as the survey moves through search, Zotero capture, deep reading, visual anchors, and final report assembly. In multi-agent mode, subagents should not read or update `manifest.md`.

## Reference Map

Load additional references only when needed:

- [references/reading-depth.md](references/reading-depth.md) for skim, comparison, and deep-reading rules
- [references/visual-assets.md](references/visual-assets.md) when extracting paper figures, screenshots, or visual anchors for deep-reading reports
- [references/zotero-integration.md](references/zotero-integration.md) before capturing selected core papers into Zotero
- [references/subagent-prompting.md](references/subagent-prompting.md) only when the user explicitly opts into multi-agent execution

Source templates copied during workspace initialization:

- [templates/search_report.template.md](templates/search_report.template.md) for broad-search outputs
- [templates/deep_reading_report.template.md](templates/deep_reading_report.template.md) for core-paper deep reading
- [templates/final_report.template.md](templates/final_report.template.md) for the final synthesis

## Responsibility Model

The main agent always owns:

- understanding the user topic
- designing a small set of complementary queries
- orchestrating search and deep-reading subtasks
- deduplicating and clustering candidates
- selecting core papers
- building the comparison matrix
- writing the final report

In default single-agent mode, the main agent also owns:

- query-level broad retrieval and triage
- core-paper deep reading
- lightweight comparison reads for evidence gaps

In explicit multi-agent mode, subagents own narrowly scoped local work:

- broad retrieval for one query
- deep reading for one core paper
- optional lightweight comparison of a small number of gap-filling papers

In multi-agent mode, do not ask subagents to improvise the entire workflow. Give them a bounded input, a narrow task, and a fixed output template.

## Zotero Assumption

This skill assumes Zotero MCP is available. If Zotero MCP is unavailable, read $zotero-mcp-installation skill and help the user install, configure, or repair Zotero MCP before library capture.

## Multi-Agent Contract

This section applies only when the user explicitly opts into multi-agent execution.

Use [references/subagent-prompting.md](references/subagent-prompting.md) for the full subagent prompt contract.

Default subagent settings:

- model: `gpt-5.5`
- reasoning effort: `high`
- `fork_context=false`

Core behavior rules:

- give subagents bounded local tasks
- make subagents write report artifacts into the survey workspace
- close subagents after their artifact is complete

## Output Contract

Default final deliverable: Markdown. Use:

- `search_reports/*.md` for query-level search and triage
- `deep_read_reports/*.md` for one core paper each
- `assets/*` for paper figure crops, screenshots, and visual anchors used by deep-reading reports
- `final_report.md` for the reader-facing synthesis

The final report should be reader-first: put core papers, comparison matrix, key claims, synthesis, and gaps before execution details. Move search strategy, evidence standard, shortlist, Zotero capture, and run metadata into appendices.

In `final_report.md`, link each core paper to its corresponding `deep_read_reports/*.md` artifact and record the concrete Zotero collection path used for captured papers.

Generate slides only if the user explicitly wants a presentation or speaking deck.
