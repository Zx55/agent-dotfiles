# [Project Name] Workflows

## Purpose

Explain which workflows this document defines and what level of behavior it owns.

Clarify the difference between:

- workflow meaning
- implementation details
- adapter exposure

## Workflow List

List the main workflows in the current phase.

For each workflow, create a section using the pattern below.

## [Workflow Name]

### Goal

State what the workflow is supposed to accomplish.

### Steps

Describe the normal sequence of the workflow as numbered steps.

### Important Rules

List the invariants or constraints that must hold for this workflow.

These should answer questions such as:

- what must happen before this workflow can run
- what must never happen implicitly
- what should remain reviewable or auditable
- what must stay out of scope for the current phase

### Ownership Notes

Clarify which layer owns:

- workflow semantics
- orchestration
- persistence effects
- user-facing rendering

### Current-Phase Limits

If the workflow is intentionally incomplete, narrow, or hidden from normal users in the current phase, say so explicitly.
