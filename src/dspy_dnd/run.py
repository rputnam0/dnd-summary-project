"""Command line interface to run the DSPy session analyzer."""

from __future__ import annotations

import json
from pathlib import Path

import dspy
import typer
from rich import print as rich_print

from .program import SessionAnalyzer
from .types import AnalysisArtifact

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def cli(
    transcript: Path = typer.Option(..., exists=True, readable=True, dir_okay=False),
    background: Path = typer.Option(..., exists=True, readable=True, dir_okay=False),
    overview: Path = typer.Option(..., exists=True, readable=True, dir_okay=False),
    out: Path = typer.Option(..., dir_okay=False, writable=True),
    model: str = typer.Option("openai/gpt-4o-mini", help="Language model identifier"),
) -> None:
    """Run the session analyzer and write a JSON artifact to disk."""

    lm = dspy.LM(model=model) if hasattr(dspy, "LM") else dspy.OpenAI(model=model)
    dspy.settings.configure(lm=lm)

    transcript_text = transcript.read_text()
    background_text = background.read_text()
    overview_text = overview.read_text()

    analyzer = SessionAnalyzer()
    result = analyzer(
        transcript=transcript_text,
        avarias_background=background_text,
        campaign_overview=overview_text,
    )

    artifact = AnalysisArtifact(**result).model_dump()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2))

    rich_print(f"[green]Analysis written to[/green] {out}")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
