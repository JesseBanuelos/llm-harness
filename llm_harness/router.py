from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from time import perf_counter

from llm_harness.providers.claude_cli_provider import ClaudeCLIProvider
from llm_harness.providers.openai_provider import OpenAIProvider


@dataclass(slots=True)
class ProviderResult:
    provider: str
    model: str
    response: str | None
    error: str | None
    elapsed_seconds: float


class HarnessRouter:
    """Dispatches prompt requests to one or more providers."""

    def __init__(
        self,
        openai_provider: OpenAIProvider,
        claude_provider: ClaudeCLIProvider,
    ) -> None:
        self.openai_provider = openai_provider
        self.claude_provider = claude_provider

    def dispatch(
        self,
        provider_name: str,
        prompt: str,
        system: str | None,
        model_override: str | None,
        openai_model_override: str | None = None,
        claude_model_override: str | None = None,
    ) -> list[ProviderResult]:
        if provider_name == "openai":
            return [
                self._call_provider(
                    provider="openai",
                    provider_impl=self.openai_provider,
                    prompt=prompt,
                    system=system,
                    model=self._resolve_model(
                        "openai",
                        model_override,
                        openai_model_override,
                        claude_model_override,
                    ),
                )
            ]

        if provider_name == "claude":
            return [
                self._call_provider(
                    provider="claude",
                    provider_impl=self.claude_provider,
                    prompt=prompt,
                    system=system,
                    model=self._resolve_model(
                        "claude",
                        model_override,
                        openai_model_override,
                        claude_model_override,
                    ),
                )
            ]

        if provider_name != "both":
            raise ValueError(f"Unsupported provider: {provider_name}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                "claude": executor.submit(
                    self._call_provider,
                    provider="claude",
                    provider_impl=self.claude_provider,
                    prompt=prompt,
                    system=system,
                    model=self._resolve_model(
                        "claude",
                        model_override,
                        openai_model_override,
                        claude_model_override,
                    ),
                ),
                "openai": executor.submit(
                    self._call_provider,
                    provider="openai",
                    provider_impl=self.openai_provider,
                    prompt=prompt,
                    system=system,
                    model=self._resolve_model(
                        "openai",
                        model_override,
                        openai_model_override,
                        claude_model_override,
                    ),
                ),
            }

        return [futures["claude"].result(), futures["openai"].result()]

    def _resolve_model(
        self,
        provider: str,
        model_override: str | None,
        openai_model_override: str | None,
        claude_model_override: str | None,
    ) -> str:
        if provider == "claude" and claude_model_override:
            return claude_model_override
        if provider == "openai" and openai_model_override:
            return openai_model_override
        if model_override:
            return model_override
        if provider == "claude":
            return getattr(self.claude_provider, "default_model", "sonnet")
        return getattr(self.openai_provider, "default_model", "gpt-4o")

    @staticmethod
    def _call_provider(
        provider: str,
        provider_impl: OpenAIProvider | ClaudeCLIProvider,
        prompt: str,
        system: str | None,
        model: str,
    ) -> ProviderResult:
        started = perf_counter()
        try:
            response = provider_impl.call(prompt=prompt, system=system, model=model)
            return ProviderResult(
                provider=provider,
                model=model,
                response=response,
                error=None,
                elapsed_seconds=round(perf_counter() - started, 3),
            )
        except Exception as exc:
            return ProviderResult(
                provider=provider,
                model=model,
                response=None,
                error=str(exc),
                elapsed_seconds=round(perf_counter() - started, 3),
            )
