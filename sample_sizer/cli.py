"""Click CLI for sample-sizer."""

import json
import sys

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .calculator import calculate
from .models import (
    EffectSize,
    Homogeneity,
    ResearchMethod,
    SampleSizeInput,
    UsabilityGoal,
)

console = Console()

_METHOD_CHOICES = [m.value for m in ResearchMethod]
_HOMOGENEITY_CHOICES = [h.value for h in Homogeneity]
_EFFECT_CHOICES = [e.value for e in EffectSize]
_USABILITY_CHOICES = [u.value for u in UsabilityGoal]


# --------------------------------------------------------------------------- #
# CLI group
# --------------------------------------------------------------------------- #


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """sample-sizer: AI-assisted sample size calculator for product research.

    Covers 10 research methods across qualitative, quantitative, and mixed
    designs. Rule-based by default; add --llm-backend for narrative enrichment.
    """


# --------------------------------------------------------------------------- #
# calculate command
# --------------------------------------------------------------------------- #


@cli.command("calculate")
@click.argument("method", type=click.Choice(_METHOD_CHOICES, case_sensitive=False))
@click.option(
    "--homogeneity",
    type=click.Choice(_HOMOGENEITY_CHOICES),
    default="mixed",
    show_default=True,
    help="Participant pool homogeneity (qualitative methods).",
)
@click.option(
    "--usability-goal",
    type=click.Choice(_USABILITY_CHOICES),
    default="formative",
    show_default=True,
    help="Usability testing goal (formative / summative / benchmark).",
)
@click.option(
    "--confidence",
    type=float,
    default=0.95,
    show_default=True,
    help="Confidence level: 0.90, 0.95, or 0.99.",
)
@click.option(
    "--margin-of-error",
    type=float,
    default=0.05,
    show_default=True,
    help="Margin of error for surveys / tree testing.",
)
@click.option(
    "--proportion",
    type=float,
    default=0.5,
    show_default=True,
    help="Expected proportion (0–1) for proportion-based methods.",
)
@click.option(
    "--power",
    type=float,
    default=0.80,
    show_default=True,
    help="Desired statistical power (0.70–0.95).",
)
@click.option(
    "--effect-size",
    type=click.Choice(_EFFECT_CHOICES),
    default="medium",
    show_default=True,
    help="Expected effect size.",
)
@click.option(
    "--population",
    type=int,
    default=None,
    help="Known finite population size (enables correction for surveys).",
)
@click.option(
    "--goal",
    type=str,
    default="",
    help="Study goal or context (used by LLM narrative).",
)
@click.option(
    "--llm-backend",
    type=str,
    default=None,
    help="LLM backend for narrative: openai | anthropic | gemini.",
)
@click.option("--json-output", is_flag=True, help="Emit results as JSON.")
def calculate_cmd(
    method,
    homogeneity,
    usability_goal,
    confidence,
    margin_of_error,
    proportion,
    power,
    effect_size,
    population,
    goal,
    llm_backend,
    json_output,
):
    """Calculate sample size for METHOD.

    METHOD is one of: interviews, focus_groups, diary_study, usability_test,
    card_sorting, tree_testing, survey, ab_test, experiment, correlation.
    """
    inp = SampleSizeInput(
        method=ResearchMethod(method),
        homogeneity=Homogeneity(homogeneity),
        usability_goal=UsabilityGoal(usability_goal),
        confidence_level=confidence,
        margin_of_error=margin_of_error,
        expected_proportion=proportion,
        power=power,
        effect_size=EffectSize(effect_size),
        population_size=population,
        study_goal=goal,
        llm_backend=llm_backend,
    )

    result = calculate(inp)

    if llm_backend:
        try:
            from .llm import enrich_with_llm

            result = enrich_with_llm(inp, result, llm_backend)
        except Exception as exc:
            if not json_output:
                console.print(f"[yellow]Warning: LLM enrichment failed — {exc}[/yellow]")

    # ------------------------------------------------------------------ JSON
    if json_output:
        click.echo(
            json.dumps(
                {
                    "method": result.method.value,
                    "method_type": result.method_type.value,
                    "recommended_n": result.recommended_n,
                    "min_n": result.min_n,
                    "max_n": result.max_n,
                    "rationale": result.rationale,
                    "power_notes": result.power_notes,
                    "caveats": result.caveats,
                    "confidence_level": result.confidence_level,
                    "actual_power": result.actual_power,
                    "narrative": result.narrative,
                },
                indent=2,
            )
        )
        return

    # ------------------------------------------------------------------ Rich
    method_label = method.replace("_", " ").title()
    type_label = result.method_type.value.title()

    console.print()
    console.print(
        Panel(
            f"[bold]{method_label}[/bold]  ·  {type_label}",
            title="[bold]sample-sizer[/bold]",
            border_style="dim",
            padding=(0, 2),
        )
    )
    console.print()

    # Sample size table
    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
    tbl.add_column("Range", style="dim", min_width=14)
    tbl.add_column("N", justify="right", min_width=8)
    tbl.add_row("Minimum", str(result.min_n))
    tbl.add_row(
        "[bold green]Recommended[/bold green]",
        f"[bold green]{result.recommended_n}[/bold green]",
    )
    tbl.add_row("Maximum", str(result.max_n))
    console.print(tbl)

    console.print("[bold]Rationale[/bold]")
    console.print(f"  {result.rationale}\n")

    console.print("[bold]Power / saturation[/bold]")
    console.print(f"  {result.power_notes}\n")

    if result.caveats:
        console.print("[bold]Caveats[/bold]")
        for c in result.caveats:
            console.print(f"  · {c}")
        console.print()

    if result.narrative:
        console.print(
            Panel(
                result.narrative,
                title="[bold blue]AI Narrative[/bold blue]",
                border_style="blue",
                padding=(0, 2),
            )
        )
        console.print()


