# MiMo V2.5 TTS Reference

Source: official MiMo documentation, "Speech synthesis (MiMo-V2.5-TTS Series)", https://platform.xiaomimimo.com/docs/en-US/usage-guide/speech-synthesis-v2.5

This reference documents MiMo-specific behavior for the `tts-gen` script. Do not assume these controls apply to every TTS provider.

## Refreshing the Official Documentation

The MiMo documentation site may render the page content through JavaScript. If the public page appears mostly empty in a terminal fetch, inspect the loaded static JavaScript chunks and search them for the current TTS page title or model name.

Useful search terms:

```text
Speech synthesis
mimo-v2.5-tts
MiMo-V2.5-TTS
chat/completions
message.audio.data
```

When updating this reference for a new model version, verify the endpoint, model names, message placement, audio response shape, output formats, and whether style or tag controls still use the same convention.

## Models

- `mimo-v2.5-tts`: built-in voices. This is the default model for `tts-gen`.
- `mimo-v2.5-tts-voicedesign`: voice generated from text description. The user-role instruction is required.
- `mimo-v2.5-tts-voiceclone`: voice cloned from an audio sample. This is outside the default `tts-gen` workflow.

## OpenAI-Compatible Chat-Audio Shape

MiMo exposes speech synthesis through chat completions, not the standard OpenAI `audio.speech` endpoint.

The official examples use:

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://api.xiaomimimo.com/v1",
)

completion = client.chat.completions.create(
    model="mimo-v2.5-tts",
    messages=[
        {"role": "user", "content": "Clear, calm narration with moderate pacing."},
        {"role": "assistant", "content": "Text to synthesize."},
    ],
    audio={"format": "wav", "voice": "Chloe"},
)
```

For the current `tts-gen` script, equivalent values come from:

- `TTS_GEN_API_KEY`
- `TTS_GEN_BASE_URL`
- `TTS_GEN_MODEL`

## Built-In Voice Selection

MiMo V2.5 TTS built-in voices are language-specific:

| Voice ID | Language | Gender |
| --- | --- | --- |
| `冰糖` | Chinese | Female |
| `茉莉` | Chinese | Female |
| `苏打` | Chinese | Male |
| `白桦` | Chinese | Male |
| `Mia` | English | Female |
| `Chloe` | English | Female |
| `Milo` | English | Male |
| `Dean` | English | Male |

The documented default voice ID is `mimo_default`. Its resolved voice depends on the deployed cluster. The China cluster defaults to `冰糖`, while other clusters default to `Mia`.

`tts-gen` uses this priority for the current MiMo provider:

1. User-specified `--voice`.
2. Agent-selected voice when the user's language, gender, or style request makes the choice clear.
3. Script fallback to `mimo_default`.

For Chinese-dominant text with a few English terms, prefer a Chinese voice and refine English acronyms or terms for pronunciation. For English-dominant text with a few Chinese names or terms, prefer an English voice and add pronunciation hints only when useful. For balanced or quality-sensitive bilingual narration, split the script into language-dominant segments and synthesize each segment with a suitable voice.

Do not treat voice names as provider-agnostic. They are MiMo-specific until another provider documents compatible names and behavior.

## Message Placement

- Put the text to be synthesized in the `assistant` message content.
- Put style, tone, pacing, and delivery instructions in the optional `user` message content.
- The `user` message is not spoken.
- For `mimo-v2.5-tts-voicedesign`, the `user` message is required.

## Audio Parameters

For built-in voices:

```json
{
  "audio": {
    "format": "wav",
    "voice": "mimo_default"
  }
}
```

The documentation also shows `pcm16` for streaming. `tts-gen` intentionally does not use streaming.

When `--voice` is omitted, the bundled script passes `mimo_default` as a deterministic MiMo fallback. The agent should still pass an explicit voice when the user asks for one or when language/style requirements make the choice clear.

## Natural Language Style Control

MiMo supports natural language instructions in the `user` message. Useful dimensions include:

- speaking speed
- breath control
- pauses
- accents
- resonance position
- timbre texture
- emotional fluctuation

For academic or professional narration, prefer restrained instructions such as:

```text
Clear academic narration, calm and confident, moderate pace, brief pauses between sections, avoid dramatic emotion.
```

## Tag and Pause Control

MiMo supports provider-specific tags and stage-direction-like text in the `assistant` content for fine-grained control. The documentation describes inserting audio tags to control tone, mood, expression, breathing sounds, pauses, coughs, and speaking speed.

Examples in the documentation include phrases such as:

```text
If I had... (pauses for a moment) even if I had persisted for just one more second...
```

Use these sparingly. For general narration, punctuation and concise natural language style instructions are usually safer than heavy tag usage.
