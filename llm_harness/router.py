from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter

from llm_harness.providers.claude_cli_provider import ClaudeCLIProvider
from llm_harness.providers.openai_provider import OpenAIProvider

ProviderFactory = Callable[[], OpenAIProvider | ClaudeCLIProvider]


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
        openai_provider: OpenAIProvider | None = None,
        claude_provider: ClaudeCLIProvider | None = None,
        openai_factory: ProviderFactory | None = None,
        claude_factory: ProviderFactory | None = None,
    ) -> None:
        self.openai_provider = openai_provider
        self.claude_provider = claude_provider
        self.openai_factory = openai_factory
        self.claude_factory = claude_factory

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

    def _get_provider(self, provider: str) -> OpenAIProvider | ClaudeCLIProvider:
        if provider == "openai":
            if self.openai_provider is None:
                if self.openai_factory is None:
                    raise RuntimeError("OpenAI provider is not configured.")
                self.openai_provider = self.openai_factory()
            return self.openai_provider

        if self.claude_provider is None:
            if self.claude_factory is None:
                raise RuntimeError("Claude provider is not configured.")
            self.claude_provider = self.claude_factory()
        return self.claude_provider

    def _call_provider(
        self,
        provider: str,
        prompt: str,
        system: str | None,
        model: str,
    ) -> ProviderResult:
        started = perf_counter()
        try:
            provider_impl = self._get_provider(provider)
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
