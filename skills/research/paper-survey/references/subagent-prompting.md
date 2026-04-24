# Subagent Prompting

Use this reference when the main agent spawns search or deep-reading subagents.

## Default Contract

Unless there is a strong reason not to:

- use model `gpt-5.5`
- use reasoning effort `high`
- use `fork_context=false`

Pass only the local task context the subagent needs. Do not copy the full conversation unless it is genuinely necessary.

Subagents should usually not read the full skill or the reference set. The main agent should translate the needed instructions into the subagent prompt and point the subagent to the task-local files inside the initialized survey workspace.

Every subagent prompt should explicitly specify:

- the task
- the inputs
- the task-local template path to follow
- the output file path
- any scope boundaries
- what not to do

The subagent should be told to write the report artifact first and return a short completion note with the artifact path.

## Search Subagent Prompt Contract

Include:

- the survey topic
- one search query
- the goal of that query
- any date, venue, benchmark, or exclusion constraints
- the task-local `templates/search_report.md` path
- the exact output path for the report artifact

Ask the subagent to:

- find papers relevant to the query
- filter obvious misses
- avoid doing full deep reading
- fill the report using the template structure
- stop after the report is written

Suggested skeleton:

```text
You are handling one search slice inside a paper survey.

Survey topic:
<topic>

Query:
<query>

Why this query exists:
<reason>

Constraints:
<constraints>

Use this template:
<survey workspace>/templates/search_report.md

Write the completed report to:
<output path>

Do broad retrieval and triage only. Do not do full deep reading. Read the task-local template, write the report artifact, then return a short note confirming completion and the output path.
```

## Deep-Reading Subagent Prompt Contract

Include:

- the survey topic
- the target paper identity, link, or local source
- the comparison dimensions that matter to the survey
- the task-local `templates/deep_reading_report.md` path
- the exact output path for the report artifact

Ask the subagent to:

- read the paper deeply enough to complete the template
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

Use this template:
<survey workspace>/templates/deep_reading_report.md

Write the completed report to:
<output path>

Read only as deeply as needed to complete the template well for this survey. Do not broaden into a new literature search. Read the task-local template, write the report artifact, then return a short note confirming completion and the output path.
```
