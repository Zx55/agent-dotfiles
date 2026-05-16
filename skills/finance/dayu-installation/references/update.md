# Update And CLI Audit

Use this reference when the user asks to update Dayu, says the version changed, or suspects the CLI changed. The goal is to upgrade the tool and keep both Dayu skills aligned with the real command surface.

## Update posture

- Run the doctor before changing the installation.
- Capture the current installed version with `uv tool list --show-version-specifiers --show-python`.
- Check the latest release notes with `gh release list --repo noho/dayu-agent --limit 10` and `gh release view --repo noho/dayu-agent`. For a pinned release, use `gh release view <tag> --repo noho/dayu-agent`.
- Prefer the bundled installer script for the actual update.
- If the existing workspace config is healthy, pass `--skip-init` unless release notes require `init`, the user wants first-run setup, or the user wants provider config refresh.
- Do not run `--overwrite-init` or `--reset-init` just because a version update happened.
- When release notes require `init --reset`, call out that it rebuilds generated `.dayu`, `config`, and `assets` directories before running it.

Preferred update command for an existing configured workspace:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --version latest --skip-init
```

Pinned fallback:

```bash
./scripts/dayu_install_or_update.sh --workspace ~/.dayu/workspace --version <tag> --skip-init
```

## Release-note triage

After reading release notes, classify changes into:

- installer changes: wheel naming, offline packages, Python version, dependency model, executable names
- init/config changes: provider options, workspace files, prompts, required overwrite, required reset
- research CLI changes: command names, arguments, defaults, session/run behavior, output format
- render/reporting changes: `dayu-render`, `write`, template, output paths
- operational fixes: bugs that do not require skill text changes

Update only the skill files touched by those categories.

## Version-specific hygiene

Every Dayu update must include a pass over all version-specific text in both skills. Do not leave stale version notes behind.

Search broadly:

```bash
rg -n "v[0-9]+\\.[0-9]+\\.[0-9]+|Dayu `[0-9v.+-]+|offline package|MiMo|release notes|dayu_agent-[0-9]" \
  ~/Documents/codex-workspace/agent-dotfiles/skills/finance/dayu \
  ~/Documents/codex-workspace/agent-dotfiles/skills/finance/dayu-installation
```

Rules:

- keep durable installation mechanics in [install.md](install.md) with placeholders such as `<tag>`, not concrete old versions
- keep provider-specific setup mechanics in [openai_compatible_provider.md](openai_compatible_provider.md) only when they are still generally true
- keep current release notes and "this changed in version X" observations in this file
- delete or rewrite superseded notes from older releases when a newer release changes the same behavior
- if a version-specific note remains, it must say why it is still operationally relevant

## Documentation boundaries

Keep the files narrow:

- `SKILL.md`: when to use this skill, high-level workflow, and which reference to read
- `install.md`: normal install path, commands, assumptions, and generic verification
- `update.md`: release review, version-specific notes, CLI audit, stale-doc cleanup, and provider refresh decisions
- `troubleshooting.md`: symptoms and recovery paths only
- `openai_compatible_provider.md`: manual provider config repair after init is insufficient

If two files say the same procedural rule, leave the detail in the narrower reference and replace the other copy with a short pointer.

## CLI surface audit

After installing the new version, inspect the commands documented by the skills:

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

Then search the skill docs for command mentions:

```bash
rg -n "dayu-cli|dayu-render|dayu-web|upload_filing|upload_filings_from|upload_material|download|interactive|prompt|runs|host|sessions|conv|write|reset-init|overwrite-init" \
  ~/Documents/codex-workspace/agent-dotfiles/skills/finance/dayu \
  ~/Documents/codex-workspace/agent-dotfiles/skills/finance/dayu-installation
```

Patch the sibling `dayu` skill when research commands or workflow semantics changed. Patch this installation skill when setup, update, init, executable discovery, or render verification changed.

## Init and provider refresh

Some releases add or change provider setup. If release notes say a provider requires rerunning init, make the init mode explicit and protect existing config.

Overwrite refresh:

```bash
dayu-cli init --base ~/.dayu/workspace --overwrite
```

Reset refresh:

```bash
dayu-cli init --base ~/.dayu/workspace --reset
```

Only run overwrite or reset when release notes require it or the user wants that refresh. `--reset` is stronger because it rebuilds generated `.dayu`, `config`, and `assets` directories. If the provider is OpenAI-compatible and init does not produce the desired config, continue with [openai_compatible_provider.md](openai_compatible_provider.md).

Current version-specific note:

- Dayu `v0.1.4` adds A-share and Hong Kong native filing download and Web interactive analysis. From `v0.1.3`, release notes say to run `dayu-cli init` after updating. From earlier versions, including `v0.1.2`, release notes say to run `dayu-cli init --reset`.
- Dayu `v0.1.2` says MiMo Plan overseas support requires rerunning `dayu-cli init --overwrite` when staying on that release line.

## Offline packages

Dayu `v0.1.4` publishes offline packages for macOS ARM64, macOS x64, and Windows x64. Linux users should use the online wheel or source install according to the release notes. Treat offline packages as a fallback when network wheel installation is not viable. The preferred local agent setup remains `uv tool install` from the release wheel, because it keeps `dayu-cli`, `dayu-render`, `dayu-web`, and `dayu-wechat` in the normal `uv` tool inventory.

When a newer release changes the offline package matrix, update this section and remove stale platform claims.

## Web UI audit

Dayu `v0.1.4` installs a `dayu-web` executable. In the audited `uv tool install` environment, invoking `dayu-web --help` failed because `streamlit` was not installed by the wheel dependency set. Treat `dayu-web` as optional during CLI setup verification unless a later release fixes the dependency or the user explicitly needs the Web UI.

## Script boundary

Keep `dayu_install_or_update.sh` as one script while install and update share the same mechanics: detect `uv`, ensure managed Python, resolve a release wheel, install the uv tool, verify executables, optionally run init.

Split only if one of these becomes true:

- first install and update require materially different release resolution or Python setup
- offline install becomes a first-class path with separate inputs and verification
- the script grows separate interactive provider-migration behavior beyond `dayu-cli init`
- shared helpers can be moved into a small library without making normal usage harder

If split, prefer thin entrypoint scripts such as `dayu_install.sh` and `dayu_update.sh` over duplicating helper logic.

## Verification

A complete update has:

- `uv tool list --show-version-specifiers --show-python` showing the expected `dayu-agent` version
- doctor passing for `uv`, Python, `dayu-cli`, `dayu-render`, and workspace config
- `dayu-cli --help` and command-specific help matching documented skill workflows
- `dayu-render` returning usage text when invoked without arguments
- no stale documented command examples from older releases

In the final response, include the old version, new version, install command, whether init was skipped or run, CLI audit result, and the skill files updated.
