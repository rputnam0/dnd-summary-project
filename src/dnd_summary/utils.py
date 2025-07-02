"""
Utility functions for the D&D session summary generator.
"""

import re
import sys

def get_session_number(session_identifier):
    """Extracts the session number from the session identifier."""
    try:
        # Extract the first sequence of digits found in the identifier.
        match = re.search(r"\d+", session_identifier)
        if match:
            session_number_str = match.group(0)
            session_number = int(session_number_str)
            # Ensure the session number is positive.
            if session_number <= 0:
                print("❗️ Session number must be positive.", file=sys.stderr)
                sys.exit(1)
            return session_number
        else:
            # Exit if no digits could be found.
            print(
                f"❗️ Invalid input: Could not find a number in ''{session_identifier}'´.",
                file=sys.stderr,
            )
            sys.exit(1)
    except ValueError:
        # This case should be rare due to re.search but handles potential conversion errors.
        print(
            f"❗️ Invalid input: ''{session_identifier}'´ does not contain a valid number.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors during processing.
        print(
            f"❗️ An unexpected error occurred during input processing: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
