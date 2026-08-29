"""CLI entry point: investigate, synthesize-demo, eval."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from execos.config import load_config
from execos.eval.fixtures import ALL_FIXTURES
from execos.llm import DailyQuotaExhausted, OllamaUnavailable, build_llm_client
from execos.report.render import save_run
from execos.supervisor.orchestrate import run_supervisor, synthesize

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
console = Console()


@app.command()
def investigate(
    question: str = typer.Option(..., help="The executive's question."),
    deal_id: str = typer.Option(None, "--deal-id", help="Specific deal to investigate (revenue_ops). Defaults to the top flagged deal."),
    target_date: str = typer.Option(None, "--target-date", help="ISO date to investigate (data_investigation), e.g. 2025-04-15."),
) -> None:
    """Full pipeline: route -> delegate to real specialists (Projects 01/09) -> synthesize.

    Specialist delegation calls Project 01/09's own Gemini-backed agents
    directly (they predate this portfolio's Ollama fallback pattern) --
    this command requires GEMINI_API_KEY to be valid and unexhausted for
    those two projects' own .env files, regardless of this project's own
    LLM_PROVIDER setting.
    """
    config = load_config()
    console.print(f"[bold]Supervisor investigating (own LLM provider: {config.llm_provider})...[/]")
    client = build_llm_client(config)
    try:
        trace = run_supervisor(client, question, deal_id=deal_id, target_date=target_date)
    except (DailyQuotaExhausted, OllamaUnavailable) as exc:
        console.print(f"[bold red]Stopped: {exc}[/]")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]Specialists invoked:[/] {trace.routing.relevant_specialists}")
    if trace.unavailable:
        console.print(f"[bold yellow]Unavailable:[/] {trace.unavailable}")

    table = Table(title="Specialist Findings")
    table.add_column("Specialist")
    table.add_column("Summary")
    table.add_column("Confidence")
    table.add_column("Own Grounding")
    for f in trace.findings:
        table.add_row(f.specialist, f.summary, f.confidence, "yes" if f.specialist_grounding_passed else "no")
    console.print(table)

    s = trace.synthesis
    console.print(f"\n[bold]Cross-domain connection found:[/] {s.cross_domain_connection_found} ({s.connection_confidence})")
    console.print(f"[bold]Reasoning:[/] {s.connection_reasoning}")
    console.print(f"[bold]Coverage:[/] {s.coverage_note}")

    if trace.grounding_violations:
        console.print(f"\n[bold red]Grounding: FAILED[/] — {trace.grounding_violations}")
    else:
        console.print("\n[bold green]Grounding: passed[/]")

    run_dir = save_run(trace, config.runs_dir)
    console.print(f"Saved to: {run_dir}")


@app.command(name="synthesize-demo")
def synthesize_demo(scenario: str = typer.Option(..., help="'connected' or 'unrelated' -- see eval/fixtures.py.")) -> None:
    """Run the Supervisor's OWN synthesis reasoning against a fixture pair
    of specialist findings, with no live call into Project 01 or 09.

    This is how the Supervisor's genuinely new logic gets tested live
    against the free local Ollama model, independent of whether Project
    01/09's own Gemini quota happens to be available today.
    """
    fixture = next((f for f in ALL_FIXTURES if f.name == scenario), None)
    if fixture is None:
        console.print(f"[bold red]Unknown scenario '{scenario}'.[/] Known: {[f.name for f in ALL_FIXTURES]}")
        raise typer.Exit(code=1)

    config = load_config()
    console.print(f"[bold]Synthesizing fixture scenario '{scenario}' (LLM provider: {config.llm_provider})...[/]")
    client = build_llm_client(config)
    try:
        synthesis = synthesize(client, fixture.question, fixture.findings, unavailable=[])
    except (DailyQuotaExhausted, OllamaUnavailable) as exc:
        console.print(f"[bold red]Stopped: {exc}[/]")
        raise typer.Exit(code=1)

    from execos.supervisor.grounding import validate_synthesis_grounding

    violations = validate_synthesis_grounding(synthesis, fixture.findings)

    console.print(f"\n[bold]Expected connection:[/] {fixture.expected_connection_found}")
    console.print(f"[bold]Predicted connection:[/] {synthesis.cross_domain_connection_found} ({synthesis.connection_confidence})")
    console.print(f"[bold]Reasoning:[/] {synthesis.connection_reasoning}")
    for c in synthesis.claims:
        console.print(f"  [{c.claim_type.value.upper()}] {c.statement} (based on: {c.based_on_finding_ids})")
    console.print(f"\n[bold]Grounding:[/] {'PASSED' if not violations else 'FAILED — ' + str(violations)}")


@app.command(name="eval")
def eval_cmd() -> None:
    """Run the Supervisor's synthesis reasoning against both fixture scenarios; report accuracy and false-correlation rate."""
    from execos.eval.harness import run_synthesis_eval

    config = load_config()
    console.print(f"[bold]Running synthesis eval over {len(ALL_FIXTURES)} fixture scenarios (LLM provider: {config.llm_provider})...[/]\n")
    client = build_llm_client(config)
    try:
        summary = run_synthesis_eval(client)
    except (DailyQuotaExhausted, OllamaUnavailable) as exc:
        console.print(f"[bold red]Stopped: {exc}[/]")
        raise typer.Exit(code=1)

    table = Table(title="Eval: Synthesis Results")
    table.add_column("Scenario")
    table.add_column("Expected")
    table.add_column("Predicted")
    table.add_column("Grounded")
    for r in summary.results:
        table.add_row(
            r.scenario.name, str(r.scenario.expected_connection_found), str(r.synthesis.cross_domain_connection_found),
            "[green]yes[/]" if not r.grounding_violations else "[red]no[/]",
        )
    console.print(table)

    console.print(f"\n[bold]Accuracy:[/] {summary.accuracy:.0%}")
    console.print(f"[bold]False correlation rate:[/] {summary.false_correlation_rate:.0%} (Section 131's critical negative metric)")
    console.print(f"[bold]Grounding pass rate:[/] {summary.grounding_pass_rate:.0%}")


if __name__ == "__main__":
    app()
