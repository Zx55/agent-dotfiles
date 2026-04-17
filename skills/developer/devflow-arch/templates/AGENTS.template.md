# [Project Name] AGENTS

## Project Contract

Describe what the project is, what role it plays, and what kind of engineering posture contributors should take.

Cover:

- the product or system identity
- the current project phase
- the primary engineering values for this repository
- the main caution for contributors, such as design-first, compatibility-sensitive, safety-critical, or performance-sensitive

## Source Of Truth

List the documents that define intended behavior and architecture.

Use this section to answer:

- which documents win when code and docs disagree
- which files define architecture, workflows, schema, or domain language
- whether there is a single canonical document set or several distinct sources of truth

## Working References

List the developer-facing documents that explain how to work in the repository.

Typical examples:

- docs map
- repository structure
- surface and visibility rules
- review checklist
- testing guidelines
- active plans or review docs

## Development Conventions

Document the project-specific engineering rules that should shape implementation decisions.

Possible subsections:

- language-specific rules
- dependency rules
- module ownership rules
- visibility or API surface rules
- error-handling rules
- logging, tracing, or observability rules
- persistence or migration rules

The goal is to give later contributors stable rules they can apply without rediscovering them from code.

## Boundary Rules

Define the major architectural boundaries in plain language.

Cover:

- main layers or slices
- allowed dependency directions
- what must stay out of each layer
- where key request, result, and error types should live
- what is intentionally public versus internal

If the project has no mature architecture yet, define the intended target boundary shape instead of describing every current implementation detail.

## Testing Expectations

Explain how test placement should follow ownership.

Cover:

- where public contract tests belong
- where internal contract tests belong
- where implementation-detail tests belong
- what strong coverage means in this project
- what kinds of weak or redundant tests to avoid

## Workflow Rules

Describe how contributors should work in this repository.

Typical examples:

- planning before implementation
- documentation updates alongside design changes
- review-driven execution
- feature slicing expectations
- how to treat compatibility or migrations

## Phase Policy

Define what the current phase is trying to achieve and what should explicitly not be introduced yet.

Cover:

- the current delivery focus
- acceptable shortcuts versus forbidden shortcuts
- future mechanisms that should wait until a later phase

## Commit Or Change Policy

If the project has conventions for commit subjects, PR structure, review docs, or release discipline, define them here.

## Non-Negotiable Invariants

List the invariants that every change must preserve.

These should be short, durable, and easy to review against.
