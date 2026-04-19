# OpenAI-Compatible Provider Configuration

Use this reference when the user wants Dayu to call a provider that speaks an OpenAI-compatible API but is not OpenAI itself.

Common examples:

- Moonshot / Kimi
- custom gateway services that expose `/v1/chat/completions`
- other vendors that instruct users to reuse an OpenAI-style client

## When this matters

`dayu-cli init` asks the user to choose a provider and will happily accept an existing `OPENAI_API_KEY`. That is enough only when the requests should really go to OpenAI.

If the key actually belongs to a different OpenAI-compatible provider, Dayu may still need a post-init config change in `workspace/config/llm_models.json` and sometimes in `workspace/config/prompts/manifests/*.json`.

## What to change

For the target model config in `llm_models.json`, confirm:

- the config name the manifests should reference
- `endpoint_url`
- `model`
- `headers.Authorization`
- temperature constraints or other provider-specific payload quirks

Then make sure each relevant manifest's `model.default_name` and `model.allowed_names` reference the intended config name.

This default step matters:

- if you only add or edit a model entry in `llm_models.json`, users may still need to pass `--model-name` every time
- if you want the provider to become the normal default for Dayu usage, update each relevant manifest's `model.default_name`
- if you want explicit selection and validation to stay consistent, update `model.allowed_names` too
- if you do not want to change the global default behavior, leave the manifests alone and tell the user to pass `--model-name <config-name>` when needed

## Recommended verification flow

1. Verify the provider's model list or a minimal completion call with `curl`.
2. Update `llm_models.json` with the provider-specific endpoint and model ID.
3. If needed, rename the Dayu config entry to a user-friendly name.
4. If the provider should become the new default experience, update `model.default_name` in the relevant manifests.
5. Update `model.allowed_names` wherever the new config name should be selectable without manual JSON edits.
6. Run a minimal `dayu-cli prompt` against the workspace to confirm the config works end-to-end.

## Moonshot / Kimi example

For Moonshot's OpenAI-compatible API:

- endpoint base: `https://api.moonshot.cn`
- chat completions endpoint: `https://api.moonshot.cn/v1/chat/completions`

Example checks:

```bash
curl -sS https://api.moonshot.cn/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```bash
cat <<'JSON' >/tmp/moonshot_test_payload.json
{
  "model": "kimi-k2.5",
  "messages": [{"role": "user", "content": "Reply with OK only."}],
  "max_tokens": 8,
  "temperature": 1
}
JSON

curl -sS https://api.moonshot.cn/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data @/tmp/moonshot_test_payload.json
```

## Suggested final user-facing command

Once the config and manifest defaults are aligned, users should normally be able to omit `--model-name` and rely on the manifest default. If they want to force the model explicitly during verification, use:

```bash
dayu-cli prompt --base ~/.dayu/workspace --model-name <config-name> "Just respond OK"
```
