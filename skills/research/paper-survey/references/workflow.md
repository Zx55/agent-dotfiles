# Workflow

Use this reference to run the survey from topic to synthesis.

## Execution Model

The workflow is artifact-based.

Core rules:

- the main agent should initialize a task-local survey workspace first
- structured Markdown report artifacts are the handoff surface between workflow stages
- `manifest.md` is the task-local progress and gate checklist
- update `manifest.md` when a required gate is completed or explicitly marked unresolved
- in multi-agent mode, only the main agent updates `manifest.md`; subagents should not read, edit, or reason about required gates
- the main agent should read completed artifacts before moving to the next stage
- do not rely on long free-form chat output as the main handoff surface

Execution modes:

- default single-agent mode: the main agent writes all report artifacts itself
- explicit multi-agent mode: subagents may write assigned search and deep-reading artifacts

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
    assets/
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

The main agent should always be explicit about artifact paths. In multi-agent mode, it should also be explicit about the paths it expects each subagent to read and write.

## Workflow Focus Map

Use this table to keep the run oriented. Each phase should finish with an artifact or a manifest gate, not just a chat update.

| Phase | Focus | Main Artifact / Gate |
| --- | --- | --- |
| Setup | normalize topic, language, time window, workspace | `Workspace initialized` |
| Search | broad retrieval and triage by complementary query | `search_reports/*.md` |
| Merge | dedupe, cluster, and pick core papers | `Core papers selected` |
| Zotero | dedupe library, import verified PDFs, place collection | `Zotero capture completed or explicitly marked unresolved` |
| Deep Read | claim-level evidence for core papers | `deep_read_reports/*.md` |
| Visuals | one visual-anchor decision per core paper | `assets/*` or explicit `none` reason |
| Synthesis | comparison, claims, gaps, next steps | `final_report.md` |

## Setup: Scope

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

Do not invent a time limit by default. If the user asks for "recent", "latest", "last N months", or names a date range, convert it into an explicit search constraint. In multi-agent mode, pass that constraint to search subagents.

## Setup: Report Language

Match the report language to the user's request by default:

- if the user request is primarily Chinese, write search reports, deep-reading reports, and the final report in Chinese
- if the user request is primarily English, write the reports in English
- preserve paper titles, model names, benchmark names, metric names, citation keys, URLs, and quoted source labels in their original language
- override this default only when the user explicitly asks for a different report language, such as "generate an English report"

In multi-agent mode, pass the report language explicitly to every subagent.

## Setup: Initialize Survey Workspace

Before search and reading work:

- run `python <skill-dir>/scripts/init_survey_workspace.py --topic "<topic>"`
- confirm the survey workspace path
- use the task-local template files under `templates/`
- write all stage artifacts into this survey workspace
- store extracted paper figures, screenshots, generated images, and SVG image assets under `assets/`
- use relative paths inside all Markdown artifacts; avoid absolute local workspace paths because the survey directory may move
- put Mermaid or Markdown schematics inline in the deep-reading report instead of storing separate `.md` schematic files under `assets/`

The script should create the workspace root, materialize task-local templates, and create the report and asset directories.

After initialization, mark `Workspace initialized` complete in `manifest.md`.

## Phase 1: Query Design

Design `3-5` complementary queries. They should not be trivial restatements of the same phrase.

Prefer mixing these angles:

- task or problem framing
- method family or paradigm
- dataset / benchmark / evaluation setting
- synonyms or adjacent terminology
- recent or foundational framing when appropriate

Carry forward time constraints from setup. For example, "recent", "last six months", and "since 2024" should become explicit query constraints.

The main agent owns query design.

## Phase 2: Broad Retrieval And Triage

For each query, produce one `search_reports/search_<query_slug>.md` artifact using the task-local `templates/search_report.md`.

The artifact should capture:

- the query
- why the query exists
- candidate papers
- primary source links or IDs
- short relevance notes grounded in observed source text
- obvious coverage gaps
- keep / borderline / drop recommendations
- claims that need verification during deep reading

Default single-agent mode:

- the main agent runs broad retrieval and triage for each query
- the main agent writes each search report artifact itself

Explicit multi-agent mode:

- assign one search subagent per query when parallelism helps
- give each search subagent the survey topic, one query, constraints, the task-local template path, and one output path
- require each search subagent to write one Markdown artifact following `templates/search_report.md`
- close each search subagent once its artifact is complete

After all search artifacts are complete, the main agent should:

- read all search report artifacts
- merge candidates across queries
- deduplicate overlapping hits
- cluster papers by method family or direction
- mark `Search reports written` complete in `manifest.md`

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

After selecting core papers, mark `Core papers selected` complete in `manifest.md`.

## Zotero Capture

Before deep reading, use [zotero-integration.md](zotero-integration.md) to dedupe and capture the selected core papers into Zotero.

Default behavior:

