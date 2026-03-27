#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT="${1:-Give me a one-sentence summary of why this harness is useful.}"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is not set. Export it or add it to .env before running this smoke script." >&2
  exit 1
fi

cd "$ROOT_DIR"
PYTHONPATH=. python3 -m llm_harness.cli \
  --provider openai \
  --system "Be concise and practical." \
  --openai-model gpt-4o \
  "$PROMPT"
