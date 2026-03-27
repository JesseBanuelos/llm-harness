import os
import unittest
from unittest.mock import MagicMock, patch

from llm_harness.providers.openai_provider import OpenAIProvider


class OpenAIProviderTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_init_raises_when_api_key_missing(self) -> None:
        with patch("llm_harness.providers.openai_provider._load_dotenv", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                OpenAIProvider()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_call_uses_chat_completions(self) -> None:
        message = MagicMock()
        message.content = "openai response"
        choice = MagicMock()
        choice.message = message
        response = MagicMock()
        response.choices = [choice]

        create_mock = MagicMock(return_value=response)
        client = MagicMock()
        client.chat.completions.create = create_mock

        with patch("llm_harness.providers.openai_provider._build_openai_client", return_value=client):
            provider = OpenAIProvider(stream=False)
            result = provider.call(
                prompt="Hello",
                system="Be kind",
                model="gpt-4o-mini",
            )

        self.assertEqual(result, "openai response")
        create_mock.assert_called_once()
        kwargs = create_mock.call_args.kwargs
        self.assertEqual(kwargs["model"], "gpt-4o-mini")
        self.assertFalse(kwargs["stream"])
        self.assertEqual(
            kwargs["messages"],
            [
                {"role": "system", "content": "Be kind"},
                {"role": "user", "content": "Hello"},
            ],
        )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_streaming_call_emits_chunks_and_returns_text(self) -> None:
        chunk_one = MagicMock()
        chunk_one.choices = [MagicMock(delta=MagicMock(content="Hello"))]
        chunk_two = MagicMock()
        chunk_two.choices = [MagicMock(delta=MagicMock(content=" world"))]

        create_mock = MagicMock(return_value=iter([chunk_one, chunk_two]))
        client = MagicMock()
        client.chat.completions.create = create_mock
        captured = []

        with patch("llm_harness.providers.openai_provider._build_openai_client", return_value=client):
            provider = OpenAIProvider(stream=True, stream_handler=captured.append)
            result = provider.call(prompt="Hello", system=None, model="gpt-4o")

        self.assertEqual(result, "Hello world")
        self.assertEqual(captured, ["Hello", " world"])
