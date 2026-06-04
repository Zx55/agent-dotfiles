# TTS Align Installation

Use this reference only when `whisperx` is unavailable, broken, or missing model caches.

## Tool Install

Prefer the shared agent Python environment:

```bash
~/.local/share/agent-dotfiles/python/bin/python -m pip install whisperx huggingface-hub
```

The Hugging Face CLI entrypoint is `hf`, not the deprecated `huggingface-cli` entrypoint:

```bash
~/.local/share/agent-dotfiles/python/bin/hf --help
```

## Model Cache Prewarm

Use the bootstrap model warmer when this dotfiles repo is available:

```bash
~/Documents/agent-dotfiles/master/bootstrap/scripts/warm_ml_models.sh
```

The model list lives at:

```text
~/Documents/agent-dotfiles/master/bootstrap/packages/ml-models.tsv
```

It separates model sources by backend:

- `hf` for Hugging Face repositories, downloaded with `hf download`.
- `torch-hub` for models loaded through `torch.hub.load`.
- `url` for direct model files downloaded to a fixed cache path.

## Manual Commands

If the bootstrap warmer is unavailable, prewarm the current WhisperX defaults manually.

Download the faster-whisper tiny ASR model:

```bash
~/.local/share/agent-dotfiles/python/bin/hf download Systran/faster-whisper-tiny
```

Warm Silero VAD through the shared agent Python when available:

```bash
~/.local/share/agent-dotfiles/python/bin/python -c \
  'import torch; torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad", trust_repo=True)'
```

Download the English wav2vec2 alignment model:

```bash
mkdir -p ~/.cache/torch/hub/checkpoints
curl -L \
  https://download.pytorch.org/torchaudio/models/wav2vec2_fairseq_base_ls960_asr_ls960.pth \
  -o ~/.cache/torch/hub/checkpoints/wav2vec2_fairseq_base_ls960_asr_ls960.pth
```

## Verification

Check the CLI and run a small alignment job:

```bash
~/.local/share/agent-dotfiles/python/bin/whisperx --help
~/.local/share/agent-dotfiles/python/bin/whisperx narration.wav \
  --model tiny \
  --language en \
  --device cpu \
  --compute_type int8 \
  --vad_method silero \
  --output_dir output/align \
  --output_format json
```

On macOS, use CPU unless there is a proven local GPU path. WhisperX is primarily designed around CUDA acceleration, and short narration alignment is usually fast enough on CPU after caches are warm.
