"""Simple evaluation CLI for structured outputs."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print as rich_print

from .metrics import order_kendall_tau, provenance_coverage, set_prf1

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


@app.command()
def cli(
    pred: Path = typer.Option(..., exists=True, readable=True, dir_okay=False),
    gold: Path = typer.Option(..., exists=True, readable=True, dir_okay=False),
) -> None:
    """Compare predictions against reference silver labels."""

    predictions = _load_jsonl(pred)
    golds = _load_jsonl(gold)
    npc_scores: list[float] = []
    taus: list[float] = []
    provs: list[float] = []

    for prediction, reference in zip(predictions, golds):
        npc_scores.append(
            set_prf1(
                [npc.get("name", "") for npc in prediction.get("npcs", [])],
                [npc.get("name", "") for npc in reference.get("npcs", [])],
            )["f1"]
        )
        taus.append(
            order_kendall_tau(
                [evt.get("title", "") for evt in prediction.get("timeline", [])],
                [evt.get("title", "") for evt in reference.get("events", [])],
            )["kendall_tau"]
        )
        provs.append(
            provenance_coverage(prediction.get("timeline", []))["prov_coverage"]
        )

    def _avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    rich_print(
        {
            "npc_f1": _avg(npc_scores),
            "timeline_tau": _avg(taus),
            "timeline_provenance": _avg(provs),
        }
    )


if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
