from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from typing import Any

from llm_harness.providers.base import LLMProvider

StreamHandler = Callable[[str], None]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _build_openai_client(api_key: str) -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is not installed. Install dependencies with "
            "'pip install -r requirements.txt'."
        ) from exc
    return OpenAI(api_key=api_key)


def _coerce_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
            else:
                text = getattr(item, "text", None)
                if text:
                    parts.append(str(text))
        return "".join(parts)
    return str(content)


class OpenAIProvider(LLMProvider):
    """Calls the OpenAI Chat Completions API."""

    default_model = "gpt-4o"

    def __init__(
        self,
        stream: bool = False,
        stream_handler: StreamHandler | None = None,
    ) -> None:
        _load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to your environment or .env file."
            )

        self.client = _build_openai_client(api_key)
        self.stream = stream
        self.stream_handler = stream_handler

    def call(self, prompt: str, system: str | None, model: str) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        if self.stream:
            return self._streaming_call(messages=messages, model=model)

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
        )
        return _coerce_content(response.choices[0].message.content).strip()

    def _streaming_call(self, messages: list[dict[str, str]], model: str) -> str:
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        chunks: list[str] = []
        for chunk in self._iter_stream(stream):
            chunks.append(chunk)
            if self.stream_handler is not None:
                self.stream_handler(chunk)
        return "".join(chunks).strip()

    @staticmethod
    def _iter_stream(stream: Iterable[Any]) -> Iterable[str]:
        for chunk in stream:
            choices = getattr(chunk, "choices", [])
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            content = getattr(delta, "content", None)
            text = _coerce_content(content)
            if text:
                yield text
