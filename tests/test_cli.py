import json
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from llm_harness.cli import ProviderResult, build_router, cli, format_results


class CLITests(unittest.TestCase):
    def test_format_results_json_includes_timing_and_errors(self) -> None:
        results = [
            ProviderResult(
                provider="claude",
                model="sonnet",
                response="hello",
                error=None,
                elapsed_seconds=1.23,
            ),
            ProviderResult(
                provider="openai",
                model="gpt-4o",
                response=None,
                error="missing key",
                elapsed_seconds=2.34,
            ),
        ]

        payload = format_results(results, output_format="json", verbose=True)
        parsed = json.loads(payload)

        self.assertEqual(parsed["results"][0]["provider"], "claude")
        self.assertEqual(parsed["results"][1]["error"], "missing key")
        self.assertEqual(parsed["results"][0]["elapsed_seconds"], 1.23)

    def test_format_results_markdown_uses_labels(self) -> None:
        results = [
            ProviderResult(
                provider="claude",
                model="sonnet",
                response="hello",
                error=None,
                elapsed_seconds=0.5,
            ),
            ProviderResult(
                provider="openai",
                model="gpt-4o",
                response="hi",
                error=None,
                elapsed_seconds=0.7,
            ),
        ]

        payload = format_results(results, output_format="markdown", verbose=False)

        self.assertIn("## CLAUDE", payload)
        self.assertIn("## OPENAI", payload)

    def test_cli_requires_prompt_argument_or_stdin(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--provider", "openai"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Provide a prompt argument", result.output)

    def test_cli_passes_provider_specific_models_to_router(self) -> None:
        runner = CliRunner()

        with patch("llm_harness.cli.build_router") as build_router_mock:
            router = build_router_mock.return_value
            router.dispatch.return_value = [
                ProviderResult(
                    provider="claude",
                    model="opus",
                    response="done",
                    error=None,
                    elapsed_seconds=0.2,
                )
            ]

            result = runner.invoke(
                cli,
                [
                    "--provider",
                    "claude",
                    "--model",
                    "shared-model",
                    "--claude-model",
                    "opus",
                    "Hello",
                ],
            )

        self.assertEqual(result.exit_code, 0)
        router.dispatch.assert_called_once_with(
            provider_name="claude",
            prompt="Hello",
            system=None,
            model_override="shared-model",
            openai_model_override=None,
            claude_model_override="opus",
        )

    def test_build_router_does_not_construct_openai_for_claude_only(self) -> None:
        with patch("llm_harness.cli.OpenAIProvider") as openai_mock, patch(
            "llm_harness.cli.ClaudeCLIProvider"
        ) as claude_mock:
            build_router(provider_name="claude", timeout=120, output_format="terminal")

        openai_mock.assert_not_called()
        claude_mock.assert_not_called()
