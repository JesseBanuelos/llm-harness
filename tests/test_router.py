import unittest

from llm_harness.router import HarnessRouter


class StubProvider:
    def __init__(self, response: str, default_model: str | None = None) -> None:
        self.response = response
        self.calls = []
        if default_model is not None:
            self.default_model = default_model

    def call(self, prompt: str, system: str | None, model: str) -> str:
        self.calls.append((prompt, system, model))
        return self.response


class RouterTests(unittest.TestCase):
    def test_openai_route_returns_single_result(self) -> None:
        openai = StubProvider("openai says hi")
        router = HarnessRouter(openai_provider=openai, claude_provider=StubProvider("unused"))

        results = router.dispatch(
            provider_name="openai",
            prompt="Hello",
            system="System",
            model_override="gpt-4o-mini",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider, "openai")
        self.assertEqual(results[0].response, "openai says hi")
        self.assertEqual(openai.calls, [("Hello", "System", "gpt-4o-mini")])

    def test_both_route_returns_labeled_results(self) -> None:
        openai = StubProvider("openai text")
        claude = StubProvider("claude text")
        router = HarnessRouter(openai_provider=openai, claude_provider=claude)

        results = router.dispatch(
            provider_name="both",
            prompt="Compare",
            system=None,
            model_override=None,
        )

        self.assertEqual([result.provider for result in results], ["claude", "openai"])
        self.assertEqual(results[0].response, "claude text")
        self.assertEqual(results[1].response, "openai text")
        self.assertEqual(claude.calls[0][2], "sonnet")
        self.assertEqual(openai.calls[0][2], "gpt-4o")

    def test_provider_failure_is_captured_in_results(self) -> None:
        class BrokenProvider:
            def call(self, prompt: str, system: str | None, model: str) -> str:
                raise RuntimeError("bad provider")

        router = HarnessRouter(
            openai_provider=BrokenProvider(),
            claude_provider=StubProvider("claude text"),
        )

        results = router.dispatch(
            provider_name="both",
            prompt="Compare",
            system=None,
            model_override=None,
        )

        openai_result = next(result for result in results if result.provider == "openai")
        self.assertIsNone(openai_result.response)
        self.assertEqual(openai_result.error, "bad provider")

    def test_both_route_prefers_provider_specific_models(self) -> None:
        openai = StubProvider("openai text", default_model="gpt-4o")
        claude = StubProvider("claude text", default_model="sonnet")
        router = HarnessRouter(openai_provider=openai, claude_provider=claude)

        results = router.dispatch(
            provider_name="both",
            prompt="Compare",
            system=None,
            model_override="shared-model",
            openai_model_override="gpt-4o-mini",
            claude_model_override="opus",
        )

        self.assertEqual([result.provider for result in results], ["claude", "openai"])
        self.assertEqual(claude.calls[0][2], "opus")
        self.assertEqual(openai.calls[0][2], "gpt-4o-mini")

    def test_single_provider_uses_shared_model_when_specific_flag_missing(self) -> None:
        openai = StubProvider("openai text", default_model="gpt-4o")
        router = HarnessRouter(openai_provider=openai, claude_provider=StubProvider("unused"))

        router.dispatch(
            provider_name="openai",
            prompt="Hello",
            system=None,
            model_override="gpt-4.1",
            openai_model_override=None,
            claude_model_override=None,
        )

        self.assertEqual(openai.calls[0][2], "gpt-4.1")
