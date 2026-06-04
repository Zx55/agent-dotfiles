from __future__ import annotations

from types import SimpleNamespace
import unittest

from haos_openai_client.client import HaosOpenAIClient, OpenAIClientConfig


class FakeChatCompletions:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class FakeResponses:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class FakeSdkClient:
    def __init__(self, *, chat_content: str = "", response_text: str = "") -> None:
        self.chat_completions = FakeChatCompletions(chat_content)
        self.responses = FakeResponses(response_text)
        self.chat = SimpleNamespace(
            completions=self.chat_completions,
        )


class HaosOpenAIClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_chat_completions_generates_text(self) -> None:
        sdk_client = FakeSdkClient(chat_content="done")
        client = HaosOpenAIClient(
            OpenAIClientConfig(
                api_key="test-key",
                model="test-model",
                api_mode="chat_completions",
            ),
            sdk_client=sdk_client,
        )

        result = await client.generate("hello")

        self.assertEqual(result.content, "done")
        self.assertFalse(result.structured)
        call = sdk_client.chat_completions.calls[0]
        self.assertEqual(call["model"], "test-model")
        self.assertEqual(call["messages"][1]["content"], "hello")

    async def test_chat_completions_generates_structured_data(self) -> None:
        sdk_client = FakeSdkClient(chat_content='{"name":"Good night"}')
        client = HaosOpenAIClient(
            OpenAIClientConfig(
                api_key="test-key",
                model="test-model",
                api_mode="chat_completions",
            ),
            sdk_client=sdk_client,
        )

        result = await client.generate(
            "name it",
            json_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
            },
            schema_name="automation_name",
        )

        self.assertEqual(result.data, {"name": "Good night"})
        response_format = sdk_client.chat_completions.calls[0]["response_format"]
        self.assertEqual(response_format["type"], "json_schema")
        self.assertTrue(response_format["json_schema"]["strict"])
        schema = response_format["json_schema"]["schema"]
        self.assertEqual(schema["required"], ["name"])
        self.assertFalse(schema["additionalProperties"])

    async def test_responses_generates_structured_data(self) -> None:
        sdk_client = FakeSdkClient(response_text='{"name":"Good night"}')
        client = HaosOpenAIClient(
            OpenAIClientConfig(
                api_key="test-key",
                model="test-model",
                api_mode="responses",
                max_tokens=128,
            ),
            sdk_client=sdk_client,
        )

        result = await client.generate(
            "name it",
            json_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )

        self.assertEqual(result.data, {"name": "Good night"})
        call = sdk_client.responses.calls[0]
        self.assertEqual(call["max_output_tokens"], 128)
        self.assertEqual(call["text"]["format"]["type"], "json_schema")


if __name__ == "__main__":
    unittest.main()
