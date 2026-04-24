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

Start by clarifying:

- the target topic or question
- the intended outcome: overview, method comparison, reading-group note, implementation-oriented summary, or decision support
- the expected depth and time budget

If the request is underspecified, make a reasonable default assumption and state it in the final report.

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
- short relevance notes
- obvious coverage gaps
- keep / borderline / drop recommendations

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

## Phase 5: Deep Reading

Assign one deep-reading subagent per core paper.

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
- build a comparison matrix
- identify missing evidence

Deep-reading subagents should stop after writing their report artifact. Close them once the artifact is complete.

## Phase 6: Comparison And Synthesis

The main agent should compare core papers across a stable set of dimensions, such as:

- task framing
- method family
- supervision or data assumptions
- compute / memory / latency tradeoffs
- benchmark setup
- empirical strengths
- empirical weaknesses
- failure modes or limitations

If an important comparison dimension is still unsupported, add `2-3` lightweight comparison reads rather than promoting many more papers to full deep reading.

## Phase 7: Final Report

The main agent should write the root `final_report.md` in the survey workspace, using the task-local `templates/final_report.md` as the structure reference.

It should be based on:

- the merged shortlist
- the search report artifacts
- the deep-reading artifacts
- any gap-filling comparison reads

## Stopping Rule

Stop broadening the search when:

- the shortlist already covers the main method families
- new papers are mostly redundant
- the comparison matrix has enough evidence to answer the user's question

Do not keep searching merely because more papers exist.
