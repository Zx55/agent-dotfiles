---
name: bilibili-video-summary
description: Download and summarize individual Bilibili videos by extracting audio, producing MLX Whisper timestamped transcripts, optionally generating word timestamps and collecting evidence screenshots, writing a source-grounded summary, and deleting only raw media created by the run after validation.
---

# Bilibili Video Summary

Process one Bilibili video into durable metadata, a timestamped transcript, optional evidence screenshots, and a grounded summary. Keep semantic decisions in the agent and use the bundled scripts for deterministic media operations.

## Workflow

1. Resolve one video URL and an output run directory.
   - Default to `output/bilibili/<BV_ID>/` under the current project when the user does not specify a destination.
   - Treat playlists, an UP's full archive, and cross-video idea distillation as separate higher-level workflows.
2. Download metadata and audio first.

```bash
python scripts/download.py URL \
  --run-dir RUN_DIR \
  --audio
```

   - Add `--section 0-90` only for explicit sampling or workflow tests.
   - Use `--cookies-from-browser BROWSER` only when the public format is unavailable and the user authorizes access to their logged-in browser state.
3. Transcribe with MLX Whisper segment timestamps by default.

```bash
python scripts/transcribe.py RUN_DIR \
  --language zh \
  --model mlx-community/whisper-small-mlx
```

   - Add `--word-timestamps` only when a sentence must be matched precisely to a changing frame, subtitle timing is requested, or segment timing is demonstrably too coarse.
   - The script invokes only the uv-managed global entrypoint at `~/.local/bin/mlx_whisper`.
   - MLX Whisper requires an Apple Silicon Mac with Metal access.
   - Do not treat `$tts-align` or its private helper scripts as a runtime dependency. Use `$tts-align` separately only for fixed-script narration QA.
4. Read `transcript/transcript.json` and decide whether the argument depends on the image.
   - Download video when the speaker refers to a chart, table, filing, slide, portfolio, product screen, code, physical object, or phrases such as “看这里”, “这张图”, or “这个数据”.
   - Skip video for ordinary talking-head or voice-only sections whose claims are complete in speech.
5. If visual evidence is needed, download a bounded-quality playable video.

```bash
python scripts/download.py URL \
  --run-dir RUN_DIR \
  --video \
  --max-height 720
```

6. Create `frame-requests.json` from the transcript, then extract screenshots.
   - Include only timestamps with a concrete visual reason.
   - Prefer the middle of the relevant utterance when segment timing is sufficient.
   - See `references/output-schema.md` for the request format.

```bash
python scripts/extract_frames.py RUN_DIR \
  --requests RUN_DIR/frame-requests.json
```

   - The script adjusts requests to nearby scene cuts and removes near-duplicate images.
   - Inspect every retained frame before using it as evidence.
7. Write `summary.md`.
   - Identify the source video, author, BV ID, and publication metadata.
   - Separate the speaker's claims, supporting evidence, and the agent's inference.
   - Attach transcript timestamps to material claims.
   - Attach frame IDs when the evidence comes from the image.
   - Mark uncertain ASR, unreadable visuals, missing context, and claims that cannot be verified from the video.
   - Do not infer an UP's stable worldview from one video.
8. Validate durable outputs and clean up.

```bash
python scripts/finalize.py RUN_DIR --delete-media
```

   - Run finalization only after `summary.md` is complete and all retained screenshots have been inspected.
   - If any stage fails, preserve the run directory and report the failure and path.

## Safety Boundaries

- Download only the video placed in scope by the user. Do not expand to playlists or an UP's archive without explicit scope.
- Do not redistribute downloaded media.
- Delete only manifest-owned artifacts marked ephemeral under `RUN_DIR/raw/`.
- Never delete a user-provided local video or audio file.
- Keep metadata, transcripts, selected screenshots, manifests, and summaries after successful cleanup.
- Treat summaries of finance, medicine, law, or other high-stakes content as analysis of the speaker's claims, not verified professional advice.
- Do not silently switch to another ASR backend when Metal is unavailable.
