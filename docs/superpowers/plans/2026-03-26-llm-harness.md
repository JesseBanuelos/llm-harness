# LLM Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fresh Python repository that exposes one CLI for OpenAI, Claude Code, or both providers.

**Architecture:** A Click CLI loads configuration and forwards requests to a router. The router delegates to concrete providers implementing a shared abstract interface, supports parallel execution for the `both` mode, and returns structured results for terminal, Markdown, and JSON rendering.

**Tech Stack:** Python 3.10+, click, openai, python-dotenv, subprocess, concurrent.futures, unittest

---

### Task 1: Scaffold repository metadata and documentation

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `README.md`
- Create: `llm_harness/__init__.py`
- Create: `llm_harness/providers/__init__.py`

- [ ] **Step 1: Create package metadata and dependency declarations**
- [ ] **Step 2: Document installation, usage, and extension points in the README**
- [ ] **Step 3: Add example environment configuration**

### Task 2: Define the provider abstraction

**Files:**
- Create: `llm_harness/providers/base.py`

- [ ] **Step 1: Write the abstract provider contract**
- [ ] **Step 2: Add extension guidance docstrings for future providers**

### Task 3: Implement the Claude CLI provider

**Files:**
- Create: `llm_harness/providers/claude_cli_provider.py`
- Test: `tests/test_claude_cli_provider.py`

- [ ] **Step 1: Write failing tests for command construction and error handling**
- [ ] **Step 2: Verify the tests fail**
- [ ] **Step 3: Implement the minimal provider logic**
- [ ] **Step 4: Run tests to verify they pass**

### Task 4: Implement the OpenAI provider

**Files:**
- Create: `llm_harness/providers/openai_provider.py`
- Test: `tests/test_openai_provider.py`

- [ ] **Step 1: Write failing tests for missing API key and request dispatch**
- [ ] **Step 2: Verify the tests fail**
- [ ] **Step 3: Implement the provider with optional streaming**
- [ ] **Step 4: Run tests to verify they pass**

### Task 5: Implement router and result modeling

**Files:**
- Create: `llm_harness/router.py`
- Test: `tests/test_router.py`

- [ ] **Step 1: Write failing tests for single-provider and both-provider routing**
- [ ] **Step 2: Verify the tests fail**
- [ ] **Step 3: Implement sequential and parallel dispatch with timing**
- [ ] **Step 4: Run tests to verify they pass**

### Task 6: Implement the Click CLI and output renderers

**Files:**
- Create: `llm_harness/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests for JSON and Markdown rendering helpers**
- [ ] **Step 2: Verify the tests fail**
- [ ] **Step 3: Implement the CLI, prompt resolution, and output formatting**
- [ ] **Step 4: Run tests to verify they pass**

### Task 7: Verify the full repository

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Check Claude CLI availability with `which claude` or `claude --version`**
- [ ] **Step 2: Note Claude availability in the README if necessary**
- [ ] **Step 3: Run `python3 -m unittest discover -s tests -v`**
- [ ] **Step 4: Review outputs and summarize any remaining caveats**
