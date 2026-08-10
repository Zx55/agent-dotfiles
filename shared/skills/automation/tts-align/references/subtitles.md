# Subtitle Generation From Timed Narration

This reference is for the optional case where the user already has timed narration and asks for subtitle files, a soft-subtitle video, or a hard-subtitle preview. The main purpose of `tts-align` remains timing and narration/video QA.

## Inputs

- MLX Whisper JSON with word timestamps.
- Final script text used for narration. Prefer this text over raw ASR text.
- Optional video file for visual placement and burn-in QA.
- Optional existing no-subtitle base video. If the current only available video already has burned subtitles, regenerate or request a clean base before burning a new subtitle layer.

## Subtitle Text And Timing

1. Treat the final script as authoritative subtitle text.
2. Use MLX Whisper word timestamps as the timing source.
3. Align script tokens to timed ASR words by normalized text, then interpolate small unmatched gaps.
4. Split captions for readability.
   - Prefer one-line captions for slide or poster videos.
   - Keep each caption short enough to avoid wrapping.
   - Use more, shorter cues instead of tall two-line boxes when the video has a narrow subtitle band.
5. Export at least `.srt`. Export `.vtt` when browser or web-video playback is useful.

MLX Whisper timestamps come from Whisper attention alignment rather than an external forced-alignment model. Verify exact editorial cuts against the rendered narration.

## Video Placement

If a video is provided, inspect frames before choosing subtitle placement.

1. Extract representative frames across the whole video and around known visually dense sections.
2. Build a contact sheet and identify consistently empty regions.
3. Prefer a fixed subtitle region for the entire video. Do not let subtitles jump up and down based on caption length.
4. Fix both vertical position and box height. Center text inside that fixed box.
5. If the empty region is narrow, reduce font size and force shorter one-line captions.
6. If no consistently safe region exists, or if the safe region is too small for legible subtitles, tell the user and recommend soft subtitles or a layout change.

For slide videos with a reserved subtitle strip near the bottom, place subtitles in that strip with a small fixed bottom margin. Verify that the subtitle box does not cover important figures, labels, or slide text.

## Hard Subtitle Workflow

Use this workflow when `ffmpeg` lacks `subtitles` or `drawtext`, or when more deterministic placement is needed.

1. Generate `.srt` from the timing JSON and final script.
2. Render each subtitle cue as a transparent PNG with Python and Pillow.
   - Use a fixed canvas size matching the video.
   - Draw a semi-transparent background box.
   - Keep the box at a fixed `y` coordinate.
   - Use a fixed box height and center text vertically.
3. Create a transparent overlay video from the PNG sequence or a concat file.
   - `qtrle` in a `.mov` container preserves alpha well for this local workflow.
4. Overlay the subtitle video on the clean base video with `ffmpeg`.

Example overlay command:

```bash
ffmpeg -y \
  -i base-video.mp4 \
  -i subtitles-overlay.mov \
  -filter_complex '[0:v][1:v]overlay=0:0:format=auto,fps=30,format=yuv420p[v]' \
  -map '[v]' -map 0:a \
  -c:v libx264 -preset medium -crf 18 \
  -c:a copy -movflags +faststart -shortest \
  output-hardsub.mp4
```

Soft subtitles are useful as an editable companion artifact:

```bash
ffmpeg -y \
  -i base-video.mp4 \
  -i narration.srt \
  -map 0:v -map 0:a -map 1:0 \
  -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=eng \
  output-softsub.mp4
```

## QA Checklist

After generating subtitle artifacts:

- Confirm `.srt` or `.vtt` exists and has plausible cue count.
- Confirm the output video has the expected duration and audio/video streams.
- Extract frames from:
  - the first narrated section,
  - dense visual pages,
  - the case-study or demo section,
  - the conclusion section.
- Build a contact sheet and inspect it visually.
- Check that subtitle position is fixed across cues.
- Check that subtitles do not cover important content.
- Check that captions do not wrap unexpectedly unless the chosen layout explicitly allows two lines.

If any representative frame fails the placement check, adjust font size, cue length, box height, or fixed `y` position, then regenerate the hard-subtitle video and QA frames.
