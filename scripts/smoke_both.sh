#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT="${1:-Compare how OpenAI and Claude would summarize this harness.}"

cd "$ROOT_DIR"
PYTHONPATH=. python3 -m llm_harness.cli \
  --provider both \
  --system "Be concise and practical." \
  --claude-model sonnet \
  --openai-model gpt-4o-mini \
  --output terminal \
  --verbose \
  "$PROMPT"
