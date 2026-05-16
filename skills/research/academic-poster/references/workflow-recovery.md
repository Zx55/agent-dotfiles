# Workflow Recovery

Long poster jobs must be resumable.

## Workspace Layout

```text
<workspace>/
├── manifest.json
├── poster-spec.json
├── inputs/
├── planning/
├── drafts/
├── assets/
├── regions/
├── exports/
└── qa/
```

## Manifest Stages

Use these stage names:

- `initialized`
- `inputs_registered`
- `planned`
- `drafts_generated`
- `draft_selected`
- `regions_extracted`
- `pptx_built`
- `exports_rendered`
- `qa_passed`

Each stage should record:

- status: `pending`, `in_progress`, `done`, or `blocked`
- timestamp
- artifact paths
- notes

## Resume Rule

On resume:

1. Read `manifest.json`.
2. Verify artifacts for the latest `done` stage still exist.
3. Continue at the first `pending`, `blocked`, or missing-artifact stage.
4. Do not regenerate user-approved drafts unless the user asks.
5. Do not overwrite final exports without creating a new version or confirming replacement.

## Source Of Truth

If PPTX and `poster-spec.json` disagree, trust `poster-spec.json` unless the user explicitly says they manually edited the PPTX and wants those edits imported.
