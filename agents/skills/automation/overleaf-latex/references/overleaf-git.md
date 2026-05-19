# Overleaf Git Workflow

Overleaf Git integration exposes an existing Overleaf project as a Git remote. It is useful for maintaining project files. It is not a complete project-management API.

Official references:

- Authentication tokens: https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/git-integration/git-integration-authentication-tokens
- Advanced Git operations: https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/git-integration/advanced-git-operations

## Mandatory Preflight

Before editing:

```bash
git pull
git status --short --branch
```

Proceed only when the pull succeeds and the status is clean or the existing changes are clearly understood and relevant to the user's request.

If there are conflicts, unexpected local edits, unexpected untracked files, or a failed pull, stop and report the state before editing.

## Edit And Verify

Use normal file editing on the local clone. Keep changes scoped to the user's request.

Before committing or pushing:

```bash
git status --short --branch
git diff --check
git diff
```

Use project-appropriate compile verification when possible. See `latex-installation.md`.

After local compilation, check status again. Do not commit generated build artifacts such as `.aux`, `.bbl`, `.blg`, `.fdb_latexmk`, `.fls`, `.log`, `.out`, `.synctex.gz`, or generated PDFs unless the project already tracks them or the user explicitly asked to update an output asset.

## Push Rule

Before push, confirm there are no conflicts or unexpected changes:

```bash
git status --short --branch
```

Then push:

```bash
git push origin master
```

After a successful push, Overleaf should receive the update. The browser editor may need a refresh or may show a remote update notice. Do not assume the open browser tab is instantly refreshed.

## Browser Edits

If the user edits in Overleaf's browser UI, they do not need to push manually. Pull before local work:

```bash
git pull origin master
```

Avoid simultaneous browser and local edits to the same lines. If the user has active browser edits, pull and inspect before making local changes.

## Supported By Git

Git can manage files inside an existing project:

- Add, edit, move, and delete source files.
- Update `.tex`, `.bib`, `.bst`, `.cls`, `.sty`, image, and PDF figure assets.
- Commit and push content changes.
- Pull changes made from the Overleaf browser UI.

## Not A Full Overleaf API

Do not use Git integration for these project-management tasks:

- Creating a new Overleaf project.
- Deleting an Overleaf project.
- Managing sharing, members, permissions, comments, track changes, or UI-only settings.
- Reliably changing compiler, main document, or TeX Live version unless Overleaf explicitly represents the setting in project files.

For those tasks, use the Overleaf UI. Browser automation may help when the user asks for it.

## Overleaf Git Limitations

Overleaf Git differs from normal Git hosting:

- The Overleaf remote history is effectively linear.
- The remote branch is `master`.
- Branching is not supported as a normal collaboration mechanism.
- Tags are not supported.
- Git LFS is not supported.
- Symlinks may be converted to regular files.
- Execute permissions are not preserved. If file mode churn appears, use `git config core.fileMode false`.
- Overleaf projects can be used as external submodules, but an Overleaf project should not contain submodules.
- Renaming or moving files in Overleaf may behave like delete plus create and can lose comments or tracked-change metadata.
- Folder renames can leave old empty folders. Split complex rename work into smaller commits.
- Frequent automated polling can hit rate limits.
- Very large pushes or many file changes can timeout. Split large updates into smaller commits.

Avoid force push, history rewriting, rebase-on-remote, and destructive reset workflows unless the user explicitly requests them and understands the risk.
