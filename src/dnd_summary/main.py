
"""
Main execution logic for the D&D session summary generator.
"""

import os
import sys
import argparse

from .config import (
    PROMPTS_DIR,
    TRANSCRIPTS_DIR,
    SESSIONS_DIR,
    BASE_CAMPAIGN_OVERVIEW_FILE,
)
from .file_handler import find_transcript_file
from .llm_handler import (
    generate_analysis,
    update_campaign_overview,
    generate_summary,
)
from .utils import get_session_number

def main():
    """Main function to run the session summary generation process."""
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Generate D&D session analysis, campaign overview update, and summary."
    )
    parser.add_argument(
        "session_identifier",
        nargs="?",
        help="Optional: The session number or identifier (e.g., '32', 'Session 32').",
    )
    args = parser.parse_args()

    # --- Fallback Input Prompt ---
    if not args.session_identifier:
        try:
            user_input = input(
                "Please enter the session identifier (e.g., '32', 'Session 32'): "
            ).strip()
            if not user_input:
                print("❗️ No session identifier provided. Exiting.", file=sys.stderr)
                sys.exit(1)
            args.session_identifier = user_input
        except (EOFError, KeyboardInterrupt):
            print("\n❗️ Input cancelled by user. Exiting.", file=sys.stderr)
            sys.exit(1)

    # --- Initial Directory Checks ---
    if not os.path.isdir(PROMPTS_DIR):
        print(f"❌ Critical Error: Prompts directory not found.", file=sys.stderr)
        print(f"   Expected location: {PROMPTS_DIR}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(TRANSCRIPTS_DIR):
        print(f"❌ Critical Error: Transcripts directory not found.", file=sys.stderr)
        print(f"   Expected location: {TRANSCRIPTS_DIR}", file=sys.stderr)
        sys.exit(1)

    print("--- Session Analysis & Summary Generator ---")

    # --- Process Session Identifier ---
    session_number = get_session_number(args.session_identifier)

    # --- Construct Session Identifiers ---
    session_number_str = str(session_number)
    session_file_prefix = f"session_{session_number_str}"
    session_folder_title = f"Session {session_number_str}"

    # --- Find Transcript File ---
    transcript_file = find_transcript_file(session_number)
    if transcript_file is None:
        sys.exit(1)

    # --- Define Session-Specific Output Paths ---
    output_folder = os.path.join(SESSIONS_DIR, session_folder_title)
    analysis_output_file = os.path.join(
        output_folder, f"{session_file_prefix}_analysis_output.txt"
    )
    co_output_file = os.path.join(
        output_folder, f"{session_file_prefix}_campaign_overview.txt"
    )
    summary_output_file = os.path.join(
        output_folder, f"{session_file_prefix}_summary_output.txt"
    )

    # --- Determine the INPUT Campaign Overview Path ---
    previous_co_input_path = ""
    if session_number > 0:
        prev_session_number_str = str(session_number - 1)
        prev_session_file_prefix = f"session_{prev_session_number_str}"
        prev_session_folder_title = f"Session {prev_session_number_str}"
        potential_prev_co_path = os.path.join(
            SESSIONS_DIR,
            prev_session_folder_title,
            f"{prev_session_file_prefix}_campaign_overview.txt",
        )
        if os.path.exists(potential_prev_co_path):
            previous_co_input_path = potential_prev_co_path
            print(
                f"ℹ️ Using Campaign Overview from previous session: ''{os.path.basename(previous_co_input_path)}''"
            )
        else:
            previous_co_input_path = BASE_CAMPAIGN_OVERVIEW_FILE
            print(
                f"ℹ️ Previous session CO not found. Falling back to base: ''{os.path.basename(previous_co_input_path)}''"
            )
            if not os.path.exists(previous_co_input_path):
                print(
                    f"⚠️ Warning: Base campaign overview file ''{previous_co_input_path}'´ not found! Processing may fail.",
                    file=sys.stderr,
                )
    else:
        previous_co_input_path = BASE_CAMPAIGN_OVERVIEW_FILE
        print(
            f"ℹ️ Session number <= 0 or first session. Using base campaign overview: ''{os.path.basename(previous_co_input_path)}''"
        )
        if not os.path.exists(previous_co_input_path):
            print(
                f"⚠️ Warning: Base campaign overview file ''{previous_co_input_path}'´ not found! Processing may fail.",
                file=sys.stderr,
            )

    # --- Display Configuration ---
    print(f"\n🔧 Configuration:")
    print(f"   - Session Number: {session_number}")
    print(f"   - Transcript File: ''{os.path.basename(transcript_file)}'´")
    print(
        f"   - Input CO File Used: ''{os.path.basename(previous_co_input_path)}'´ (from {os.path.dirname(previous_co_input_path)})"
    )
    print(f"   - Output Folder: ''{output_folder}'´")
    print(f"   - Analysis Output Target: ''{os.path.basename(analysis_output_file)}'´")
    print(f"   - CO Output Target: ''{os.path.basename(co_output_file)}'´")
    print(f"   - Summary Output Target: ''{os.path.basename(summary_output_file)}'´")

    # --- Create Output Directory ---
    try:
        print(f"\n📁 Ensuring output directory exists: ''{output_folder}'´")
        os.makedirs(output_folder, exist_ok=True)
    except OSError as e:
        print(
            f"❌ Error creating output directory ''{output_folder}'´: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Run Generation Steps ---
    print("\n--- Starting Generation Process ---")

    analysis_ok = False
    co_update_ok = False
    summary_ok = False

    print("\n--- Step 1: Generating Session Analysis ---")
    analysis_ok = generate_analysis(
        transcript_file,
        previous_co_input_path,
        analysis_output_file,
    )

    if analysis_ok:
        print("\n--- Step 2: Updating Campaign Overview ---")
        co_update_ok = update_campaign_overview(
            previous_co_input_path,
            analysis_output_file,
            co_output_file,
        )
    else:
        print("\n⚠️ Analysis generation failed. Skipping subsequent steps.")

    if co_update_ok:
        print("\n--- Step 3: Generating Session Summary ---")
        summary_ok = generate_summary(
            transcript_file,
            analysis_output_file,
            co_output_file,
            summary_output_file,
        )
    elif analysis_ok and not co_update_ok:
        print("\n⚠️ Campaign Overview update failed. Skipping summary generation.")

    # --- Final Status ---
    print("\n--- Generation Process Finished ---")
    if analysis_ok and co_update_ok and summary_ok:
        print(f"✅ Process completed for Session {session_number}.")
        print(f"   Outputs are in: ''{output_folder}'´")
        print(
            f"   (Note: Some steps may have been skipped if output files already existed.)"
        )
    else:
        print(
            f"⚠️ Process completed with errors or was interrupted for Session {session_number}."
        )
        print(
            f"   Check logs above for details. Any generated files are in: ''{output_folder}'´"
        )
