from __future__ import annotations

import json
import sys
from dataclasses import asdict

import click

from llm_harness.router import HarnessRouter, ProviderResult
from llm_harness.providers.claude_cli_provider import ClaudeCLIProvider
from llm_harness.providers.openai_provider import OpenAIProvider


def build_router(
    provider_name: str,
    timeout: int,
    output_format: str,
) -> HarnessRouter:
    stream_openai = provider_name == "openai" and output_format == "terminal"
    openai_provider = OpenAIProvider(
        stream=stream_openai,
        stream_handler=lambda chunk: click.echo(chunk, nl=False),
    )
    claude_provider = ClaudeCLIProvider(timeout=timeout)
    return HarnessRouter(openai_provider=openai_provider, claude_provider=claude_provider)


def resolve_prompt(prompt: str | None) -> str:
    if prompt:
        return prompt
    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            return piped
    raise click.UsageError("Provide a prompt argument or pipe prompt text on stdin.")


def format_results(
    results: list[ProviderResult],
    output_format: str,
    verbose: bool,
) -> str:
    if output_format == "json":
        return json.dumps(
            {"results": [asdict(result) for result in results]},
            indent=2,
        )

    if output_format == "markdown":
        sections: list[str] = []
        for result in results:
            header = f"## {result.provider.upper()}"
            body = result.response if result.error is None else f"Error: {result.error}"
            section = f"{header}\n\n{body}"
            if verbose:
                section += f"\n\n_Time: {result.elapsed_seconds:.3f}s_"
            sections.append(section)
        return "\n\n".join(sections)

    if len(results) == 1:
        result = results[0]
        lines = [
            result.response if result.error is None else f"Error: {result.error}",
        ]
        if verbose:
            lines.append(f"[{result.provider} | {result.model} | {result.elapsed_seconds:.3f}s]")
        return "\n".join(lines)

    sections = []
    for result in results:
        label = f"=== {result.provider.upper()} ==="
        body = result.response if result.error is None else f"Error: {result.error}"
        section_lines = [label, body]
        if verbose:
            section_lines.append(f"[model={result.model} time={result.elapsed_seconds:.3f}s]")
        sections.append("\n".join(section_lines))
    return "\n\n".join(sections)


@click.command()
@click.argument("prompt", required=False)
@click.option(
    "--provider",
    type=click.Choice(["openai", "claude", "both"]),
    default="openai",
    show_default=True,
)
@click.option("--system", help="Optional system prompt passed to the selected provider(s).")
@click.option("--model", help="Shared model override used when a provider-specific model is not set.")
@click.option("--openai-model", help="Override the OpenAI model.")
@click.option("--claude-model", help="Override the Claude model.")
@click.option(
    "--timeout",
    type=int,
    default=120,
    show_default=True,
    help="Timeout in seconds for Claude CLI calls.",
)
@click.option(
    "--output",
    "output_format",
    type=click.Choice(["terminal", "markdown", "json"]),
    default="terminal",
    show_default=True,
)
@click.option("--verbose", is_flag=True, help="Show provider timing details.")
def cli(
    prompt: str | None,
    provider: str,
    system: str | None,
    model: str | None,
    openai_model: str | None,
    claude_model: str | None,
    timeout: int,
    output_format: str,
    verbose: bool,
) -> None:
    """Call OpenAI, Claude Code, or both from one CLI."""
    resolved_prompt = resolve_prompt(prompt)
    router = build_router(provider_name=provider, timeout=timeout, output_format=output_format)
    results = router.dispatch(
        provider_name=provider,
        prompt=resolved_prompt,
        system=system,
        model_override=model,
        openai_model_override=openai_model,
        claude_model_override=claude_model,
    )

    if provider == "openai" and output_format == "terminal":
        result = results[0]
        if result.error:
            raise click.ClickException(result.error)
        if verbose:
            click.echo()
            click.echo(f"[openai | {result.model} | {result.elapsed_seconds:.3f}s]")
        return

    click.echo(format_results(results=results, output_format=output_format, verbose=verbose))


if __name__ == "__main__":
    cli()
