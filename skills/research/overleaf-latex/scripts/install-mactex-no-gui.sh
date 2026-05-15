#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage:
  install-mactex-no-gui.sh --check
  install-mactex-no-gui.sh --install

Purpose:
  Check or install the local LaTeX toolchain preferred for Overleaf parity.

Defaults:
  Distribution: mactex-no-gui
  Compiler: pdfLaTeX
  Minimum local TeX Live version: ${OVERLEAF_TEXLIVE_VERSION:-2025}

Notes:
  --check does not install anything.
  --install uses Homebrew: brew install --cask mactex-no-gui
  mactex-no-gui is large and may require administrator approval.
EOF
}

mode="${1:---check}"
expected_texlive_version="${OVERLEAF_TEXLIVE_VERSION:-2025}"

if [[ "$mode" != "--check" && "$mode" != "--install" && "$mode" != "-h" && "$mode" != "--help" ]]; then
  usage >&2
  exit 2
fi

if [[ "$mode" == "-h" || "$mode" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This helper currently supports macOS only." >&2
  exit 1
fi

ensure_tex_path() {
  case ":${PATH}:" in
    *":/Library/TeX/texbin:"*) ;;
    *) export PATH="/Library/TeX/texbin:${PATH}" ;;
  esac

  local texlive_bin
  texlive_bin="$(
    find /usr/local/texlive -maxdepth 3 -type d -path '*/bin/universal-darwin' 2>/dev/null \
      | sort -r \
      | head -n 1
  )"
  if [[ -n "$texlive_bin" ]]; then
    case ":${PATH}:" in
      *":${texlive_bin}:"*) ;;
      *) export PATH="${texlive_bin}:${PATH}" ;;
    esac
  fi
}

tool_path() {
  command -v "$1" 2>/dev/null || true
}

print_status() {
  ensure_tex_path

  local latexmk_path pdflatex_path texlive_line texlive_year
  latexmk_path="$(tool_path latexmk)"
  pdflatex_path="$(tool_path pdflatex)"

  echo "latexmk: ${latexmk_path:-missing}"
  echo "pdflatex: ${pdflatex_path:-missing}"

  if [[ -n "$pdflatex_path" ]]; then
    texlive_line="$(pdflatex --version | grep -Eo 'TeX Live [0-9]+' | head -n 1 || true)"
    echo "TeX Live: ${texlive_line:-unknown}"
    texlive_year="$(printf '%s\n' "$texlive_line" | grep -Eo '[0-9]+' | head -n 1 || true)"
    if [[ -n "$texlive_year" && "$texlive_year" -gt "$expected_texlive_version" ]]; then
      echo "Note: local ${texlive_line} satisfies >= TeX Live ${expected_texlive_version}; use Overleaf compile for exact cloud parity." >&2
    elif [[ -n "$texlive_year" && "$texlive_year" -lt "$expected_texlive_version" ]]; then
      echo "Warning: local ${texlive_line} is older than required TeX Live ${expected_texlive_version}." >&2
    fi
  else
    echo "TeX Live: unknown"
  fi
}

has_required_tools() {
  ensure_tex_path
  command -v latexmk >/dev/null 2>&1 && command -v pdflatex >/dev/null 2>&1
}

has_minimum_texlive_version() {
  ensure_tex_path
  local texlive_line texlive_year
  texlive_line="$(pdflatex --version 2>/dev/null | grep -Eo 'TeX Live [0-9]+' | head -n 1 || true)"
  texlive_year="$(printf '%s\n' "$texlive_line" | grep -Eo '[0-9]+' | head -n 1 || true)"
  [[ -n "$texlive_year" && "$texlive_year" -ge "$expected_texlive_version" ]]
}

if [[ "$mode" == "--check" ]]; then
  print_status
  if has_required_tools && has_minimum_texlive_version; then
    exit 0
  fi
  echo
  echo "Missing required LaTeX tools or TeX Live is older than ${expected_texlive_version}." >&2
  echo "Read references/latex-installation.md, then run with --install to install mactex-no-gui." >&2
  exit 1
fi

ensure_tex_path

if has_required_tools && has_minimum_texlive_version; then
  echo "Required LaTeX tools already exist."
  print_status
  exit 0
fi

if command -v brew >/dev/null 2>&1; then
  echo "Installing mactex-no-gui with Homebrew cask. This is a large download and may require administrator approval."
  echo "If the macOS installer asks for an administrator password, enter it and wait for the installer to finish."
  brew install --cask mactex-no-gui
else
  echo "Homebrew is required for scripted mactex-no-gui installation but was not found." >&2
  echo "Install MacTeX-no-GUI manually from https://www.tug.org/mactex/ or install Homebrew first." >&2
  exit 1
fi

echo
echo "Verifying installation..."
print_status

if ! has_required_tools || ! has_minimum_texlive_version; then
  echo "mactex-no-gui installation finished, but required tools are not on PATH or TeX Live is older than ${expected_texlive_version}." >&2
  echo "Open a new shell, run eval \"$(/usr/libexec/path_helper)\", or ensure /Library/TeX/texbin is on PATH." >&2
  exit 1
fi

echo "mactex-no-gui installation verified."