- **Dedupe:** check each selected core paper before import using DOI, arXiv ID, title, and stable URL signals.
- **Import:** use verified local PDFs and `zotero_add_from_file`; follow [zotero-integration.md](zotero-integration.md) for the PDF completion gate.
- **Clean:** inspect child items, delete only low-value import notes, and remove imported tags from newly imported items.
- **Place:** choose the best existing collection and place both newly imported and already-existing core papers there.
- **Preserve:** keep user-created notes, annotations, existing PDFs, and user-managed metadata intact.

If Zotero MCP is unavailable, read $zotero-mcp-installation skill and help the user install, configure, or repair Zotero MCP. If capture still cannot be completed in the current run, record the unresolved capture status in the final report.

After Zotero capture, mark `Zotero capture completed or explicitly marked unresolved` complete in `manifest.md`. If capture is unresolved, write the reason in `manifest.md` and carry it into the final report.

## Phase 5: Deep Reading

For each selected core paper, produce one `deep_read_reports/deep_read_<paper_slug>.md` artifact using the task-local `templates/deep_reading_report.md`.

Use [reading-depth.md](reading-depth.md) for the skim, comparison-read, and deep-read criteria.

Use [visual-assets.md](visual-assets.md) when a method figure, pipeline diagram, benchmark table, or schematic would make the deep-reading report clearer.

Deep-reading artifacts should:

- **Evidence discipline:** link each important strength and limitation to specific evidence, with PDF page, section, figure, table, appendix, or metric references when available.
- **Visual decision:** include one `Visual Anchor` decision for every core paper.
- **Visual default:** for architecture, system, tokenizer, training-pipeline, benchmark, or empirical model papers, produce at least one useful visual anchor unless the paper has no informative visual and a schematic would add no value.
- **Path style:** use relative links and local paths inside Markdown reports.
- **Asset location:** store extracted figures, screenshots, generated image files, and SVG image assets under `assets/`.

Before deep reading, check whether PDF rendering is available and install PyMuPDF when package installation is acceptable; see [visual-assets.md](visual-assets.md). Prefer original paper figures or PDF crops for the visual anchor. If the paper has no useful figure or the original figure is too dense, use an inline deterministic schematic such as Mermaid or Markdown directly in the deep-reading report. Use SVG or `$imagegen` only when an actual image file adds value and can be verified against the paper; label it as generated, not copied from the paper.

Default single-agent mode:

- the main agent deep-reads each selected core paper
- the main agent writes each deep-reading artifact itself

Explicit multi-agent mode:

- assign one deep-reading subagent per core paper
- give each deep-reading subagent the survey topic, target paper identity or source, comparison dimensions, the task-local template path, and one output path
- require each deep-reading subagent to write one Markdown artifact following `templates/deep_reading_report.md`
- close each deep-reading subagent once its artifact is complete

After all deep-reading artifacts are complete, the main agent should:

- read the deep-reading artifacts
- extract stable comparison dimensions
- preserve claim-to-evidence links from the evidence logs
- build a comparison matrix
- identify missing evidence
- mark which important claims still need cross-validation
- mark `Deep-reading reports written` complete in `manifest.md`
- mark `Visual anchors considered for each core paper` complete in `manifest.md`

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

The final report is reader-first. Put the survey conclusions and comparison content before process details.

Top-level content should appear in this order:

- `Executive Summary`
- `Core Papers`
- `Comparison Matrix`
- `Key Claims And Evidence`
- `Synthesis`
- `Evidence Gaps And Uncertainties`
- `Suggested Next Steps`

Execution details should go in appendices:

- `Appendix: Shortlist`
- `Appendix: Search Strategy`
- `Appendix: Evidence Standard`
- `Appendix: Zotero Capture`
- `Appendix: Run Metadata`

If the execution details would dominate the final report, or if the user asks for a separate audit trail, write them to `run_report.md` and keep only a short appendix with a link to that file.

The report should be based on:

- the merged shortlist
- the search report artifacts
- the deep-reading artifacts
- any gap-filling comparison reads

Required content:

- **Core Papers:** priority, paper title or short name, relative deep-read link, method family, why core, key strength/limitation, evidence basis, Zotero item key or status.
- **Key Claims And Evidence:** separate well-supported claims, weak claims, missing comparisons, and claims requiring another source check.
- **Zotero Appendix:** record collection path, collection key, placement rule, and one row per core paper with item key, collection path, collection key, PDF attachment status, and notes.
- **Evidence Gaps:** include `Evidence Gaps And Uncertainties` even when no major gaps were found.

After writing the final report, update `manifest.md`:

- mark `Final report links deep-reading reports` complete only after checking the links are present
- mark `Final report records Zotero collection path or unresolved status` complete only after checking the Zotero appendix
- mark `Final report includes evidence gaps and uncertainties` complete only after checking the section exists

## Stopping Rule

Stop broadening the search when:

- the shortlist already covers the main method families
- new papers are mostly redundant
- the comparison matrix has enough evidence to answer the user's question

Do not keep searching merely because more papers exist.
