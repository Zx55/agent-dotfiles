from __future__ import annotations

import unittest

from haos_openai_client.client import GenerateResult


class GenerateResultTest(unittest.TestCase):
    def test_structured_flag_does_not_depend_on_data_truthiness(self) -> None:
        result = GenerateResult(content="null", data=None, is_structured=True)

        self.assertTrue(result.structured)


if __name__ == "__main__":
    unittest.main()
