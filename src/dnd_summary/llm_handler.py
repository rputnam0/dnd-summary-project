
"""
Handles interactions with the Google GenAI API.
"""

import os
import sys
import re
import time

import google.generativeai as genai

from .config import (
    API_KEY_ENV,
    MODEL_NAME,
    DELAY_SECONDS,
    ANALYSIS_SYSTEM_PROMPT_FILE,
    ANALYSIS_PROMPT_TEMPLATE_FILE,
    AVARIAS_BACKGROUND_FILE,
    SESSION_ANALYSIS_INSTRUCTIONS_FILE,
    ANALYSIS_EXAMPLE_FILE,
    CO_PROMPT_TEMPLATE_FILE,
    SUMMARY_SYSTEM_PROMPT_FILE,
    SUMMARY_PROMPT_TEMPLATE_FILE,
    SUMMARY_INSTRUCTIONS_FILE,
)
from .file_handler import read_file

def init_client():
    """Initializes and returns the GenAI client using API key from environment."""
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        print(f"❌ Error: Environment variable {API_KEY_ENV} not set.", file=sys.stderr)
        print(
            f"   Please set the {API_KEY_ENV} environment variable with your API key.",
            file=sys.stderr,
        )
        return None
    try:
        # Instantiate a Gemini Developer API client
        client = genai.Client(api_key=api_key)
        return client

    except Exception as e:
        print(f"❌ Error initializing GenAI client: {e}", file=sys.stderr)
        return None

def generate_analysis(
    transcript_file_path,  # Full path to the session's transcript
    previous_co_input_path,  # Path to the Campaign Overview to USE as input (previous session's or base)
    analysis_output_path,  # Full path for the FINAL analysis output file for this session
):
    """
    Generates the session analysis using the transcript and the relevant campaign overview.
    Skips generation if the output file already exists.
    """
    # Skip if output already exists
    if os.path.exists(analysis_output_path):
        print(
            f"✔️  Analysis already exists: ''{os.path.basename(analysis_output_path)}'´, skipping generation."
        )
        return True  # Indicate success (skipped)

    print(
        f"⏳ Loading files for analysis of ''{os.path.basename(transcript_file_path)}''..."
    )
    # Load static prompt components
    analysis_system_prompt = read_file(ANALYSIS_SYSTEM_PROMPT_FILE)
    analysis_prompt_template = read_file(ANALYSIS_PROMPT_TEMPLATE_FILE)
    avarias_bg = read_file(AVARIAS_BACKGROUND_FILE)
    session_analysis_inst = read_file(SESSION_ANALYSIS_INSTRUCTIONS_FILE)
    analysis_example = read_file(ANALYSIS_EXAMPLE_FILE)

    # Load dynamic/specific inputs for this session
    campaign_ovw = read_file(
        previous_co_input_path
    )  # Load the specific CO (previous or base)
    session_trans = read_file(transcript_file_path)

    # Validate all required files were loaded
    if None in [
        analysis_system_prompt,
        analysis_prompt_template,
        avarias_bg,
        campaign_ovw,
        session_analysis_inst,
        analysis_example,
        session_trans,
    ]:
        print(
            f"❌ Aborting analysis due to file loading errors. Check required prompt files and inputs:",
            file=sys.stderr,
        )
        print(f"   Transcript: {transcript_file_path}", file=sys.stderr)
        print(f"   Input CO: {previous_co_input_path}", file=sys.stderr)
        return False  # Indicate failure

    print("⚙️  Formatting analysis prompt...")
    try:
        # Populate the analysis prompt template
        user_prompt = analysis_prompt_template.format(
            avarias_bg=avarias_bg,
            campaign_ovw=campaign_ovw,  # Injects the content from the previous session/base CO
            session_trans=session_trans,
            session_analysis_inst=session_analysis_inst,
            analysis_example=analysis_example,
        )
    except KeyError as e:
        print(
            f"❌ Analysis template placeholder error: Missing key {e}. Check ''{ANALYSIS_PROMPT_TEMPLATE_FILE}'´.",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(f"❌ Error formatting analysis template: {e}", file=sys.stderr)
        return False

    client = init_client()
    if not client:
        return False  # Indicate failure (client init failed)

    print(f"🤖 Generating analysis via LLM ({MODEL_NAME})...")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                genai.types.Content(
                    role="user", parts=[genai.types.Part.from_text(text=user_prompt)]
                )
            ],
            config=genai.types.GenerateContentConfig(
                response_mime_type="text/plain",
                system_instruction=[analysis_system_prompt],
            ),
        )
        analysis_text = response.text

        # Check for blocked prompt
        if (
            not analysis_text
            and hasattr(response, "prompt_feedback")
            and response.prompt_feedback.block_reason
        ):
            print(
                f"❌ LLM blocked prompt during analysis: {response.prompt_feedback.block_reason}",
                file=sys.stderr,
            )
            if hasattr(response.prompt_feedback, "block_reason_message"):
                print(
                    f"   Reason: {response.prompt_feedback.block_reason_message}",
                    file=sys.stderr,
                )
            return False

    except AttributeError:
        # Handle cases where the response structure might differ unexpectedly
        print(
            f"❌ LLM response object structure unexpected. Response: {response}",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(
            f"❌ LLM API call failed during analysis generation: {e}", file=sys.stderr
        )
        return False

    print(f"💾 Saving analysis to ''{analysis_output_path}''...")
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(analysis_output_path), exist_ok=True)
        # Write the generated analysis to its final destination
        with open(analysis_output_path, "w", encoding="utf-8") as f:
            f.write(analysis_text)
    except Exception as e:
        print(
            f"❌ Error writing analysis output to ''{analysis_output_path}'´: {e}",
            file=sys.stderr,
        )
        return False

    print(f"✅ Analysis saved successfully.")
    print(f"⏱ Sleeping {DELAY_SECONDS:.1f}s before next step...")
    time.sleep(DELAY_SECONDS)
    return True  # Indicate success

