---
name: "gpt-image2"
description: "Generate or edit raster images through the user's local Codex image generation capability. Use when an agent outside Codex needs GPT Image 2-style concept art, mockups, product visuals, UI concepts, or reference-image edits without calling the OpenAI Images API directly."
---

# GPT Image 2 via Codex

Use this skill when the current agent cannot call an image-generation tool directly, but the user's local Codex account can. The skill delegates image generation to Codex through the Codex Python SDK and asks Codex to use its built-in `$imagegen` capability.

Codex itself should normally disable or ignore this skill and use its native `.system/imagegen` skill directly.

## Tool Path

Run:

```bash
"$HOME/.local/share/agent-dotfiles/python/bin/python" \
  "$HOME/Documents/agent-dotfiles/shared/skills/creativity/gpt-image2/scripts/codex_gpt_image2.py" \
  "<image prompt>" \
  --out "<output path>" \
  --json
```

The wrapper uses the `openai-codex` Python SDK. It does not call the OpenAI Images API directly and does not require `OPENAI_API_KEY`.

## Workflow

1. Write a concise image prompt before calling the script. Include subject, intended use, style or medium, framing, size/aspect needs, text to render verbatim, constraints, and avoid-list when relevant.
2. Choose an output path in the active project or a temp/output directory visible to the current agent.
3. Call `scripts/codex_gpt_image2.py` with `--json`.
4. Read the JSON response and verify `ok` is true, `exists` is true, and `image_path` points to the expected file.
5. Always include the generated `image_path` in the final response as the guaranteed handoff. The path is the stable cross-agent contract for this wrapper.
6. In Cursor, if the `cursor-inline-img-loader` MCP server is available, call its `load_image` tool with the generated `image_path` to return a Cursor-visible MCP image result. The preview appears in the intermediate MCP tool result card, not inside the assistant's final answer. The final answer must include the generated path and mention that the preview is shown above in the Cursor tool result.
7. If the host agent has another native image-generation or image-return tool that renders images inline, optionally add that preview after preserving the path. 
8. If there is no reliable inline display channel, keep the final asset in the project and report the generated path. When available, open the image resource in the editor or preview pane as a convenience, but do not claim it was embedded in chat.

## Common Commands

Generate a concept image:

```bash
"$HOME/.local/share/agent-dotfiles/python/bin/python" \
  "$HOME/Documents/agent-dotfiles/shared/skills/creativity/gpt-image2/scripts/codex_gpt_image2.py" \
  "compact sci-fi drone concept sheet, clean industrial design, three-quarter view" \
  --out "output/imagegen/drone-concept.png" \
  --size "1024x1024" \
  --quality low \
  --constraints "no logos, no watermark" \
  --json
```

Edit or use reference images:

```bash
"$HOME/.local/share/agent-dotfiles/python/bin/python" \
  "$HOME/Documents/agent-dotfiles/shared/skills/creativity/gpt-image2/scripts/codex_gpt_image2.py" \
  "replace only the background with a clean warm studio backdrop; keep the product unchanged" \
  --mode edit \
  --image "input/product.png" \
  --out "output/imagegen/product-studio.png" \
  --json
```

Dry-run without creating files:

```bash
"$HOME/.local/share/agent-dotfiles/python/bin/python" \
  "$HOME/Documents/agent-dotfiles/shared/skills/creativity/gpt-image2/scripts/codex_gpt_image2.py" \
  "test prompt" \
  --out "output/imagegen/test.png" \
  --dry-run \
  --json
```

## Parameters

- `PROMPT`, `--prompt`, or `--prompt-file`: exactly one image prompt source.
- `--out`: required final image path.
- `--cwd`: workspace root for the Codex run. Defaults to the current directory.
- `--mode generate|edit`: use `edit` when preserving or modifying an attached image.
- `--image`: attach a local image. Repeat for multiple inputs.
- `--size`: requested size or aspect, such as `1024x1024`, `1536x1024`, or `16:9`.
- `--quality low|medium|high|auto`: guidance for draft or final quality.
- `--style`, `--composition`, `--constraints`, `--avoid`: prompt-shaping helpers.
- `--transparent`: request transparent output. The wrapper asks Codex to follow its imagegen transparent workflow.
- `--force`: allow overwriting `--out`.
- `--model`: optional Codex model override.
- `--sandbox read-only|workspace-write|full-access`: defaults to `workspace-write`.
- `--json`: print machine-readable status.

## Prompt Guidance

Keep prompts specific but not bloated:

```text
Use case: stylized-concept
Asset type: concept sheet
Primary request: compact sci-fi drone with foldable arms
Style/medium: clean industrial design render
Composition/framing: three-quarter view, annotation-ready whitespace
Materials/textures: matte graphite shell, brushed aluminum hinges, subtle sensor glass
Constraints: no logos, no watermark, no extra vehicles
```

For edits, repeat invariants:

```text
Change only the background. Keep the subject shape, labels, colors, texture, and lighting direction unchanged.
```

## Notes

- This wrapper is intended for agents that lack a native image-generation tool.
- Codex should use its built-in imagegen skill directly instead of routing through this wrapper.
- The wrapper can attach Codex's local imagegen `SKILL.md` explicitly. Use `--no-attach-imagegen-skill` only if that causes SDK incompatibility.
- The generated filesystem path is the required user-facing output. Inline preview is best-effort and must not replace the path.
- Cursor-specific preview can be provided by the `cursor-inline-img-loader` MCP server, which loads a generated local image path and returns MCP `ImageContent`.
- Do not claim that reading a local image file will display it inline to the user. Use a documented inline image channel when the host provides one, otherwise provide the path and optionally open the image in the editor or preview surface.
