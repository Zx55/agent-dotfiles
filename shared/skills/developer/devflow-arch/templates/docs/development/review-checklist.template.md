# Review Checklist

## Purpose

Explain what this checklist is for and what kinds of review it should guide.

Typical focus areas:

- boundary integrity
- extensibility
- redundancy control
- testing quality

Clarify that this document is review guidance, not the source of truth for product behavior.

## Review Stance

Define what reviewers should compare first.

Typical rule:

- review against design docs first
- then against implementation

Also list the related documents reviewers should use, such as:

- architecture docs
- workflow docs
- testing guidelines
- surface rules

## How To Use This Checklist

Explain the review order and the intended output style.

Useful prompts:

- what responsibility slice owns this change
- what contract does it expose
- what dependencies is it allowed to take

## Review Workflow

### 1. Boundary

Questions to include:

- Is the owner of the behavior clear?
- Does the change stay in the correct layer?
- Are dependency directions still intentional?
- Has the public surface grown without a real external need?
- Has the change introduced half-wired scaffolding or widened visibility too early?

### 2. Extensibility

Questions to include:

- Can this shape grow without forcing a rewrite of boundaries?
- Is the behavior localized in the natural owner?
- If a second variant appears later, will the design still hold?
- Are request, result, and error types owned by the right module?

### 3. Redundancy

Questions to include:

- Did the change duplicate policy or validation across layers?
- Did it introduce another way to express the same concept?
- Are helpers or mappings beginning to drift?
- Is documentation repeating details that belong in one authoritative place?

### 4. Tests

Questions to include:

- Is coverage placed at the boundary that owns the contract?
- Do tests protect caller-visible behavior instead of accidental internals?
- Are success, boundary, and failure paths covered where they matter?
- Are parallel features covered symmetrically unless there is a reason not to?

### 5. Project Invariants

List the project-level invariants every review should re-check.

These should be copied or adapted from `AGENTS.md` rather than invented ad hoc.

## Output Format

Define the preferred review output categories.

Typical categories:

- `Blocker`
- `Risk`
- `Redundancy`
- `Tests`
- `Recommendation`

For each item, explain:

- what the problem is
- why it matters
- what the smallest repair path is
- whether docs or tests need updates

## Documented Review Workflow

Use a documented review document when the work is structural rather than purely local, or when the review should leave behind a durable execution record.

Typical triggers include:

- cross-module boundary cleanup
- crate-surface or visibility changes
- test migration across ownership boundaries
- large internal module splits or merges
- architectural cleanup that should happen in sequenced steps
- review work that will be implemented over multiple follow-up steps

Place documented review documents under `docs/development/review/` using this filename pattern:

- `YYYY-MM-DD-PN.md`

Do not rename the file later just to reflect archive status. Keep the filename stable and record lifecycle state in frontmatter instead.

Required frontmatter:

```yaml
---
create-date: 2026-04-16
lifecycle: active
resolution: in_progress
review_snapshot: main@abc1234
archive_snapshot:
description: Short summary of the review topic.
---
```

Field meanings:

- `create-date`: the date the document was opened
- `lifecycle`: `active` or `archived`
- `resolution`: `in_progress`, `done`, or `deprecated`
- `review_snapshot`: the git branch and commit snapshot the review was originally based on
- `archive_snapshot`: the git branch and commit snapshot recorded when the document was archived; leave empty while active
- `description`: a short human-readable summary

Typical state combinations:

- active work in progress:
  - `lifecycle: active`
  - `resolution: in_progress`
- completed and retained as historical record:
  - `lifecycle: archived`
  - `resolution: done`
- superseded or intentionally abandoned:
  - `lifecycle: archived`
  - `resolution: deprecated`

Use this recommended structure unless there is a clear reason to shorten it:

- `# YYYY-MM-DD-PN Review Report`
- `Summary`
- `Goals`
- `Non-Goals`
- `Scope`
- `Review Findings` or `Current Problems`
- `Review Principles`
- `Execution Plan`
- `Implementation Notes`
- `Risks And Review Checkpoints`
- `Acceptance Criteria`

Do not add a standalone `Purpose` section unless it contributes review-specific information that is not already obvious from the title, summary, and description.

`Execution Plan` and `Implementation Notes` have different jobs and should not be collapsed together.

- `Execution Plan` records the intended sequence before or during the work
- `Implementation Notes` record what the implementation owner actually did while carrying out the review follow-up work

The implementation owner should update both sections during execution:

- revise `Execution Plan` when the intended sequence or scope changes
- append or refine `Implementation Notes` as steps are completed and concrete decisions are made

Use them to record:

- what was actually implemented
- where implementation intentionally differed from the initial plan
- what boundary or ownership decision was selected
- any follow-up constraints that future review should preserve

Treat `Implementation Notes` as decision records, not as a generic changelog.