"""DSPy teleprompt compilation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional

import dspy
import typer
from rich import print as rich_print

from .program import SessionAnalyzer
from .eval.metrics import order_kendall_tau, provenance_coverage, set_prf1

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def npc_metric(example: dict, pred: dict) -> float:
    """Compute F1 between predicted and reference NPC names."""

    try:
        pred_names = [npc.get("name", "") for npc in pred.get("npcs", [])]
        gold_names = [npc.get("name", "") for npc in example.get("npcs", [])]
        return set_prf1(pred_names, gold_names)["f1"]
    except Exception:  # pragma: no cover - defensive guard
        return 0.0


def timeline_metric(example: dict, pred: dict) -> float:
    """Blend ordering quality and provenance coverage."""

    try:
        pred_titles = [evt.get("title", "") for evt in pred.get("timeline", [])]
        gold_titles = [evt.get("title", "") for evt in example.get("events", [])]
        tau = order_kendall_tau(pred_titles, gold_titles)["kendall_tau"]
        prov = provenance_coverage(pred.get("timeline", []))["prov_coverage"]
        return 0.7 * tau + 0.3 * prov
    except Exception:  # pragma: no cover - defensive guard
        return 0.0


@app.command()
def cli(
    train: Path = typer.Option(..., exists=True, readable=True, dir_okay=False, help="Training JSONL"),
    dev: Optional[Path] = typer.Option(
        None, exists=True, readable=True, dir_okay=False, help="Optional dev JSONL"
    ),
    model: str = typer.Option("openai/gpt-4o-mini", help="Language model identifier"),
    trials: int = typer.Option(40, help="Teleprompt search trials"),
) -> None:
    """Compile the session analyzer against silver labels using DSPy."""

    lm = dspy.LM(model=model) if hasattr(dspy, "LM") else dspy.OpenAI(model=model)
    dspy.settings.configure(lm=lm)

    trainset = _load_jsonl(train)
    devset = _load_jsonl(dev) if dev else None

    program = SessionAnalyzer()
    teleprompter = dspy.teleprompt.BootstrapFewShotWithRandomSearch(
        num_trials=trials,
        max_labeled_data=min(200, len(trainset)),
        metric=lambda example, pred: (npc_metric(example, pred) + timeline_metric(example, pred))
        / 2.0,
    )
    compiled_program = teleprompter.compile(program, trainset=trainset, valset=devset)

    if hasattr(compiled_program, "save"):  # pragma: no cover - depends on DSPy version
        compiled_program.save("compiled_program.json")
        rich_print("[green]Compilation complete.[/green] Saved to compiled_program.json")
    else:
        rich_print("[green]Compilation complete.[/green] DSPy version does not expose save().")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
