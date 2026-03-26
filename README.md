# llm-harness

First release of llm-harness, a lightweight Python CLI for running prompts against OpenAI, Claude Code, or both from one command. Includes parallel dual-provider mode, provider-specific model flags, JSON/Markdown/terminal output, smoke scripts, and a typed provider abstraction for future backends.

## Prerequisites

- Python 3.10 or newer
- Claude Code installed and authenticated locally
- An OpenAI API key for OpenAI-backed requests

Claude Code install docs:
- [https://docs.anthropic.com/en/docs/claude-code](https://docs.anthropic.com/en/docs/claude-code)

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional editable install with console script:

```bash
pip install -e .
```

Create your local environment file:

```bash
cp .env.example .env
```

Then set `OPENAI_API_KEY` in `.env` or export it in your shell.

## Usage

You can pass the prompt as a positional argument:

```bash
python -m llm_harness.cli --provider openai "Write a haiku about tax engines"
```

Or, after editable install:

```bash
llm-harness --provider claude "Summarize this repository"
```

If no positional prompt is provided, `llm-harness` reads from standard input.

### OpenAI mode

```bash
llm-harness --provider openai --system "Be concise" "Explain nexus in one paragraph"
```

Defaults:
- Provider: `openai`
- Model: `gpt-4o`

In terminal mode, OpenAI responses stream directly to stdout when OpenAI is the only selected provider.

### Claude mode

```bash
llm-harness --provider claude --timeout 180 "Summarize this design"
```

Defaults:
- Provider: `claude`
- Model: `sonnet`
- Timeout: `120` seconds

Claude requests use local Claude Code authentication. No Anthropic API key is required.

### Both providers in parallel

```bash
llm-harness --provider both --system "Be terse" "Compare two ways to cache this"
```

When `--provider both` is used, the harness runs both requests concurrently with `ThreadPoolExecutor` and prints results sequentially with clear labels:

- `=== CLAUDE ===`
- `=== OPENAI ===`

### Output formats

Terminal output:

```bash
llm-harness --provider both --output terminal "What changed?"
```

Markdown output:

```bash
llm-harness --provider both --output markdown "Draft release notes"
```

JSON output:

```bash
llm-harness --provider both --output json --verbose "Summarize the file"
```

### Flags

- `--provider`: `openai`, `claude`, or `both`
- `--system`: optional system prompt passed to the selected provider or providers
- `--model`: shared model override used when a provider-specific flag is not set
- `--openai-model`: override the OpenAI model
- `--claude-model`: override the Claude model
- `--timeout`: timeout in seconds for Claude CLI calls
- `--output`: `terminal`, `markdown`, or `json`
- `--verbose`: include timing details in rendered output

Provider-specific model flags take precedence over `--model`. For example:

```bash
llm-harness --provider both --claude-model sonnet --openai-model gpt-4o-mini "Compare these answers"
```

## Smoke Scripts

The repository includes a few runnable smoke scripts:

- `scripts/smoke_openai.sh`
- `scripts/smoke_claude.sh`
- `scripts/smoke_both.sh`

Make them executable once:

```bash
chmod +x scripts/*.sh
```

Run them with the built-in prompt:

```bash
./scripts/smoke_openai.sh
./scripts/smoke_claude.sh
./scripts/smoke_both.sh
```

Or pass your own prompt:

```bash
./scripts/smoke_both.sh "Compare how each provider would explain this tool"
```

## How It Works

- OpenAI calls use the `openai` Python SDK and `OPENAI_API_KEY`
- Claude calls use `claude --print --model <model>` and local CLI auth
- `both` mode executes both providers in parallel and returns structured results
- A common abstract base class makes it easy to add new providers later

## Extending With New Providers

To add another backend such as Gemini or a local Ollama instance:

1. Create a new provider module in `llm_harness/providers/`
2. Subclass `LLMProvider`
3. Implement `call(prompt, system, model) -> str`
4. Set a `default_model`
5. Register the provider in `llm_harness/router.py`

That keeps the CLI and output handling unchanged while new providers plug into the same contract.
