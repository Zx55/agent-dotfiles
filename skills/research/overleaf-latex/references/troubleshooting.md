# Troubleshooting

## Token Or Authentication Fails

Check that `OVERLEAF_GIT_TOKEN` exists without printing the token:

```bash
test -n "$OVERLEAF_GIT_TOKEN" && echo present || echo missing
```

If missing, ask the user to generate an Overleaf Git authentication token and set the variable.

If authentication still fails, ask the user to confirm the token was generated for Overleaf Git integration and that the project id is correct.

## Pull Fails

Run:

```bash
git status --short --branch
git remote -v
```

If local changes exist, do not overwrite them. Report the conflict and ask whether to commit, stash, or inspect. Do not run destructive reset unless explicitly requested.

## Push Rejected

Pull first:

```bash
git pull origin master
```

If conflicts appear, stop and report the conflicted files. Resolve only with user approval or when the requested edit clearly implies the resolution.

## Browser Does Not Show Pushed Changes

After a successful push, refresh the Overleaf browser tab. If the tab warns about remote changes, follow the UI prompt. If the browser still differs, run `git log --oneline -5` locally and verify the pushed commit exists in Overleaf after refresh.

## Local Compile Missing Tools

If `latexmk` or `pdflatex` is not found, local compile cannot run. First check whether this is only a PATH issue:

```bash
eval "$(/usr/libexec/path_helper)"
which latexmk
which pdflatex
```

If the tools are still missing, check whether TeX Live exists in its versioned install directory:

```bash
find /usr/local/texlive -maxdepth 3 -type d -path '*/bin/universal-darwin' -print
```

The helper script adds the newest matching directory to `PATH` for its own checks. The user's interactive shell may still need PATH setup.

If no versioned TeX Live bin directory exists, TeX Live is probably not installed. Read `latex-installation.md` and follow its `mactex-no-gui` installation workflow.

## Install Fails Or Does Not Finish

If `brew install --cask mactex-no-gui` fails with `sudo: a terminal is required to read the password`, ask the user to rerun the install command in their own terminal with proxy enabled if needed, enter the administrator password, and wait for the installer to finish. Never ask the user to paste the administrator password into chat.

If Homebrew reports `mactex-no-gui` is installed but TeX Live tools are still missing, the previous package installer may have been interrupted after Homebrew recorded the cask as installed. Do not try to repair it with ad hoc package commands. Ask the user to uninstall and reinstall from their own terminal:

```bash
brew uninstall --cask mactex-no-gui
brew install --cask mactex-no-gui
```

During reinstall, enter the administrator password if prompted and wait for the installer to finish. It can appear quiet for 5-10 minutes. If Homebrew itself reports permission or ownership errors, tell the user to follow Homebrew's printed repair instructions in their own terminal before retrying. Do not run `sudo -S` or ask the user to paste the administrator password into chat.

## Local Compile Passes But Overleaf Fails

Treat Overleaf as authoritative. Check:

- Overleaf compiler is `pdfLaTeX` unless the user says otherwise.
- Overleaf TeX Live version is `2025` unless the user says otherwise.
- Local TeX Live may be newer than Overleaf. TeX Live `>= 2025` is acceptable for fast local checks, while Overleaf compile remains authoritative for exact cloud parity.
- File case sensitivity and paths match exactly.
- Generated files are not accidentally required by local build but missing from Git.
- Bibliography files and figure assets are committed.

Use browser automation to inspect the Overleaf compile log when needed.

## Overleaf Compile Passes But Local Fails

Check the local TeX distribution and package availability. If local parity is not required for the task, proceed with Overleaf browser verification and report that local compile could not be used.