# --------------------------------------------------------------------------- #
# batch command
# --------------------------------------------------------------------------- #


@cli.command("batch")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--llm-backend", type=str, default=None)
@click.option("--output", type=click.Path(), default=None, help="Write JSON results to file.")
def batch_cmd(input_file, llm_backend, output):
    """Run multiple sample size calculations from a JSON file.

    INPUT_FILE must be a JSON array of objects with at least a "method" key.
    All other keys are optional and mirror the --flags of the calculate command.
    """
    with open(input_file) as fh:
        items = json.load(fh)

    if not isinstance(items, list):
        console.print("[red]Error: input file must be a JSON array.[/red]")
        sys.exit(1)

    results = []
    for item in items:
        try:
            inp = SampleSizeInput(
                method=ResearchMethod(item["method"]),
                homogeneity=Homogeneity(item.get("homogeneity", "mixed")),
                usability_goal=UsabilityGoal(item.get("usability_goal", "formative")),
                confidence_level=item.get("confidence_level", 0.95),
                margin_of_error=item.get("margin_of_error", 0.05),
                expected_proportion=item.get("expected_proportion", 0.5),
                power=item.get("power", 0.80),
                effect_size=EffectSize(item.get("effect_size", "medium")),
                population_size=item.get("population_size"),
                study_goal=item.get("study_goal", ""),
            )
            result = calculate(inp)
            if llm_backend:
                try:
                    from .llm import enrich_with_llm

                    result = enrich_with_llm(inp, result, llm_backend)
                except Exception:
                    pass
            results.append(
                {
                    "method": result.method.value,
                    "method_type": result.method_type.value,
                    "recommended_n": result.recommended_n,
                    "min_n": result.min_n,
                    "max_n": result.max_n,
                    "rationale": result.rationale,
                    "narrative": result.narrative,
                }
            )
        except Exception as exc:
            results.append({"method": item.get("method", "unknown"), "error": str(exc)})

    out = json.dumps(results, indent=2)
    if output:
        with open(output, "w") as fh:
            fh.write(out)
        console.print(f"[green]Results written to {output}[/green]")
    else:
        click.echo(out)
