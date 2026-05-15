# Project Initialization

This workflow accepts three forms:

```text
$overleaf <path-to-local-git-repo>
$overleaf <project-id>
$overleaf <git clone https://git@git.overleaf.com/<project-id>>
```

## Local Repo Input

If the user gives a path:

1. Resolve the path.
2. Confirm it is a Git repo with `git -C <path> rev-parse --show-toplevel`.
3. Inspect remotes with `git -C <path> remote -v`.
4. Treat it as an Overleaf repo only if a remote points to `git.overleaf.com`.
5. Continue with the mandatory preflight in `overleaf-git.md`.

Do not clone again when a valid local Overleaf repo is already provided.

## Project Id Or Clone Command Input

If the user gives a project id, accept either the bare id or a copied command like:

```bash
git clone https://git@git.overleaf.com/<project-id>
```

Extract `<project-id>` from the command. The project id is the path segment after `git.overleaf.com/`.

Before cloning, check whether the shell environment has the token:

```bash
test -n "$OVERLEAF_GIT_TOKEN" && echo present || echo missing
```

Do not print, log, or echo the token value. It is enough to know whether the variable is present.

If `OVERLEAF_GIT_TOKEN` is missing, stop and tell the user to generate an Overleaf Git authentication token and set the variable. Link the official docs:

https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/git-integration/git-integration-authentication-tokens#step-by-step-how-to-clone-a-project-using-overleaf-git-authentication-tokens

## Clone Rule

When cloning with `OVERLEAF_GIT_TOKEN`, avoid leaving the token in the saved remote URL. After clone, ensure the remote is token-free:

```bash
git clone "https://git:${OVERLEAF_GIT_TOKEN}@git.overleaf.com/<project-id>" <project-id>
git -C <project-id> remote set-url origin https://git@git.overleaf.com/<project-id>
```

Do not paste this command into chat with a real token expanded. Prefer running it locally from a shell where `OVERLEAF_GIT_TOKEN` is already set.

If already inside the cloned repo, set the token-free remote URL with:

```bash
git remote set-url origin https://git@git.overleaf.com/<project-id>
```

Then verify:

```bash
git remote -v
```

The remote should look like:

```text
origin  https://git@git.overleaf.com/<project-id> (fetch)
origin  https://git@git.overleaf.com/<project-id> (push)
```

If credentials are needed later, rely on the user's Git credential helper, keychain, or `OVERLEAF_GIT_TOKEN` workflow. Never write the token into project files.

## Missing Input

If the user invokes `$overleaf` with no project id, clone command, or local repo path, ask them to provide one of those inputs. Point them to the official authentication-token cloning instructions above.
