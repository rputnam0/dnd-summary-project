"""
This script is the main entry point for running the D&D session summary generator.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.dnd_summary.main import main

if __name__ == "__main__":
    main()
