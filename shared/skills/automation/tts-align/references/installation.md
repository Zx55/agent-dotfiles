# TTS Align Installation

Use this reference only when the uv-managed MLX Whisper tool is unavailable, broken, or missing model caches.

## Tool Install

Install or upgrade the global tool with uv:

```bash
uv tool install --upgrade mlx-whisper
```

The expected entrypoint is:

```text
~/.local/bin/mlx_whisper
```

Do not install MLX Whisper into the shared agent Python environment.

## Model Cache Prewarm

Use the bootstrap model warmer when this dotfiles repo is available:

```bash
~/Documents/agent-dotfiles/master/bootstrap/scripts/warm_ml_models.sh
```

The model list lives at:

```text
~/Documents/agent-dotfiles/master/bootstrap/packages/ml-models.tsv
```

For a manual prewarm, use the Hugging Face CLI from the shared agent Python environment:

```bash
~/.local/share/agent-dotfiles/python/bin/hf download mlx-community/whisper-tiny
~/.local/share/agent-dotfiles/python/bin/hf download mlx-community/whisper-small-mlx
```

If Hugging Face Xet returns a CAS authorization error, retry the same command with `HF_HUB_DISABLE_XET=1`.

## Verification

Check the CLI:

```bash
~/.local/bin/mlx_whisper --help
```

Run a small word-timestamp job:

```bash
python scripts/transcribe.py narration.wav \
  --output-dir output/align \
  --model mlx-community/whisper-tiny \
  --language en \
  --timing word
```

Validate that the resulting JSON contains non-empty `segments` and that timed words contain `word`, `start`, `end`, and `probability`.

## Runtime Requirements

MLX Whisper requires an Apple Silicon Mac with Metal access.
