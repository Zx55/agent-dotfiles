from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from haos_openai_client.client import OpenAIClientConfig, normalize_base_url


class OpenAIClientConfigTest(unittest.TestCase):
    def test_from_env_reads_api_key_base_url_and_model(self) -> None:
        env = {
            "OPENAI_API_KEY": "env-key",
            "OPENAI_BASE_URL": "https://example.test/v1",
            "OPENAI_MODEL": "env-model",
        }
        with patch.dict(os.environ, env, clear=True):
            config = OpenAIClientConfig.from_env()

        self.assertEqual(config.model, "env-model")
        self.assertEqual(config.base_url, "https://example.test/v1")

    def test_normalize_base_url_adds_scheme_and_v1_for_origin(self) -> None:
        self.assertEqual(
            normalize_base_url("token-plan-cn.xiaomimimo.com"),
            "https://token-plan-cn.xiaomimimo.com/v1",
        )

    def test_normalize_base_url_strips_endpoint_path(self) -> None:
        self.assertEqual(
            normalize_base_url("https://example.test/v1/chat/completions"),
            "https://example.test/v1",
        )

    def test_config_normalizes_base_url(self) -> None:
        config = OpenAIClientConfig(
            api_key="test-key",
            model="test-model",
            base_url="https://example.test",
        )

        self.assertEqual(config.base_url, "https://example.test/v1")

    def test_from_env_requires_api_key(self) -> None:
        with patch.dict(os.environ, {"OPENAI_MODEL": "env-model"}, clear=True):
            with self.assertRaisesRegex(ValueError, "api_key is required"):
                OpenAIClientConfig.from_env()


if __name__ == "__main__":
    unittest.main()
