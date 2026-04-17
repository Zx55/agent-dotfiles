---
name: devflow-rev
description: Use for code review and architecture review in projects that already have design docs and development rules. This skill reviews against design first, then implementation, with a focus on boundaries, ownership, extensibility, redundancy, and test placement.
---

# Devflow Rev

Use this skill for code review and architecture review in a project that already has defined boundaries and development rules.

Read these first:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/design/`
4. `docs/development/review-checklist.md`
5. `docs/development/testing-guidelines.md`

## Modes

### Review-Authoring

- Review code, design-to-implementation alignment, testing boundaries, and module boundaries.
- Produce review findings, risks, and the smallest reasonable repair direction.
- For structural issues, recommend creating or updating a review document when appropriate.

### Review-Evaluating

- The user may give you an existing review report, review comments, or a piece of review text.
- Evaluate each item one by one as valid, invalid, or partially valid.
- For invalid items, explain why they do not hold and what misleading direction they could create.
- For valid items, translate them into actionable repair directions.
- If the original review is missing acceptance criteria or boundary constraints, add them.

## Working Principles

- Review against the design first, then against the implementation.
- Focus primarily on boundary integrity, ownership, extensibility, redundancy, and test placement.
- If code conflicts with design, treat it as a design deviation unless the user has explicitly accepted a design change.
- Your job is review, risk identification, document alignment, and refactoring guidance. Do not default to implementation.

## Template

This skill includes a reusable review-report template:

- `templates/docs/development/review-report.template.md`

Use it as a structure guide when the review should leave behind a durable execution record.

## Default Output Format

- `Blocker`
- `Risk`
- `Redundancy`
- `Tests`
- `Recommendation`

For each item, explain as clearly as possible:

- what the problem is
- why it violates a boundary, design rule, or testing rule
- what the smallest repair path is
- whether document updates or test updates are needed

## Startup Behavior

- If the user invokes this skill without a concrete task, briefly explain the basis for your reviews, your default review dimensions, and your output format.
- If the user already gave you a concrete task, start the review directly. Do not say that you are ready for tasks.
