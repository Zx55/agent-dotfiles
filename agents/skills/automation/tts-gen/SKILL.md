---
name: tts-gen
description: Generate fixed text-to-speech audio from raw text or text files through a configured OpenAI-compatible TTS or chat-audio provider. Use to refine narration text, prepare provider-specific speaking instructions, and synthesize an audio file without streaming.
---

# TTS Gen

Use this skill to turn text into a fixed audio file. Keep it provider-agnostic by default. The current bundled script targets OpenAI-compatible chat-audio APIs configured through environment variables.

## Workflow

1. Resolve the source text.
   - Use a user-provided `.txt` file when available.
   - Use raw prompt text when the user provides it directly.
   - If the user says the text is final or exact, preserve it and skip rewriting except for minimal formatting needed by the TTS provider.
2. Refine for narration before synthesis.
   - Preserve the meaning, terminology, names, numbers, and claims.
   - Improve spoken clarity with shorter sentences, natural punctuation, and explicit pronunciation hints only where useful.
   - Keep control tags or stage directions light. Add them only when requested or when the selected provider clearly supports them.
3. Choose synthesis settings.
   - Required environment variable: `TTS_GEN_API_KEY`.
   - Optional environment variable: `TTS_GEN_BASE_URL`. The script defaults to `https://token-plan-cn.xiaomimimo.com/v1`.
   - Optional environment variable: `TTS_GEN_MODEL`. The script defaults to `mimo-v2.5-tts`.
   - Default output format is `wav`.
   - For the current MiMo default provider, voice selection follows: user-specified `--voice`, then agent-selected voice when the language or request makes it clear, otherwise the script passes `mimo_default`.
   - Do not add provider-specific voice environment variables. Keep voice as an explicit command option or deterministic script fallback.
4. Generate the output bundle with `scripts/synthesize.py`.
   - Keep the final narration script, generated audio, and manifest together in the same task-local directory.
   - Prefer a user-specified audio output path and a matching final script path, such as `output/tts/narration.wav` and `output/tts/narration.txt`.
   - If no script path is specified, the script writes the final narration text next to the audio using the audio filename with a `.txt` suffix.
   - Do not use streaming for this skill.
5. Verify the result.
   - Confirm the audio file exists and has nonzero size.
   - Confirm the final narration `.txt` exists and matches the text sent to the TTS provider.
   - Preserve a generated manifest next to the audio for reproducibility.
   - Never print, save, or echo API keys.

## Script Usage

From the skill directory:

```bash
python3 scripts/synthesize.py \
  --input output/tts/narration.txt \
  --output output/tts/narration.wav \
  --voice Chloe \
  --style "Clear, calm narration with moderate pacing." \
  --format wav
```

For direct text:

```bash
python3 scripts/synthesize.py \
  --text "This is the text to synthesize." \
  --output output/tts/sample.wav
```

Use `--dry-run` to validate inputs and inspect the request shape without calling the provider. The script still writes the final narration `.txt` and manifest during dry runs. If `--voice` is omitted, the current script sends `mimo_default` for the MiMo default provider.

## Provider Notes

For MiMo V2.5 TTS built-in voices, style controls, message placement, and pause/tag behavior, read `references/mimo-v2.5-tts.md` when needed. Treat those controls as provider-specific unless the active provider documents the same convention.

## Boundaries

- This skill generates audio, not video.
- This skill does not perform voice cloning by default.
- This skill does not use streaming.
- This skill should not hard-code provider credentials, project-specific scripts, or one-off narration content.
