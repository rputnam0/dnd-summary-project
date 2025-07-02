"""
Configuration for the D&D session summary generator.
"""

import os

# --- Project Root ---
# Ensures paths are relative to the project's root directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Configuration ---
# Environment variable name for the Google API Key
API_KEY_ENV = "GOOGLE_API_KEY"

# Subdirectory Definitions (relative to PROJECT_ROOT - CASE SENSITIVE)
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")
TRANSCRIPTS_DIR = os.path.join(PROJECT_ROOT, "transcripts")
SESSIONS_DIR = os.path.join(PROJECT_ROOT, "sessions")


# LLM Configuration
MODEL_NAME = "gemini-1.5-pro"  # Or your preferred model
CALLS_PER_MINUTE = 5  # Rate limit to avoid API errors
DELAY_SECONDS = 60.0 / CALLS_PER_MINUTE

# Static File Paths (Base Inputs located in PROMPTS_DIR)
# These are the core templates and background info.
ANALYSIS_SYSTEM_PROMPT_FILE = os.path.join(PROMPTS_DIR, "analysis_system_prompt.txt")
ANALYSIS_PROMPT_TEMPLATE_FILE = os.path.join(
    PROMPTS_DIR, "analysis_prompt_template.txt"
)
AVARIAS_BACKGROUND_FILE = os.path.join(PROMPTS_DIR, "avarias_background.txt")
# This is the BASE/FALLBACK overview, never overwritten by the main script flow.
# Used for Session 1 or if a previous session's CO is missing.
BASE_CAMPAIGN_OVERVIEW_FILE = os.path.join(PROMPTS_DIR, "campaign_overview.txt")
SESSION_ANALYSIS_INSTRUCTIONS_FILE = os.path.join(
    PROMPTS_DIR, "session_analysis_instructions.txt"
)
ANALYSIS_EXAMPLE_FILE = os.path.join(PROMPTS_DIR, "analysis_example.txt")
# Template for updating the Campaign Overview (CO)
CO_PROMPT_TEMPLATE_FILE = os.path.join(PROMPTS_DIR, "co_prompt_template.txt")
# Templates and instructions for generating the session summary
SUMMARY_SYSTEM_PROMPT_FILE = os.path.join(PROMPTS_DIR, "summary_system_prompt.txt")
SUMMARY_PROMPT_TEMPLATE_FILE = os.path.join(PROMPTS_DIR, "summary_prompt_template.txt")
SUMMARY_INSTRUCTIONS_FILE = os.path.join(PROMPTS_DIR, "summary_instructions.txt")