import subprocess
import unittest
from unittest.mock import ANY
from unittest.mock import patch

from llm_harness.providers.claude_cli_provider import ClaudeCLIProvider


class ClaudeCLIProviderTests(unittest.TestCase):
    def test_call_builds_expected_command(self) -> None:
        provider = ClaudeCLIProvider(timeout=45)

        completed = subprocess.CompletedProcess(
            args=["claude"],
            returncode=0,
            stdout="hello from claude\n",
            stderr="",
        )

        with patch("subprocess.run", return_value=completed) as run_mock:
            response = provider.call(
                prompt="Summarize this",
                system="You are concise",
                model="sonnet",
            )

        self.assertEqual(response, "hello from claude")
        run_mock.assert_called_once_with(
            [
                "claude",
                "--print",
                "--model",
                "sonnet",
                "--system-prompt",
                "You are concise",
                "Summarize this",
            ],
            capture_output=True,
            env=ANY,
            text=True,
            timeout=45,
            check=False,
        )
        env = run_mock.call_args.kwargs["env"]
        self.assertNotIn("ANTHROPIC_API_KEY", env)

    def test_call_raises_helpful_error_when_binary_missing(self) -> None:
        provider = ClaudeCLIProvider()

        with patch("subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(RuntimeError, "Claude Code CLI is not installed"):
                provider.call(prompt="Hi", system=None, model="sonnet")

    def test_call_raises_on_non_zero_exit(self) -> None:
        provider = ClaudeCLIProvider()
        completed = subprocess.CompletedProcess(
            args=["claude"],
            returncode=1,
            stdout="",
            stderr="boom",
        )

        with patch("subprocess.run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "Claude CLI error: boom"):
                provider.call(prompt="Hi", system=None, model="sonnet")

    def test_call_uses_stdout_when_stderr_is_empty_on_failure(self) -> None:
        provider = ClaudeCLIProvider()
        completed = subprocess.CompletedProcess(
            args=["claude"],
            returncode=1,
            stdout="Not logged in · Please run /login",
            stderr="",
        )

        with patch("subprocess.run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "Please run /login"):
                provider.call(prompt="Hi", system=None, model="sonnet")
