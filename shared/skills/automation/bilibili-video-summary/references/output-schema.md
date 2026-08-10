# Output Schema

## Run directory

```text
RUN_DIR/
├── .bilibili-video-summary-run
├── manifest.json
├── metadata.json
├── frame-requests.json          # only when visual evidence is needed
├── raw/
│   ├── audio.m4a                # ephemeral
│   └── video.mp4                # ephemeral and optional
├── transcript/
│   ├── transcript.json
│   └── transcript.md
├── frames/                      # optional
│   ├── frame-001-000012.345.jpg
│   └── frames.json
└── summary.md
```

`finalize.py --delete-media` removes only ready ephemeral media recorded in `manifest.json`. It retains all other files.

## Frame requests

Write `frame-requests.json` as:

```json
{
  "requests": [
    {
      "timestamp": 42.5,
      "segment_id": 3,
      "reason": "The speaker refers to the revenue table shown on screen."
    }
  ]
}
```

- `timestamp` is required and measured in seconds from the start of the downloaded video.
- `segment_id` should match the transcript segment when available.
- `reason` should state what visual information is expected and why speech alone is insufficient.

## Summary evidence

Use transcript timestamps for spoken evidence:

```markdown
- The speaker expects operating pressure to continue [00:04:12–00:04:37].
```

Add a frame ID when the image supplies material information:

```markdown
- The displayed table reports a year-over-year decline [00:05:08, frame-003].
```

Distinguish direct evidence from interpretation:

```markdown
- Speaker claim: ...
- Video evidence: ...
- Interpretation: ...
- Uncertainty: ...
```
