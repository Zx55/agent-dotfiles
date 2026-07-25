# Fork Update And CLI Audit

Use this reference when the user asks to update Dayu, wants a different fork revision, or suspects the CLI changed. The default installation source is `Zx55/dayu-agent@dev`.

## Update posture

- Run the doctor before changing the installation.
- Capture the current spec with `uv tool list --show-version-specifiers --show-python`.
- Resolve the current fork head with `gh api repos/Zx55/dayu-agent/commits/dev --jq .sha` when `gh` is available.
- Review the fork commits that will be introduced before installation when the update is not already understood.
- Do not synchronize the fork with upstream as part of an ordinary local install. Fork synchronization is a separate repository-maintenance action.
- If the existing workspace config is healthy, pass `--skip-init` unless the changed code requires `init`, the user wants first-run setup, or the user wants a provider refresh.
- Do not run `--overwrite-init` or `--reset-init` merely because the branch advanced.

Preferred update command for an existing configured workspace:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --ref dev --skip-init
```

Pinned revision:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --ref <full-commit-sha> --skip-init
```

## Change triage

Classify reviewed changes into:

- installer changes: Python version, dependency model, executable names, or source layout
- init/config changes: provider options, workspace files, prompts, overwrite requirements, or reset requirements
- research CLI changes: command names, arguments, defaults, session/run behavior, or output format
- render/reporting changes: `dayu-render`, templates, or output paths
- operational fixes that require no skill text changes

Update only the files owned by the affected category.

## Documentation boundaries

Keep the files narrow:

- `SKILL.md`: usage boundary, high-level workflow, and reference routing
- `install.md`: fork install mechanics, commands, assumptions, and generic verification
- `update.md`: fork revision review, CLI audit, stale-doc cleanup, and provider refresh decisions
- `troubleshooting.md`: symptoms and recovery paths only
- `openai_compatible_provider.md`: manual provider repair after init is insufficient

If two files state the same procedural rule, keep the detail in the narrower reference and replace the other copy with a short pointer.

## CLI surface audit

After installing the selected ref, inspect the commands documented by the skills:

```bash
dayu-cli --help
dayu-cli prompt --help
dayu-cli interactive --help
dayu-cli download --help
dayu-cli upload_filing --help
dayu-cli upload_filings_from --help
dayu-cli upload_material --help
dayu-cli process --help
dayu-cli process_filing --help
dayu-cli process_material --help
dayu-cli write --help
dayu-cli sessions --help
dayu-cli runs --help
dayu-cli cancel --help
dayu-cli host --help
dayu-cli conv --help
dayu-cli init --help
dayu-render
dayu-web --help
```

The fork workflow specifically requires `dayu-cli prompt --help` to expose `--output`. Treat its absence as an incorrect or stale install.

Then search both skills for stale source and command mentions:

```bash
rg -n "noho/dayu-agent|releases/download|--version|dayu-cli|dayu-render|dayu-web|prompt|--output|conv|write|reset-init|overwrite-init" \
  ~/Documents/agent-dotfiles/shared/skills/finance/dayu \
  ~/Documents/agent-dotfiles/shared/skills/finance/dayu-installation
```

Patch the sibling `dayu` skill when research commands or workflow semantics changed. Patch this installation skill when setup, update, init, executable discovery, source revision, or render verification changed.

## Init and provider refresh

If the reviewed commit requires provider or config regeneration, make the mode explicit and protect existing config.

Overwrite refresh:

```bash
dayu-cli init --base ~/.dayu/workspace --overwrite
```

Reset refresh:

```bash
dayu-cli init --base ~/.dayu/workspace --reset
```

Only run overwrite or reset when the reviewed change requires it or the user requests it. If an OpenAI-compatible provider still needs manual config, continue with [openai_compatible_provider.md](openai_compatible_provider.md).

## Verification

A complete update has:

- `uv tool list --show-version-specifiers --show-python` showing the expected fork ref or commit
- doctor passing for uv, Python, `dayu-cli`, the prompt `--output` flag, `dayu-render`, and workspace config
- `dayu-cli --help` and command-specific help matching the documented workflows
- `dayu-render` returning usage text when invoked without arguments
- no stale upstream-release install commands in either skill

In the final response, include the prior spec, installed fork ref or commit, exact install command, whether init was skipped or run, CLI audit result, and the skill files updated.
