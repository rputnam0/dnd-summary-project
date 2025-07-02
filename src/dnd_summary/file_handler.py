
"""
Handles file operations for the D&D session summary generator.
"""

import os
import sys

from .config import TRANSCRIPTS_DIR

def read_file(path):
    """Reads a file and returns its content, handling potential errors."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found -> {path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error reading file {path}: {e}", file=sys.stderr)
        return None

def find_transcript_file(session_number):
    """Finds the transcript file for a given session number."""
    session_number_str = str(session_number)
    potential_filenames_base = [
        f"session_{session_number_str}.txt",
        f"Session_{session_number_str}.txt",
        f"session {session_number_str}.txt",
        f"Session {session_number_str}.txt",
    ]
    potential_paths = [
        os.path.join(TRANSCRIPTS_DIR, fname) for fname in potential_filenames_base
    ]

    print(
        f"\n🔍 Searching for transcript file for session {session_number_str} in ''{TRANSCRIPTS_DIR}''..."
    )
    for potential_path in potential_paths:
        if os.path.exists(potential_path):
            print(f"   -> Found: ''{potential_path}''")
            return potential_path

    print(
        f"\n❌ Error: Transcript file for session {session_number_str} not found.",
        file=sys.stderr,
    )
    print(f"   Looked inside ''{TRANSCRIPTS_DIR}'' for names like:", file=sys.stderr)
    for name in potential_filenames_base:
        print(f"     - {name}", file=sys.stderr)
    return None

