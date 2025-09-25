# D&D Session Summary Generator

This project processes raw Dungeons & Dragons session transcripts and produces structured
analysis artifacts plus natural-language summaries. The existing Gemini-based pipeline lives in
`src/dnd_summary`, while the new modular **DSPy** tooling is available under `src/dspy_dnd`.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd dnd-summary-project
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure API keys:**
    -   Copy `.env.example` to `.env` and add the credentials required for your chosen LLM
        provider (Google for the legacy pipeline, OpenAI/Anthropic/etc. for DSPy experiments).

## Legacy Gemini Pipeline

To generate a narrative summary for a specific session using the original Gemini workflow, run:

```bash
python -m src.scripts.run_summary 32
```

Replace `32` with the desired session number.

## DSPy Modular Analysis

The `dspy_dnd` package exposes a structured analysis pipeline that outputs a single JSON artifact.

```bash
# Generate heuristic silver labels (placeholder heuristics)
python -m src.dspy_dnd.labeling.silver_labels --in transcripts --out data/silver

# (Optional) compile prompts with DSPy teleprompting
python -m src.dspy_dnd.compile --train data/silver/silver.jsonl

# Run the analyzer on an example transcript/background/overview trio
python -m src.dspy_dnd.run \
  --transcript examples/minimal_transcript.txt \
  --background examples/avarias_background.txt \
  --overview examples/campaign_overview.txt \
  --out out/example.analysis.json

# Evaluate predictions against silver labels
python -m src.dspy_dnd.eval.run --pred out/preds.jsonl --gold data/silver/silver.jsonl
```

The output schema is defined in `src/dspy_dnd/types.py` via Pydantic models. The orchestrating
`SessionAnalyzer` module in `src/dspy_dnd/program.py` composes DSPy sub-modules for NPCs, timeline,
dialogue, mechanics, and more, producing a DB-ready artifact.

## Testing

Run the full test suite before committing changes:

```bash
pytest
```
