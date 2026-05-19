from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mcp_launcher.cli import LauncherError, build_launch_plan, parse_args, parse_env_file_line


def plan(argv: list[str], env: dict[str, str] | None = None):
    return build_launch_plan(parse_args(argv), env or {})


class LauncherTests(unittest.TestCase):
    def test_expands_home_and_env_in_env_assignment(self) -> None:
        result = plan(
            ["--env", "BIN=~/.local/bin/$TOOL", "--", "$BIN", "--serve"],
            {"HOME": "/Users/example", "TOOL": "server"},
        )

        self.assertEqual(result.env["BIN"], "/Users/example/.local/bin/server")
        self.assertEqual(result.argv, ("/Users/example/.local/bin/server", "--serve"))

    def test_env_file_values_are_available_to_later_env(self) -> None:
        with TemporaryDirectory() as tmp:
            env_file = Path(tmp) / "secret"
            env_file.write_text(
                "\n".join(
                    [
                        "# comment",
                        "export DEEPSEEK_API_KEY=\"secret-value\"",
                        "TOKEN_ALIAS=$DEEPSEEK_API_KEY",
                    ]
                ),
                encoding="utf-8",
            )

            result = plan(
                [
                    "--env-file",
                    str(env_file),
                    "--env",
                    "API_KEY=$TOKEN_ALIAS",
                    "--",
                    "server",
                ],
                {"HOME": "/Users/example"},
            )

        self.assertEqual(result.env["DEEPSEEK_API_KEY"], "secret-value")
        self.assertEqual(result.env["TOKEN_ALIAS"], "secret-value")
        self.assertEqual(result.env["API_KEY"], "secret-value")

    def test_missing_env_fails_by_default(self) -> None:
        with self.assertRaisesRegex(LauncherError, r"\$MISSING"):
            plan(["--env", "TOKEN=$MISSING", "--", "server"])

    def test_allow_missing_env_expands_to_empty(self) -> None:
        result = plan(["--allow-missing-env", "--env", "TOKEN=$MISSING", "--", "server"])

        self.assertEqual(result.env["TOKEN"], "")

    def test_parse_env_file_line(self) -> None:
        cases = [
            ("", None),
            ("# comment", None),
            ("FOO=bar", ("FOO", "bar")),
            ("export FOO='bar baz'", ("FOO", "bar baz")),
            ('export FOO="bar baz"', ("FOO", "bar baz")),
        ]
        for line, expected in cases:
            with self.subTest(line=line):
                self.assertEqual(parse_env_file_line(line), expected)

    def test_rejects_invalid_env_file_line(self) -> None:
        with self.assertRaises(LauncherError):
            parse_env_file_line("not an assignment")


if __name__ == "__main__":
    unittest.main()
