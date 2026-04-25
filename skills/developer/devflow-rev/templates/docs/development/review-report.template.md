---
create-date: YYYY-MM-DD
lifecycle: active
resolution: in_progress
review_snapshot:
archive_snapshot:
description: Short summary of the review topic.
---

# YYYY-MM-DD-PN Review Report

## Frontmatter Fields

- `create-date`: the date the review document was first opened
- `lifecycle`: whether the document is still active or has been archived
- `resolution`: the current resolution state, such as `in_progress`, `done`, or `deprecated`
- `review_snapshot`: the branch and commit snapshot the review was originally based on
- `archive_snapshot`: the branch and commit snapshot recorded when the review was archived; leave empty while active
- `description`: a short human-readable summary of what the review covers

Typical state combinations:

- active work in progress:
  - `lifecycle: active`
  - `resolution: in_progress`
- completed and kept as history:
  - `lifecycle: archived`
  - `resolution: done`
- superseded or intentionally abandoned:
  - `lifecycle: archived`
  - `resolution: deprecated`

## Summary

State what this review covers and why it exists.

## Goals

List the outcomes this review is trying to achieve.

## Non-Goals

List what this review is not trying to solve.

## Scope

Define which modules, workflows, or boundaries are in scope.

## Code Review Lane

Record findings from the code review lane.

Typical categories:

- request or spec compliance
- correctness and bug risk
- security or data-safety risk
- implementation quality
- test placement or test coverage

For each finding, explain:

- the problem
- why it matters
- severity or priority
- the smallest repair direction

Write `Out of scope` if the user explicitly requested architecture-only review.

## Architecture Review Lane

Record findings from the architecture review lane.

Typical categories:

- boundary drift
- ownership or responsibility drift
- hidden coupling
- extensibility risk
- redundancy at system or workflow level
- deviation from `docs/design/`

Include architectural status when useful:

- `CLEAR`: no unresolved architectural blocker found
- `WATCH`: non-blocking design risk to track
- `BLOCK`: design issue that should prevent merge-ready acceptance

Write `Out of scope` if the user explicitly requested code-only review.

## Plan-Critic Notes

Use this section when reviewing a repair plan, remediation plan, or implementation handoff.

Record whether the plan has:

- clear ownership and file scope
- explicit do-not-touch areas
- testable acceptance criteria
- concrete risks and verification steps

Write `Not applicable` when this review is not evaluating a plan or handoff.

## Verification Evidence

Use this section during acceptance review.

Record:

- `git diff` or artifact evidence checked
- commands, tests, diagnostics, or manual checks run
- missing evidence
- pre-existing failures
- remaining risk

Write `Not applicable` when this is not an acceptance review.

## Review Findings Summary

Group the main findings by severity or ownership.

Typical categories:

- boundary issues
- extensibility risks
- redundancy problems
- testing gaps

For each finding, explain:

- the problem
- why it matters
- the smallest repair direction

## Review Principles

List the rules that should guide the follow-up implementation.

These should be specific enough to prevent the follow-up work from drifting.

## Execution Plan

Describe the intended sequence of follow-up steps.

Use this section for planned work, not historical notes.

## Implementation Notes

Record what was actually implemented and any important decisions made during execution.

Use this section as a lightweight decision record, not a generic changelog.

## Risks And Review Checkpoints

List the risks that should be re-checked during or after implementation.

## Acceptance Criteria

Define what must be true for this review item to be considered complete.
