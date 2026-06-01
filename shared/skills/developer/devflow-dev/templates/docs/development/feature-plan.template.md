---
create-date: YYYY-MM-DD
lifecycle: active
status: approved
plan_snapshot:
archive_snapshot:
description: Short summary of the feature or refactor plan.
---

# YYYY-MM-DD-PN Feature Plan

## Frontmatter Fields

- `create-date`: the date the plan was first opened
- `lifecycle`: whether the document is still active or has been archived
- `status`: the current plan state, such as `approved`, `in_progress`, `done`, or `deprecated`
- `plan_snapshot`: the branch and commit snapshot the plan was originally based on
- `archive_snapshot`: the branch and commit snapshot recorded when the plan was archived; leave empty while active
- `description`: a short human-readable summary of what the plan covers

Write this document after the user has approved the plan direction. A newly created feature plan should normally start as approved, not as a draft.

Typical state combinations:

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

State what capability, refactor, or repair this feature plan covers and why it exists.

## Goals

List the intended outcomes.

## Non-Goals

List what this plan intentionally does not include.

## Constraints

Record design, phase, compatibility, operational, surface, or testing constraints that the implementation must respect.

## Candidate Plans

List the viable implementation paths considered before selecting one.

For each candidate, summarize:

- what it changes
- why it might be attractive
- why it might be risky or less appropriate

## Selected Plan

Describe the chosen implementation shape at a high level.

Explain why this approach was selected over the main alternatives.

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
- write `No file changes` if the step does not require file edits

## Round Plan

If using multi-agent orchestration, group steps into rounds.

For each round, record:

- which tasks can run together
- which files or ownership areas each task owns
- which dependencies must be resolved first
- which tests the main agent must rerun after integration

## Task Ownership

Record planned task owners when using subagents.

For each task, include:

- owner or role
- write scope
- do-not-touch scope
- expected tests
- acceptance criteria

## Risks And Checkpoints

List risks that should be re-checked during or after implementation.

## Testing Strategy

Explain which boundaries will be tested and why those test locations are correct.

## Acceptance Criteria

Define what must be true for the plan to be considered complete.

## Implementation Notes

Record what was actually implemented and any important decisions made during execution.

Use this section as a lightweight decision record, not a generic changelog.

## Resolution Summary

When complete, summarize:

- final outcome
- commits or major change groups
- final verification commands
- known residual risks or follow-ups
