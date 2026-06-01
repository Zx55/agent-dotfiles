# Documentation Map

## Purpose

Explain how the `docs/` directory is organized and how contributors should decide where a new document belongs.

This document should separate:

- design source-of-truth documents
- developer-facing implementation guidance
- review or execution records
- planning documents

## Document Roles

### `docs/design/`

Describe what belongs in design docs.

Typical scope:

- intended architecture
- workflow behavior
- domain or ontology rules
- schema or persistence design
- roadmap or phase boundaries

Clarify whether these documents are normative and whether they override current implementation.

### `docs/development/`

Describe what belongs in developer-facing docs.

Typical scope:

- repository organization notes
- review guidance
- testing guidance
- implementation plans
- review records

Clarify that these docs support implementation work and do not replace design source of truth.

### Optional Subdirectories

If the project uses dedicated subdirectories, define them here.

Typical examples:

- `docs/development/review/`
- `docs/development/plans/`
- `docs/adr/`
- `docs/runbooks/`

For each one, explain:

- what kind of document belongs there
- naming conventions if any
- whether documents are long-lived, dated, or archival

## Related Entrypoints

List nearby top-level files that contributors should know about.

Typical examples:

- `README.md`
- `AGENTS.md`
- `docs/design/`
- `docs/development/`
