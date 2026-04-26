# Subagent Prompting

Use this reference only when the user explicitly asks for multi-agent execution and the main agent spawns search or deep-reading subagents.

## Default Contract

Unless there is a strong reason not to:

- use model `gpt-5.5`
- use reasoning effort `high`
- use `fork_context=false`

Pass only the local task context the subagent needs. Do not copy the full conversation unless it is genuinely necessary.

Subagents should usually not read the full skill or the reference set. The main agent should translate the needed instructions into the subagent prompt and point the subagent to the task-local files inside the initialized survey workspace.

Subagents should not read, edit, or update `manifest.md`. Required gates are main-agent orchestration state. Subagents only write their assigned report artifact and any explicitly requested image/media asset files.

Every subagent prompt should have three blocks:

- **Context:** task, inputs, scope boundaries, report language.
- **Artifacts:** task-local template path, output file path, assets directory when relevant.
- **Stop rule:** what not to do, and when to stop.

The subagent should be told to write the report artifact first and return a short completion note with the artifact path.

## Search Subagent Prompt Contract

Prompt fields:

- **Context:** survey topic, input basis, seed terms or seed papers, one search query, why that query exists, time window, report language.
- **Constraints:** date, venue, benchmark, source-quality, and exclusion constraints.
- **Artifacts:** task-local `templates/search_report.md` path and exact output path.

Task requirements:

- find papers relevant to the query
- filter obvious misses
- record primary source links or stable IDs
- distinguish observed source evidence from inference
- avoid doing full deep reading
- fill the report using the template structure
- stop after the report is written

Suggested skeleton:

```text
You are handling one search slice inside a paper survey.

Survey topic:
<topic>

Input basis / seed context:
<text, PDF, image, or mixed input summary; seed papers, figures, methods, datasets, or terms>

Query:
<query>

Why this query exists:
<reason>

Time window:
<time constraint or "none specified">

Report language:
<language>

Constraints:
<constraints>

Use this template:
<survey workspace>/templates/search_report.md

Write the completed report to:
<output path>

Do broad retrieval and triage only. Do not do full deep reading. Read the task-local template, record primary source links or stable IDs, distinguish observed evidence from inference, write the report artifact, then return a short note confirming completion and the output path.
```

## Deep-Reading Subagent Prompt Contract

Prompt fields:

- **Context:** survey topic, target paper identity or local source, comparison dimensions, report language.
- **Artifacts:** task-local `templates/deep_reading_report.md` path, assets directory, exact output path.
- **Scope:** read this paper only; do not broaden into literature search.

Task requirements:

- read the paper deeply enough to complete the template
- ground important claims in section, page, figure, table, appendix, or metric references where available
- pair each important strength and limitation/risk with evidence
- make one explicit visual-anchor decision
- for architecture, system, tokenizer, training-pipeline, benchmark, or empirical model papers, add one useful visual anchor by default, using an original PDF crop when feasible; if using Mermaid or Markdown, put the schematic inline in the deep-reading report, not in `assets/`
- use relative paths inside the report for the local PDF, image assets, and cross-links
- flag claims that need cross-validation from another paper or source
- stay focused on the survey question
- avoid expanding into unrelated paper search
- write the report artifact and stop

Suggested skeleton:

```text
You are handling one core-paper deep reading task inside a paper survey.

Survey topic:
<topic>

Target paper:
<paper identity or source>

Focus comparison dimensions:
<dimensions>

Report language:
<language>

Use this template:
<survey workspace>/templates/deep_reading_report.md

Use this assets directory for optional image/media visual anchors:
<survey workspace>/assets

Write the completed report to:
<output path>

Read only as deeply as needed to complete the template well for this survey. Do not broaden into a new literature search. Read the task-local template, write in the requested report language, ground important claims in specific paper locations where available, pair strengths and limitations/risks with evidence, make one explicit visual-anchor decision, add an anchor by default for architecture/system papers unless there is a concrete reason not to, prefer a PDF crop when feasible, put Mermaid/Markdown schematics inline if used, use relative paths in the report, flag claims that need cross-validation, write the report artifact, then return a short note confirming completion and the output path.
```
