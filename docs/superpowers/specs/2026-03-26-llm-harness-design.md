# LLM Harness Design

## Goal

Create a fresh Python repository that exposes a single CLI harness for calling OpenAI, Claude Code via the `claude` CLI, or both providers from one command.

## Scope

The repository will include:

- A typed `llm_harness` package with provider abstractions.
- An OpenAI provider backed by the `openai` Python SDK.
- A Claude provider backed by `subprocess` calls to `claude --print`.
- A router that supports `openai`, `claude`, and `both`.
- A Click-based CLI with output formatting and verbose timing.
- Environment loading via `.env`.
- Documentation and install instructions.

The repository will not include:

- Persistent conversation state.
- Multi-turn chat history management.
- Provider-specific retry policies.
- Additional providers beyond OpenAI and Claude.

## Architecture

The CLI entry point parses flags, loads environment variables, and delegates execution to a router. The router instantiates the requested provider or providers and returns normalized results. Provider implementations share a common abstract base class so future backends can implement the same `call(prompt, system, model) -> str` contract.

For `--provider both`, the router will use `concurrent.futures.ThreadPoolExecutor` to run both providers concurrently. Results are collected independently and rendered sequentially with explicit labels so the terminal output remains stable and easy to read.

## Components

### `llm_harness/providers/base.py`

Defines the `LLMProvider` abstract base class and documents the provider extension pattern.

### `llm_harness/providers/openai_provider.py`

Wraps the OpenAI Python SDK. It reads `OPENAI_API_KEY` from the environment after `.env` loading, defaults to model `gpt-4o`, and supports streaming output in terminal mode.

### `llm_harness/providers/claude_cli_provider.py`

Wraps the local `claude` CLI. It calls `claude --print --model <model>`, passes `--system-prompt` when provided, enforces a timeout, and surfaces clear installation guidance if the binary is missing.

### `llm_harness/router.py`

Builds the selected providers, executes one or both calls, tracks timing, and returns structured results for output rendering.

### `llm_harness/cli.py`

Provides the user-facing command with flags for provider, prompt, system prompt, model override, timeout, output format, and verbose mode.

## Output Modes

- `terminal`: plain terminal output, with streaming for OpenAI single-provider mode and labeled sections for `both`.
- `markdown`: provider-labeled Markdown sections.
- `json`: machine-readable JSON including provider name, model, response, elapsed time, and error state.

## Error Handling

- OpenAI provider raises a clear configuration error when `OPENAI_API_KEY` is missing.
- Claude provider raises a clear install/auth guidance error when `claude` is not on `PATH`.
- Non-zero Claude subprocess exits surface stderr in the exception.
- Timeout failures surface provider-specific timeout messages.
- In `both` mode, each provider result is captured independently so one failure can be reported alongside the other provider's success.

## Testing Strategy

Use `unittest` with mocks to verify:

- Router behavior for single-provider and dual-provider modes.
- Output formatting helpers.
- Claude CLI command construction and missing-binary errors.
- OpenAI provider environment validation and request shaping where practical without live API calls.

## Verification

Before completion:

- Run `which claude` or `claude --version`.
- Run the unit test suite.
- If Claude is unavailable, note that in the README while keeping the harness fully implemented.
