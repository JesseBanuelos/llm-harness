#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT="${1:-Summarize what this repository does in two short sentences.}"

cd "$ROOT_DIR"
PYTHONPATH=. python3 -m llm_harness.cli \
  --provider claude \
  --system "Be concise and practical." \
  --claude-model sonnet \
  "$PROMPT"
