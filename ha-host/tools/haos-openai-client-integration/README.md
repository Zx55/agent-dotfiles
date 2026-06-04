# HAOS OpenAI Client Integration

`haos-openai-client-integration` is a compact Home Assistant custom integration for calling OpenAI-compatible text generation APIs from Home Assistant AI Task.

The package owns the provider/client boundary:

- configurable `base_url`, `api_key`, and model
- Chat Completions API mode for broad OpenAI-compatible providers
- Responses API mode for OpenAI's newer API surface
- optional JSON Schema response formatting and parsing
- a local CLI for quick diagnostics
- a Home Assistant custom component that exposes one AI Task data-generation entity

The repository layout is intentionally direct:

```text
haos-openai-client-integration/
  src/
    client/
      __init__.py
      cli.py
      client.py
      config.py
      result.py
      schema.py
    __init__.py
    ai_task.py
    connection_test.py
    config_flow.py
    const.py
    button.py
    ha_client.py
    manifest.json
    strings.json
```

`src/` is the custom component directory content. Copy it to `/config/custom_components/haos_openai_client` on HAOS.

## Install Locally

```sh
cd ha-host/tools/haos-openai-client-integration
uv venv --seed .venv
uv pip install --python .venv/bin/python .
```

## CLI

Chat Completions mode:

```sh
.venv/bin/haos-openai-client prompt \
  --api-key "$OPENAI_API_KEY" \
  --base-url "https://api.openai.com/v1" \
  --model "gpt-4o-mini" \
  --api-mode chat_completions \
  --prompt "Suggest a short Home Assistant automation name for turning off bedroom lights."
```

Responses mode:

```sh
.venv/bin/haos-openai-client prompt \
  --api-key "$OPENAI_API_KEY" \
  --base-url "https://api.openai.com/v1" \
  --model "gpt-4o-mini" \
  --api-mode responses \
  --prompt "Suggest a short Home Assistant automation name for turning off bedroom lights."
```

Environment fallbacks:

```text
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL
```

## Structured Output

Pass a JSON Schema file to ask the provider for structured output:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

```sh
.venv/bin/haos-openai-client prompt \
  --api-key "$OPENAI_API_KEY" \
  --model "gpt-4o-mini" \
  --json-schema ./schema.json \
  --prompt "Generate a concise automation name."
```

The command prints parsed JSON when a schema is provided and raw text otherwise.

## Home Assistant Custom Integration

The deployable custom component content is:

```text
src/
```

It is intentionally limited to AI Task data generation. It does not create a conversation agent, expose Home Assistant tools to the model, generate images, or control smart-home entities directly.

### Deployment

Copy the integration directory to HAOS:

```sh
ssh haos 'mkdir -p /config/custom_components/haos_openai_client'
scp -r src/* haos:/config/custom_components/haos_openai_client/
ssh haos 'ha core restart'
```

Then configure it from the Home Assistant UI:

```text
Settings > Devices & services > Add integration > HAOS OpenAI Client
```

Configuration fields:

- `Name`: display name for the AI Task entity.
- `API key`: provider API key.
- `Base URL`: OpenAI-compatible API root, for example `https://api.openai.com/v1`.
- `Model`: provider model id.
- `API mode`: `chat_completions` for broad compatibility or `responses` for OpenAI Responses API.
- `Timeout seconds`, `Temperature`, `Maximum tokens`: optional generation settings.

Base URL is normalized before use. If only an origin is entered, for example `https://token-plan-cn.xiaomimimo.com`, the integration uses `https://token-plan-cn.xiaomimimo.com/v1`. If a full endpoint such as `/v1/chat/completions` is entered, it is reduced back to `/v1`.

After the first form is submitted, the integration runs a short test prompt and shows the result on a confirmation page. It does not call `/models`. A failed test does not block setup, so local or partially compatible providers can still be saved intentionally.

Configured entries also expose a `Test Connection` button entity. Pressing it runs the same short test prompt and posts the result as a Home Assistant persistent notification.

The connection test uses up to 64 output tokens by default and only passes when the response text is non-empty and contains `OK`.

The integration declares `custom_components.haos_openai_client` as its logger and writes test pass/fail results to HA logs. The integration page may only show a Logs shortcut after Home Assistant has log records for this domain.

In Home Assistant, the integration passes HA's shared async HTTP client into the OpenAI SDK to avoid blocking TLS certificate loading in the event loop.

### HA Verification

After restart and UI setup, the entity should appear as an AI Task provider. You can select it from the AI Suggestions page or call:

```yaml
action: ai_task.generate_data
data:
  entity_id: ai_task.haos_openai_client
  task_name: test_name
  instructions: Suggest a short automation name for turning off bedroom lights.
```

If Home Assistant reports a different entity id, use the entity id shown in Developer Tools.

## Tests

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q src tests
```

The tests use fake SDK clients and do not call external APIs.
