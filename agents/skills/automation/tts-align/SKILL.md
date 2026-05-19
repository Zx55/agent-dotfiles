---
name: tts-align
description: Align fixed narration audio against its script with WhisperX, produce sentence or word timestamps, and compare narration sections against video clips for companion videos, presentations, demos, and TTS QA.
---

# TTS Align

Use this skill when a user needs timing for an existing narration audio file, especially after `$tts-gen`, or wants to check whether a narration section matches a silent video, slide animation, or demo clip.

## Workflow

1. Resolve inputs.
   - Required: narration audio, usually `.wav`.
   - Recommended: final script `.txt` used to synthesize the narration.
   - Optional: video clip to compare against a section of the narration.
2. Check whether WhisperX is available.
   - First try `command -v whisperx` and `whisperx --help`.
   - If it is not available or model caches are missing, read `references/installation.md`.
   - Do not assume the user's bootstrap has already installed the tool.
3. Run WhisperX for timestamps.
   - Prefer CPU for short narration under roughly 10 minutes. On macOS, WhisperX is generally more reliable on CPU than Metal/MPS.
   - Use `tiny` or `small` for timing QA. Use larger models only when recognition errors affect the target section.
   - Keep model caches in normal global locations. Do not point model downloads at project `tmp/` unless the user explicitly wants disposable cache.
4. Compare timing.
   - For global timing, use wav duration and total script words only as a rough estimate.
   - For section timing, prefer WhisperX `json` output and marker phrases from the script.
   - For video sync, compare section start/end times against `ffprobe` video duration and keyframe inspection.
5. Report actionable adjustments.
   - If narration is longer than the clip, suggest shortening text or increasing speech rate only if provider controls support it.
   - If narration is shorter than the clip, suggest adding a pause, adding explanatory words, or delaying the visual transition.
   - For internal mismatch, redistribute words across subsegments instead of only matching total section duration.

## WhisperX Command

After confirming `whisperx` is on `PATH`, run:

```bash
whisperx narration.wav \
  --model tiny \
  --language en \
  --device cpu \
  --compute_type int8 \
  --vad_method silero \
  --output_dir output/align \
  --output_format json \
  --print_progress False
```

If `whisperx` is missing, broken, or blocked by missing model caches, read `references/installation.md` before trying to install or prewarm anything.

## Helper Script

Use `scripts/section_timing.py` when you have a WhisperX JSON and want marker-based section timing:

```bash
python scripts/section_timing.py \
  --json output/align/narration.json \
  --start "Now let us walk through one representative case study" \
  --end "To conclude"
```

The script estimates marker timestamps from aligned words when available, and falls back to segment interpolation when only segment timestamps are present.

## Boundaries

- This skill aligns existing audio. It does not generate TTS audio. Use `$tts-gen` for synthesis.
- This skill can inspect video duration and frames, but it does not edit video or build a final deck.
- Word-level timestamps are only as good as WhisperX alignment. For exact editorial timing, verify with the rendered audio/video preview.
