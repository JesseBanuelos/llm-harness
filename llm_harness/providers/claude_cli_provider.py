from __future__ import annotations

import os
import subprocess

from llm_harness.providers.base import LLMProvider

CLAUDE_CODE_DOCS_URL = "https://docs.anthropic.com/en/docs/claude-code"


class ClaudeCLIProvider(LLMProvider):
    """Calls Claude Code through the local ``claude`` CLI."""

    default_model = "sonnet"

    def __init__(self, timeout: int = 120) -> None:
        self.timeout = timeout

    def call(self, prompt: str, system: str | None, model: str) -> str:
        cmd = ["claude", "--print", "--model", model]
        if system:
            cmd.extend(["--system-prompt", system])
        cmd.append(prompt)
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                env=env,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Claude Code CLI is not installed or not on PATH. "
                f"Install or sign in with Claude Code: {CLAUDE_CODE_DOCS_URL}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Claude CLI timed out after {self.timeout} seconds."
            ) from exc

        if result.returncode != 0:
            error_text = result.stderr.strip() or result.stdout.strip()
            if not error_text:
                error_text = f"Unknown Claude CLI error (exit code {result.returncode})."
            raise RuntimeError(f"Claude CLI error: {error_text}")

        return result.stdout.strip()
