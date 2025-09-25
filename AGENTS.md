# D&D Summary Project — Contributor Guide

## Project Overview
This repository contains a Python application that turns raw Dungeons & Dragons session transcripts into structured analyses, campaign overview updates, and concise summaries. The current implementation orchestrates Google Gemini (via `google-generativeai`) to perform the language modeling steps. The long-term roadmap is to evolve this codebase into a **dspy-powered, prompt-optimized summarization toolkit** that can iteratively improve prompts, evaluate outputs, and surface the best-performing summary strategies.

## Key Components
- **`src/dnd_summary/`** – Core library code used for reading inputs, invoking the LLM, and writing outputs.
  - `config.py` centralizes filesystem paths.
  - `file_handler.py` locates transcripts and prepares file IO.
  - `llm_handler.py` wraps LLM calls (currently Gemini, future-friendly for dspy).
  - `main.py` provides the orchestration pipeline.
  - `utils.py` collects shared helpers (e.g., session number parsing).
- **`src/scripts/run_summary.py`** – CLI entry point that calls into the main pipeline.
- **`transcripts/`, `prompts/`, `sessions/`** – Working data directories for raw inputs, prompt templates, and generated outputs.
- **`tests/`** – Pytest suite covering the core behaviors. Expand alongside new functionality.
- **`requirements.txt`** – Runtime dependencies; expect this to grow as we introduce `dspy` and optimization tooling.

## Development Workflow
1. **Environment** – Use Python 3.10+ and install dependencies with `pip install -r requirements.txt`. Create a virtual environment when possible.
2. **Secrets** – Copy `.env.example` to `.env` and add `GOOGLE_API_KEY` (or other keys as we add providers).
3. **Running the Pipeline** – `python -m src.scripts.run_summary <session_number>` processes a session end-to-end.
4. **Testing** – Run `pytest` before pushing any change. Add or update tests whenever you change logic or add features. When an
   external LLM is required, standardize on the latest Gemini 2.5 Flash model to keep evaluations consistent.
5. **Formatting & Style** – Keep code readable, favor small functions, and add docstrings for any non-trivial utilities. As we integrate dspy, encapsulate prompt-building and optimization steps in clearly named modules.
6. **Future DSPy Integration** – When adding dspy components:
   - Separate model wiring, prompt templates, and evaluation logic.
   - Expose configuration hooks (CLI flags or config files) so experiments are reproducible.
   - Document new workflows inside this file and the README.

## Contribution Tips
- Prefer pure functions and dependency injection to keep components testable.
- Log meaningful milestones in the CLI output so users can trace processing steps.
- When adding datasets or prompts, place them in well-named subdirectories and update references in `config.py`.
- Use feature branches for longer efforts, but keep commits focused and well-described.

Keeping this guide up to date will help future contributors ramp quickly as the project grows into a fully optimized, dspy-driven summarization system.
