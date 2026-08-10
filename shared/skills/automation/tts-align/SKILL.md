---
name: tts-align
description: Time fixed narration audio with MLX Whisper, produce segment or word timestamps, and compare narration sections against video clips for companion videos, presentations, demos, and TTS QA.
---

# TTS Align

Use this skill when a user needs timing for an existing narration audio file, especially after `$tts-gen`, or wants to check whether a narration section matches a silent video, slide animation, or demo clip.

## Workflow

1. Resolve inputs.
   - Required: narration audio, usually `.wav`.
   - Recommended: final script `.txt` used to synthesize the narration.
   - Optional: video clip to compare against a section of the narration.
2. Check whether the global MLX Whisper tool is available.
   - Run `~/.local/bin/mlx_whisper --help`.
   - If it is unavailable or model caches are missing, read `references/installation.md`.
   - MLX Whisper requires an Apple Silicon Mac with Metal access.
3. Generate timestamps with the bundled wrapper.
   - Use `mlx-community/whisper-tiny` for short timing QA by default.
   - Use `mlx-community/whisper-small-mlx` when recognition errors affect marker phrases.
   - Keep model caches in normal global locations. Do not point model downloads at project `tmp/` unless the user explicitly wants disposable cache.
   - Use word timestamps when marker or subtitle timing is required. MLX Whisper derives them from Whisper attention alignment rather than an external forced-alignment model.
4. Compare timing.
   - For global timing, use wav duration and total script words only as a rough estimate.
   - For section timing, prefer MLX Whisper JSON with word timestamps and marker phrases from the script.
   - For video sync, compare section start/end times against `ffprobe` video duration and keyframe inspection.
5. Report actionable adjustments.
   - If narration is longer than the clip, suggest shortening text or increasing speech rate only if provider controls support it.
   - If narration is shorter than the clip, suggest adding a pause, adding explanatory words, or delaying the visual transition.
   - For internal mismatch, redistribute words across subsegments instead of only matching total section duration.
6. Optional subtitle post-processing.
   - If the user asks for subtitles after alignment, use `references/subtitles.md` as the reference workflow.
   - Keep MLX timestamps as the timing source and the final script as the subtitle text source.
   - If a video is provided, inspect frames first and place subtitles only in a consistently empty region. If no safe region exists, tell the user instead of forcing hard subtitles over important content.

## Timing Command

Use the bundled wrapper so the model, output schema, and validation remain consistent:

```bash
python scripts/transcribe.py narration.wav \
  --output-dir output/align \
  --model mlx-community/whisper-tiny \
  --language en \
  --timing word
```

For segment timestamps only, pass `--timing segment`. The wrapper invokes only the uv-managed global entrypoint at `~/.local/bin/mlx_whisper`.

## Helper Script

Use `scripts/section_timing.py` when you have MLX Whisper JSON and want marker-based section timing:

```bash
python scripts/section_timing.py \
  --json output/align/narration.json \
  --start "Now let us walk through one representative case study" \
  --end "To conclude"
```

The script uses timed words when available and falls back to interpolation within timed segments.

## Boundaries

- This skill times existing audio. It does not generate TTS audio. Use `$tts-gen` for synthesis.
- This skill can inspect video duration and frames. Subtitle generation and burn-in are optional post-processing references, not the primary responsibility of the skill.
- MLX word timestamps are attention-derived estimates. For exact editorial timing, verify with the rendered audio/video preview.
- Do not silently switch to another ASR backend when Metal is unavailable.
