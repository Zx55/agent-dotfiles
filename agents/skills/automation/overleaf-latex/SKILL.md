---
name: overleaf-latex
description: Work with Overleaf LaTeX projects through Overleaf Git clones. Use when the user invokes $overleaf, provides an Overleaf project id, Overleaf Git clone command, or local Overleaf Git repo, or asks to edit, verify, pull, push, initialize, compile, or troubleshoot an Overleaf LaTeX project.
---

# Overleaf LaTeX

Use this skill for Overleaf projects accessed through Overleaf Git integration. The primary artifact is a local Git clone of an Overleaf project. Browser automation is only a fallback for Overleaf UI state, compile verification, or project management that Git cannot represent.

## Default Assumptions

- Default compiler: `pdfLaTeX`.
- Default Overleaf TeX Live target: `2025`.
- Preferred local distribution on macOS: `mactex-no-gui` with TeX Live `>= 2025`.
- Preferred local compile command: `latexmk -pdf <entrypoint>.tex`.
- Token environment variable: `OVERLEAF_GIT_TOKEN`.
- Remote branch: `master`, unless the actual repo proves otherwise.

Override the Overleaf compiler or TeX Live target only when the user says the project uses different settings, or when project files clearly encode another setting. Local TeX Live `>= 2025` is acceptable for fast checks. When exact cloud parity matters, treat local compilation as advisory unless the local TeX Live year matches the Overleaf project, and use Overleaf compile as the final authority.

## Route By Task

- Initialization, `$overleaf <project-id>`, `$overleaf <git clone ...>`, or `$overleaf <path>`: read `references/project-initialization.md`.
- Git workflow, pull/edit/push rules, supported operations, or Overleaf Git limitations: read `references/overleaf-git.md`.
- Installing or checking local LaTeX tools, compiler selection, or local compile commands: read `references/latex-installation.md`.
- Compile failures, Git errors, token problems, stale browser state, or sync confusion: read `references/troubleshooting.md`.

## Required Work Discipline

Before editing any Overleaf project, establish the intended local repo and run the mandatory Git preflight from `references/overleaf-git.md`.

Never silently edit without a fresh `git pull` and clean status check. Never push without reviewing the final diff and confirming there are no conflicts or unexpected local changes.

Keep changes surgical. For paper work, edit only the relevant `.tex`, `.bib`, figure, or style files. Preserve the current project organization instead of imposing a generic layout.

## Project Discovery

Do not assume a fixed structure. Discover entrypoints and supporting files first:

- Find candidate entrypoints by searching for `\documentclass`.
- Prefer likely root files such as `main.tex`, `paper.tex`, `arxiv.tex`, `appendix.tex` or `supp.tex`.
- Identify included section trees such as `sections/` and `figures/`.
- Identify shared files such as `preamble.tex`, `math_commands.tex`, `macros.tex`, `.bib` files, `.bst` files, and local class or style files.

If multiple entrypoints are plausible and the user did not specify which artifact to work on, state the candidates and ask for the intended target.

## Verification

Use local compilation when TeX tools are installed and the relevant entrypoint is known. If local tools are unavailable, or if Overleaf and local output disagree, treat Overleaf compile as the final authority and use browser automation as needed.

Report exactly what was verified. Distinguish local checks from Overleaf browser checks.
