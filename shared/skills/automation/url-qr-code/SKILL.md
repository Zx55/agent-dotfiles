---
name: url-qr-code
description: Generate local QR codes from URLs with offline validation. Use when needing to turn a URL or web link into a PNG or SVG QR code, verify that the QR decodes back to the intended URL.
---

# URL QR Code

## Prerequisites

- Install Python packages in the shared agent Python environment: `~/.local/share/agent-dotfiles/python/bin/python -m pip install segno Pillow`
- Install local decoder: `brew install zbar`
- Check decoder availability: `command -v zbarimg`

## Workflow

1. Normalize the input URL before generation.
   - Trim surrounding whitespace.
   - If no scheme is present, add `https://`.
   - Accept only `http://` and `https://`.
   - Reject URLs without a host.

2. Generate the QR code with `scripts/make_qr.py`.
   - Default output format is PNG.
   - Use `--format svg` or a `.svg` output path for SVG.

3. Validate by default.
   - Decode the generated PNG with `zbarimg --raw`.
   - For SVG output, render a temporary PNG from the same QR matrix and decode that temporary PNG.
   - Compare the decoded text exactly with the normalized URL.
   - If `zbarimg` is unavailable, report that validation was skipped. Use `--strict-validate` when missing validation must fail.

4. Report the normalized URL, output path, format, and validation status.

## Commands

Generate and validate a PNG:

```bash
~/.local/share/agent-dotfiles/python/bin/python scripts/make_qr.py "example.com" --out example-qr.png
```

Generate and validate SVG content through a temporary PNG:

```bash
~/.local/share/agent-dotfiles/python/bin/python scripts/make_qr.py "https://example.com/path" --out example-qr.svg
```

Require validation to succeed:

```bash
~/.local/share/agent-dotfiles/python/bin/python scripts/make_qr.py "https://example.com" --out example-qr.png --strict-validate
```

Skip validation only when the user explicitly requests it:

```bash
~/.local/share/agent-dotfiles/python/bin/python scripts/make_qr.py "https://example.com" --out example-qr.png --no-validate
```

## Notes

- The generated QR encodes the normalized URL exactly.
- This skill does not upload URLs to any external service.
- Keep output files in the current task workspace unless the user requests another destination.