def update_campaign_overview(
    previous_co_input_path,  # Path to the Campaign Overview to USE as input (previous session's or base)
    session_analysis_path,  # Path to the generated session analysis for THIS session
    final_co_output_path,  # Path to save the FINAL updated overview file for THIS session
):
    """
    Updates the campaign overview based on the session analysis.
    Uses the Campaign Overview from the previous step (or base) as input.
    Skips generation if the final output file already exists.
    """
    # Skip if output already exists
    if os.path.exists(final_co_output_path):
        print(
            f"✔️  Updated Campaign Overview already exists: ''{os.path.basename(final_co_output_path)}'´, skipping generation."
        )
        return True  # Indicate success (skipped)

    print(f"\n⏳ Loading files for Campaign Overview update...")
    # Load the CO update prompt template
    co_prompt_template_text = read_file(CO_PROMPT_TEMPLATE_FILE)

    # Load dynamic inputs: the previous CO and the analysis for this session
    previous_campaign_overview = read_file(previous_co_input_path)
    session_analysis = read_file(
        session_analysis_path
    )  # Analysis generated in the previous step

    # Ensure the analysis file actually exists (it should if generate_analysis succeeded/skipped)
    if not os.path.exists(session_analysis_path):
        print(
            f"❌ Cannot update Campaign Overview: Session Analysis file not found at ''{session_analysis_path}'´. Run analysis first.",
            file=sys.stderr,
        )
        return False

    # Validate all required files/content were loaded
    if None in [co_prompt_template_text, previous_campaign_overview, session_analysis]:
        print(
            f"❌ Aborting Campaign Overview update due to file loading errors. Check required prompt files and inputs:",
            file=sys.stderr,
        )
        print(f"   Analysis: {session_analysis_path}", file=sys.stderr)
        print(f"   Input CO: {previous_co_input_path}", file=sys.stderr)
        return False  # Indicate failure

    print("⚙️  Formatting Campaign Overview update prompt...")
    try:
        # Populate the CO update template using the loaded content
        # Assumes CO_PROMPT_TEMPLATE_FILE contains {previous_campaign_overview} and {session_analysis} placeholders
        user_prompt = co_prompt_template_text.format(
            previous_campaign_overview=previous_campaign_overview,
            session_analysis=session_analysis,
        )
    except KeyError as e:
        print(
            f"❌ Campaign Overview template placeholder error: Missing key {e}. Check ''{CO_PROMPT_TEMPLATE_FILE}'´.",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(f"❌ Error formatting Campaign Overview template: {e}", file=sys.stderr)
        return False

    client = init_client()
    if not client:
        return False  # Indicate failure

    print(f"🤖 Updating Campaign Overview via LLM ({MODEL_NAME})...")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                genai.types.Content(
                    role="user", parts=[genai.types.Part.from_text(text=user_prompt)]
                )
            ],
        )
        updated_co_text = response.text

        # --- Extract content within <campaign_overview> tags ---
        # The CO prompt template asks the LLM to only output the content within these tags.
        match = re.search(
            r"<campaign_overview>(.*?)</campaign_overview>",
            updated_co_text,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            extracted_co_text = match.group(1).strip()  # Get content inside tags
            print("ℹ️  Successfully extracted content within <campaign_overview> tags.")
        else:
            print(
                "⚠️ Warning: Could not find <campaign_overview> tags in the LLM response for CO update."
            )
            print("   Saving the full response, but manual review might be needed.")
            extracted_co_text = updated_co_text  # Save the full response as fallback

        # Check for blocked prompt
        if (
            not updated_co_text
            and hasattr(response, "prompt_feedback")
            and response.prompt_feedback.block_reason
        ):
            print(
                f"❌ LLM blocked prompt during CO update: {response.prompt_feedback.block_reason}",
                file=sys.stderr,
            )
            if hasattr(response.prompt_feedback, "block_reason_message"):
                print(
                    f"   Reason: {response.prompt_feedback.block_reason_message}",
                    file=sys.stderr,
                )
            return False

    except AttributeError:
        print(
            f"❌ LLM response object structure unexpected during CO update. Response: {response}",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(
            f"❌ LLM API call failed during CO update generation: {e}", file=sys.stderr
        )
        return False

    print(f"💾 Saving updated Campaign Overview to ''{final_co_output_path}''...")
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(final_co_output_path), exist_ok=True)
        # Write the extracted/updated CO to its final destination for this session
        with open(final_co_output_path, "w", encoding="utf-8") as f:
            f.write(extracted_co_text)
    except Exception as e:
        print(
            f"❌ Error writing updated CO output to ''{final_co_output_path}'´: {e}",
            file=sys.stderr,
        )
        return False

    print(f"✅ Updated Campaign Overview saved successfully.")
    print(f"⏱ Sleeping {DELAY_SECONDS:.1f}s before next step...")
    time.sleep(DELAY_SECONDS)
    return True  # Indicate success

def generate_summary(
    transcript_file_path,  # Full path to transcript for THIS session
    analysis_output_path,  # Full path to analysis output for THIS session
    current_session_co_path,  # Path to the UPDATED Campaign Overview for THIS session
    summary_output_path,  # Full path for the FINAL summary output file for THIS session
):
    """
    Generates the session summary using the transcript, analysis, and updated campaign overview.
    Skips generation if the output file already exists.
    """
    # Skip if output already exists
    if os.path.exists(summary_output_path):
        print(
            f"✔️  Summary already exists: ''{os.path.basename(summary_output_path)}'´, skipping generation."
        )
        return True  # Indicate success (skipped)

    # Ensure required input files from previous steps exist
    if not os.path.exists(analysis_output_path):
        print(
            f"❌ Cannot generate summary: Analysis file not found at ''{analysis_output_path}'´.",
            file=sys.stderr,
        )
        return False
    if not os.path.exists(current_session_co_path):
        print(
            f"❌ Cannot generate summary: Campaign Overview file for this session not found at ''{current_session_co_path}'´.",
            file=sys.stderr,
        )
        return False

    print(
        f"⏳ Loading files for summary of ''{os.path.basename(transcript_file_path)}''..."
    )
    # Load static prompt components
    summary_system_prompt = read_file(SUMMARY_SYSTEM_PROMPT_FILE)
    summary_prompt_template = read_file(SUMMARY_PROMPT_TEMPLATE_FILE)
    avarias_bg = read_file(AVARIAS_BACKGROUND_FILE)
    summary_inst = read_file(SUMMARY_INSTRUCTIONS_FILE)

    # Load dynamic inputs specific to this session
    campaign_ovw = read_file(
        current_session_co_path
    )  # Load the CO generated FOR THIS session
    session_trans = read_file(transcript_file_path)
    session_analysis = read_file(analysis_output_path)

    # Validate all required files/content were loaded
    if None in [
        summary_system_prompt,
        summary_prompt_template,
        avarias_bg,
        campaign_ovw,
        summary_inst,
        session_trans,
        session_analysis,
    ]:
        print(
            "❌ Aborting summary due to file loading errors. Check required prompt files and inputs:",
            file=sys.stderr,
        )
        print(f"   Analysis: {analysis_output_path}", file=sys.stderr)
        print(f"   This Session CO: {current_session_co_path}", file=sys.stderr)
        return False

    print("⚙️  Formatting summary prompt...")
    try:
        # Populate the summary prompt template
        # Assumes SUMMARY_PROMPT_TEMPLATE_FILE uses {avarias_bg}, {campaign_ovw}, {session_trans}, {session_analysis}, {summary_inst}
        summary_prompt = summary_prompt_template.format(
            avarias_bg=avarias_bg,
            campaign_ovw=campaign_ovw,  # Uses the CO updated/generated FOR THIS session
            session_trans=session_trans,
            session_analysis=session_analysis,
            summary_inst=summary_inst,
        )
    except KeyError as e:
        print(
            f"❌ Summary template placeholder error: Missing key {e}. Check ''{SUMMARY_PROMPT_TEMPLATE_FILE}'´.",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(f"❌ Error formatting summary template: {e}", file=sys.stderr)
        return False

    client = init_client()
    if not client:
        return False  # Indicate failure

    print(f"🤖 Generating summary via LLM ({MODEL_NAME})...")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                genai.types.Content(
                    role="user", parts=[genai.types.Part.from_text(text=summary_prompt)]
                )
            ],
            config=genai.types.GenerateContentConfig(
                response_mime_type="text/plain",
                system_instruction=[summary_system_prompt],
            ),
            # request_options=genai.types.RequestOptions(timeout=300)
        )
        summary_text = response.text

        # Optional: Extract content if summary prompt asks for specific tags, like <Summary>...</Summary>
        match = re.search(
            r"<Summary>(.*?)</Summary>", summary_text, re.DOTALL | re.IGNORECASE
        )
        if match:
            summary_text = match.group(1).strip()
        else:
            print(
                "⚠️ Warning: Could not find <Summary> tags in summary response. Saving full text."
            )

        # Check for blocked prompt
        if (
            not summary_text
            and hasattr(response, "prompt_feedback")
            and response.prompt_feedback.block_reason
        ):
            print(
                f"❌ LLM blocked prompt during summary: {response.prompt_feedback.block_reason}",
                file=sys.stderr,
            )
            if hasattr(response.prompt_feedback, "block_reason_message"):
                print(
                    f"   Reason: {response.prompt_feedback.block_reason_message}",
                    file=sys.stderr,
                )
            return False

    except AttributeError:
        print(
            f"❌ LLM response object structure unexpected during summary. Response: {response}",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(f"❌ LLM API call failed during summary generation: {e}", file=sys.stderr)
        return False

    print(f"💾 Saving summary to ''{summary_output_path}''...")
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(summary_output_path), exist_ok=True)
        # Write the generated summary to its final destination
        with open(summary_output_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
    except Exception as e:
        print(
            f"❌ Error writing summary output to ''{summary_output_path}'´: {e}",
            file=sys.stderr,
        )
        return False

    print(f"✅ Summary saved successfully.")
    # No sleep needed after the final step in this session's flow
    return True  # Indicate success
