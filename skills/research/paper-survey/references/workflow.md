# Workflow

Use this reference to run the survey from topic to synthesis.

## Execution Model

The workflow is artifact-based.

That means:

- the main agent should initialize a task-local survey workspace first
- subagents should write structured Markdown report artifacts
- the main agent should read those artifacts for the next step
- do not rely on long free-form chat output as the main handoff surface

Recommended workspace shape:

```text
surveys/
  survey-<topic-slug>-<date>/
    templates/
      search_report.md
      deep_reading_report.md
      final_report.md
    search_reports/
    deep_read_reports/
    final_report.md
    manifest.md
```

Initialize the workspace with:

```bash
python <skill-dir>/scripts/init_survey_workspace.py --topic "<topic>"
```

Recommended artifact names inside the workspace:

- search stage: `search_<query_slug>.md`
- deep reading stage: `deep_read_<paper_slug>.md`
- final synthesis: `final_report.md`

The main agent should always be explicit about the paths it expects subagents to read and write.

## Phase 0: Scope

The user input can be any combination of:

- text topic or question
- one or more PDFs
- one or more images, such as screenshots, figures, diagrams, tables, or paper snippets

At least one input must be present.

First normalize the inputs into:

- the target topic or question
- the input basis: text, PDF, image, or mixed
- seed papers, figures, methods, datasets, or terms extracted from the inputs
- explicit constraints from the user
- inferred constraints that should be treated as assumptions

Then clarify:

- the intended outcome: overview, method comparison, reading-group note, implementation-oriented summary, or decision support
- the expected depth and time budget
- the time window, if the user specified one

If the request is underspecified, make a reasonable default assumption and state it in the final report.

Do not invent a time limit by default. If the user asks for "recent", "latest", "last N months", or names a date range, convert it into an explicit search constraint and pass it to search subagents.

## Phase 0.5: Initialize Survey Workspace

Before spawning subagents:

- run `python <skill-dir>/scripts/init_survey_workspace.py --topic "<topic>"`
- confirm the survey workspace path
- use the task-local template files under `templates/`
- write all stage artifacts into this survey workspace

The script should create the workspace root, materialize task-local templates, and create the report directories.

## Phase 1: Query Design

Design `3-5` complementary queries. They should not be trivial restatements of the same phrase.

Prefer mixing these angles:

- task or problem framing
- method family or paradigm
- dataset / benchmark / evaluation setting
- synonyms or adjacent terminology
- recent or foundational framing when appropriate

Carry forward time constraints from Phase 0. For example, "recent", "last six months", and "since 2024" should become explicit query constraints.

The main agent owns query design.

## Phase 2: Broad Retrieval And Triage

Assign one search subagent per query when parallelism helps.

Each search subagent should receive:

- the survey topic
- one query
- any scope boundaries or exclusion rules
- the task-local `templates/search_report.md` path
- an explicit output path

Each search subagent should produce one Markdown artifact following the task-local `templates/search_report.md`.

The artifact should capture:

- the query
- why the query exists
- candidate papers
- primary source links or IDs
- short relevance notes grounded in observed source text
- obvious coverage gaps
- keep / borderline / drop recommendations
- claims that need verification during deep reading

The main agent should then:

- read all search report artifacts
- merge candidates across queries
- deduplicate overlapping hits
- cluster papers by method family or direction

Search subagents should stop after writing their report artifact. Close them once the artifact is complete.

## Phase 3: Merge, Deduplicate, Cluster

The main agent should merge search outputs and then:

- remove duplicates
- collapse near-duplicate variants
- group papers by method family or research direction
- note obvious gaps in coverage

The shortlist should usually land around `15-30` papers, depending on topic breadth.

## Phase 4: Select Core Papers

Choose about `5` core papers for deep reading.

Selection criteria:

- central relevance to the user topic
- representativeness of a major method family
- influence or visibility if that matters for the task
- complementarity across approaches
- enough diversity to support meaningful comparison

Avoid selecting five slight variants of the same idea.

## Phase 4.5: Zotero Capture

Before deep reading, use [zotero-integration.md](zotero-integration.md) to dedupe and capture the selected core papers into Zotero.

Default behavior:

- check whether each selected core paper already exists in Zotero
- avoid duplicate imports using DOI, arXiv ID, title, and stable URL signals
- import missing core papers with PDF attachments when available
- inspect imported child items
- delete low-value arXiv import notes when they only contain acceptance, homepage, or venue metadata
- remove all tags from newly imported items
- choose the best existing target collection for the survey topic
- place newly imported and already-existing core papers into that target collection
- preserve useful user-created notes and annotations

If Zotero MCP is unavailable, read $zotero-mcp-installation skill and help the user install, configure, or repair Zotero MCP. If capture still cannot be completed in the current run, record the unresolved capture status in the final report.

## Phase 5: Deep Reading

Assign one deep-reading subagent per core paper.

Use [reading-depth.md](reading-depth.md) for the skim, comparison-read, and deep-read criteria.

Each deep-reading subagent should receive:

- the survey topic
- the target paper identity or source
- the comparison dimensions to pay attention to
- the task-local `templates/deep_reading_report.md` path
- an explicit output path

Each deep-reading subagent should produce one Markdown artifact following the task-local `templates/deep_reading_report.md`.

The main agent should then:

- read the deep-reading artifacts
- extract stable comparison dimensions
- preserve claim-to-evidence links from the evidence logs
- build a comparison matrix
- identify missing evidence
- mark which important claims still need cross-validation

Deep-reading subagents should stop after writing their report artifact. Close them once the artifact is complete.

## Phase 6: Cross-Validation Gate

Before writing synthesis, the main agent must classify key claims into:

- cross-validated: supported by at least two independent sources, or by one source plus directly checked primary evidence
- single-source: supported by one paper only
- indirect: inferred from related evidence but not directly stated or tested
- unsupported: not backed by a located source

Evidence gaps are mandatory. If a claim is single-source, indirect, or unsupported, either soften it in the final report or move it into `Evidence Gaps And Uncertainties`.

Use lightweight comparison reads when cross-validation is needed for an important claim. Do not add extra reading just to confirm minor background details.

## Phase 7: Comparison And Synthesis

The main agent should compare core papers across a stable set of dimensions, such as:

- task framing
- method family
- supervision or data assumptions
- compute / memory / latency tradeoffs
- benchmark setup
- empirical strengths
- empirical weaknesses
- failure modes or limitations

Only promote a synthesis claim when it is traceable to a search report, deep-reading report, or directly checked source. If the evidence is weak or not cross-validated, mark it as an evidence gap or explicitly lower the confidence.

If an important comparison dimension is still unsupported, add `2-3` lightweight comparison reads rather than promoting many more papers to full deep reading.

## Phase 8: Final Report

The main agent should write the root `final_report.md` in the survey workspace, using the task-local `templates/final_report.md` as the structure reference.

It should be based on:

- the merged shortlist
- the search report artifacts
- the deep-reading artifacts
- any gap-filling comparison reads

The final report should include an evidence section that distinguishes:

- well-supported claims
- weakly supported claims
- missing comparisons
- points that require another source check

The final report must include `Evidence Gaps And Uncertainties`, even when the section says no major gaps were found.

## Stopping Rule

Stop broadening the search when:

- the shortlist already covers the main method families
- new papers are mostly redundant
- the comparison matrix has enough evidence to answer the user's question

Do not keep searching merely because more papers exist.
