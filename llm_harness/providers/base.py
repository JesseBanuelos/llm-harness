from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for provider integrations.

    To add a new backend, create a subclass in ``llm_harness/providers``,
    define its ``default_model``, and implement ``call(prompt, system, model)``.
    Examples include a Gemini API provider, a local Ollama provider, or any
    other backend that can turn a prompt into a text response.
    """

    default_model: str

    @abstractmethod
    def call(self, prompt: str, system: str | None, model: str) -> str:
        """Return a text completion for the given prompt."""

