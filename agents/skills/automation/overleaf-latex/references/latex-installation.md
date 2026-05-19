# LaTeX Installation And Compile Alignment

Default Overleaf target for this user's workflow:

- Compiler: `pdfLaTeX`
- TeX Live version: `2025`
- Local macOS distribution preference: `mactex-no-gui`

`mactex-no-gui` is the Homebrew cask for a full TeX Live distribution without GUI applications. It includes TeX engines, common packages, fonts, BibTeX/Biber tools, and `latexmk`. It is still large, but it best approximates Overleaf compared with smaller local installs. Homebrew normally installs the latest version, so the local TeX Live year may be newer than the Overleaf project target. Treat TeX Live `>= 2025` as acceptable for local checks.

## Tool Relationship

- TeX Live is the full LaTeX toolchain and package distribution.
- MacTeX is TeX Live packaged for macOS. `mactex-no-gui` installs the TeX Live toolchain without GUI apps.
- `pdflatex` is the compiler engine.
- `latexmk` is the build orchestrator that runs `pdflatex`, BibTeX or Biber, and additional passes as needed.

Prefer `latexmk` over manual repeated `pdflatex` runs.

## Check Local Tools

Prefer the bundled helper script:

```bash
./scripts/install-mactex-no-gui.sh --check
```

From outside the skill directory, use the script by absolute path.

Manual equivalent:

```bash
which latexmk
which pdflatex
which xelatex
which lualatex
```

If `latexmk` or `pdflatex` is missing, local compile verification is unavailable until `mactex-no-gui` or another TeX Live distribution is installed.

## Install Guidance

Do not install `mactex-no-gui` without user approval. It is a large system-level installation.

Preferred scripted installation:

```bash
./scripts/install-mactex-no-gui.sh --install
```

The script installs `mactex-no-gui` through Homebrew with:

```bash
brew install --cask mactex-no-gui
```

The installation may invoke macOS `sudo installer`. If the agent is running in a non-interactive command session and the installer asks for an administrator password, stop and ask the user to run the same script in their own terminal. Do not ask the user to paste their password into chat. When running interactively, enter the password and wait for the installer to finish. Do not interrupt it just because it appears quiet.

Manual user-facing option:

- Install MacTeX or MacTeX-no-GUI from https://www.tug.org/mactex/
- Restart the shell or ensure TeX binaries are on `PATH`.
- Recheck `latexmk` and `pdflatex`.

If a smaller installation is explicitly preferred, BasicTeX may be used, but expect missing packages. For Overleaf parity without GUI applications, `mactex-no-gui` is the default recommendation.

Homebrew may install the latest `mactex-no-gui`, whose TeX Live version can be newer than the Overleaf project default. The helper script accepts local TeX Live `>= 2025` by default. A newer local version is acceptable for fast checks, but Overleaf compile remains the final authority for exact cloud parity.

If `/Library/TeX/texbin` is missing or not on `PATH`, MacTeX binaries may still exist under a versioned directory such as `/usr/local/texlive/2026/bin/universal-darwin`. The helper script checks this fallback path.

If the project target differs from the default TeX Live 2025, set it when checking:

```bash
OVERLEAF_TEXLIVE_VERSION=2026 ./scripts/install-mactex-no-gui.sh --check
```

## Compile Commands

For the default compiler:

```bash
latexmk -pdf <entrypoint>.tex
```

For explicit non-default compilers:

```bash
latexmk -xelatex <entrypoint>.tex
latexmk -lualatex <entrypoint>.tex
```

Run from the repo root unless the project clearly expects another working directory.

Compilation can create auxiliary files near the source tree. After compiling, run `git status --short` and keep generated build artifacts out of commits unless they are already tracked or explicitly requested.

## Entrypoint Discovery

Find candidate entrypoints:

```bash
rg -n -F '\\documentclass' -g '*.tex'
```

If multiple entrypoints exist, choose the one matching the user's target artifact. If unclear, ask.

## Verification Authority

Local compilation is a fast check, not the final source of truth. Local TeX Live `>= 2025` is acceptable for routine checks. When exact cloud parity matters, local compilation is advisory unless the local TeX Live year matches the Overleaf project. If local output and Overleaf output disagree, Overleaf compile wins. Use browser automation to compile on Overleaf when local parity is uncertain or when the user asks for cloud verification.
