# Risk Checks

Use deterministic inspection output as the first evidence layer, then apply LLM judgment conservatively. For semantic edits, use `evidence-check.md` to verify the proposed change against rollout summaries before treating it as apply-ready.

## Sensitive Content

Flag likely secrets without copying their values:

- API keys, bearer tokens, OAuth tokens, session tokens, passwords
- private key blocks
- references to `.secret`, `secret.local`, or secret-bearing environment files
- commands that include credentials inline

Do not include secret text in reports, plans, or final answers.

## Low-Value Memory

Flag material that is unlikely to be useful long term:

- one-off debug notes
- transient command failures that were immediately fixed
- temporary local paths or scratch files
- repeated status updates without durable decisions
- stale implementation details for deleted branches or abandoned experiments

## Conflicts And Duplicates

Flag:

- repeated headings or near-identical paragraphs
- user preferences that contradict newer preferences
- project facts superseded by later decisions
- old migration state that has since become baseline

## Size And Growth

Flag unusually large files or directories:

- large `memory_summary.md`, because injected memory should stay compact
- large `MEMORY.md`, because search quality declines when it becomes noisy
- rapid growth in `raw_memories.md` or `rollout_summaries/`

Size alone is not a reason to delete content. It is a reason to inspect and plan.

## Portability

Flag:

- hard-coded `/Users/<name>/...` paths when `~/...` would be more portable
- temporary directories such as `/tmp`, `/private/var/folders`, or app cache paths
- machine-specific runtime paths that should not become durable memories

Absolute paths inside `rollout_summaries/` are usually evidence paths. Flag them, but do not normalize rollout files during ordinary maintenance.
