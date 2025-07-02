"""
Unit tests for the file_handler module.
"""

import os
import unittest
from unittest.mock import patch

from src.dnd_summary.file_handler import find_transcript_file
from src.dnd_summary.config import TRANSCRIPTS_DIR

class TestFileHandler(unittest.TestCase):
    """Test suite for the file_handler module."""

    @patch("os.path.exists")
    def test_find_transcript_file_found(self, mock_exists):
        """Test that the transcript file is found when it exists."""
        mock_exists.return_value = True
        session_number = 1
        expected_path = os.path.join(TRANSCRIPTS_DIR, f"session_{session_number}.txt")
        self.assertEqual(find_transcript_file(session_number), expected_path)

    @patch("os.path.exists")
    def test_find_transcript_file_not_found(self, mock_exists):
        """Test that None is returned when the transcript file does not exist."""
        mock_exists.return_value = False
        self.assertIsNone(find_transcript_file(99))

if __name__ == "__main__":
    unittest.main()
