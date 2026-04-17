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

## Review Findings

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
