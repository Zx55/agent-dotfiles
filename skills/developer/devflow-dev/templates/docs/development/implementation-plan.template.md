---
create-date: YYYY-MM-DD
lifecycle: active
status: draft
plan_snapshot:
archive_snapshot:
description: Short summary of the implementation plan.
---

# Implementation Plan

## Frontmatter Fields

- `create-date`: the date the plan was first opened
- `lifecycle`: whether the document is still active or has been archived
- `status`: the current state of the plan, such as `draft`, `approved`, `in_progress`, `done`, or `deprecated`
- `plan_snapshot`: the branch and commit snapshot the plan was originally based on
- `archive_snapshot`: the branch and commit snapshot recorded when the plan was archived; leave empty while active
- `description`: a short human-readable summary of what the plan covers

Typical state combinations:

- active draft:
  - `lifecycle: active`
  - `status: draft`
- approved or currently being executed:
  - `lifecycle: active`
  - `status: approved` or `status: in_progress`
- completed and kept as history:
  - `lifecycle: archived`
  - `status: done`
- superseded or intentionally abandoned:
  - `lifecycle: archived`
  - `status: deprecated`

## Summary

State what capability, refactor, or repair this plan covers.

## Goals

List the intended outcomes of the plan.

## Non-Goals

List what the plan intentionally does not include.

## Constraints

Record the design, phase, compatibility, operational, or surface constraints that the implementation must respect.

## Proposed Approach

Describe the chosen implementation shape at a high level.

Explain why this approach was chosen over the most likely alternatives.

## Step Plan

Break the work into `Step1`, `Step2`, and so on.

Each step should include:

- `Goal`
- `Do`
- `Do Not`
- `Planned Files And Purpose`
- `Risks`
- `Tests`
- `Acceptance Criteria`
- `Decision Points` if any

For `Planned Files And Purpose`:

- list the files or directories expected to change
- explain why each one is part of the step
- write `No file changes` if the step is documentation-only or analysis-only

## Risks

List the main implementation and review risks.

## Testing Strategy

Explain which boundaries will be tested and why those test locations are correct.

## Acceptance Criteria

Define the overall completion criteria for the plan.
