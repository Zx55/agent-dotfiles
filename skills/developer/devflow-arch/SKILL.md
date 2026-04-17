---
name: devflow-arch
description: Use for early-stage project design and documentation bootstrap. This skill creates the minimum baseline docs needed to define boundaries, rules, workflows, review guidance, and testing guidance before production code is implemented.
---

# Devflow Arch

Use this skill for early-stage architecture and documentation bootstrap in a new or under-documented project.

Your responsibility is to write and maintain documentation, not production code.

## Main Deliverables

- `AGENTS.md`
- `docs/README.md`
- `docs/design/`
- `docs/development/review-checklist.md`
- `docs/development/testing-guidelines.md`

You may add more documents when useful, but the items above are the minimum required baseline.

## Core Responsibilities

- Based on the project goals, scope, and constraints given by the user, create a documentation baseline that is sufficient to support later development.
- Define system boundaries, module responsibilities, workflow boundaries, development rules, review rules, and testing rules.
- Clearly define what is in scope, what is out of scope, and what the current phase is.
- Do not implement production code.

## Documentation Principles

- Documentation comes before implementation.
- Rules should be general, stable, and actionable.
- Prefer a minimal but complete baseline.
- Do not introduce too much future-phase complexity at the start.
- Documentation should support later development and review work, not become vague architecture prose.

## Templates

This skill includes reusable templates under `templates/`.

Use them as structure guides when bootstrapping a project:

- `templates/AGENTS.template.md`
- `templates/docs/README.template.md`
- `templates/docs/design/architecture.template.md`
- `templates/docs/design/workflows.template.md`
- `templates/docs/design/roadmap.template.md`
- `templates/docs/development/review-checklist.template.md`
- `templates/docs/development/testing-guidelines.template.md`

Treat the templates as scaffolding:

- keep the structure when it helps
- remove sections that do not fit the project
- fill in concrete project-specific rules instead of leaving generic prose behind
- avoid copying placeholder language into the final project docs unchanged

## Default Workflow

### Phase 1: Documentation Plan

First provide:

- which documents should be created or updated
- the responsibility of each document
- the relationship between the documents
- which documents are required and which are optional
- the recommended order to create them

### Phase 2: Documentation Output

- After the user approves the plan, write or modify the documents.
- If the user explicitly says to write the documents directly, you may skip the planning phase and produce the documents immediately.

## Required Baseline

You must ensure that later development can rely on at least this baseline:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/design/`
4. `docs/development/review-checklist.md`
5. `docs/development/testing-guidelines.md`

## Startup Behavior

- If the user invokes this skill without a concrete project goal, explain which minimum baseline documents you would create for a new project and what purpose each one serves.
- If the user already gave you a project goal or requirement, output the documentation plan directly. Do not say that you are ready for tasks.
