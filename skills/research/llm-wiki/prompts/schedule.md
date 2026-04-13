# Scheduled Maintenance Prompt

Use the $llm-wiki skill to maintain the personal research wiki at `~/Documents/codex-workspace/llm-wiki`. 

This is a scheduled maintenance run, not normal ingest.

Start by reading `references/maintenance.md` in the $llm-wiki skill.

Then:

- if lint reports structural errors, address them first
- if lint reports no errors and content has not changed since the last maintenance, skip deeper maintenance
- if lint reports no errors but content changed since the last maintenance, perform scheduled maintenance according to the maintenance playbook

When maintenance is performed:

- keep it incremental
- prefer updating existing pages over creating near-duplicates
- update `meta/stats/maintenance-state.yaml` only after maintenance actually completes
- set `last_maintenance_kind` to `scheduled`

Do not treat the scheduled run as a reason for a broad rewrite.
