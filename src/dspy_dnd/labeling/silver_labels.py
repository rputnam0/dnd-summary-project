"""Generate heuristic silver labels for transcripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

import typer
from rich import print as rich_print

NAME_PATTERN = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b")

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _candidate_names(text: str) -> List[str]:
    """Very naive proper-noun miner; replace with stronger heuristics later."""

    raw = {match.group(1) for match in NAME_PATTERN.finditer(text)}
    blacklist = {"GM", "DM", "Chapter", "Timestamp", "Narrator", "Scene"}
    return sorted(name for name in raw if name not in blacklist and len(name) > 2)


@app.command()
def cli(
    inp: Path = typer.Option(..., "--in", exists=True, dir_okay=True, file_okay=False),
    out: Path = typer.Option(..., "--out", dir_okay=True, file_okay=True),
) -> None:
    """Create placeholder silver labels for each transcript in ``inp``."""

    if out.is_dir() or str(out).endswith("/"):
        out.mkdir(parents=True, exist_ok=True)
        outfile = out / "silver.jsonl"
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        outfile = out

    count = 0
    with outfile.open("w") as handle:
        for transcript_file in sorted(inp.glob("*.txt")):
            text = transcript_file.read_text()
            npcs = [{"name": name} for name in _candidate_names(text)]
            entry = {
                "transcript_id": transcript_file.stem,
                "npcs": npcs,
                "events": [],  # TODO: populate via heuristics / LLM ensemble
            }
            handle.write(json.dumps(entry) + "\n")
            count += 1

    rich_print(f"[green]Wrote[/green] {count} silver items -> {outfile}")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
