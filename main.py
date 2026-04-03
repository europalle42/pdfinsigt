"""PDFIndsigt — PDF Metadata Analyse Tool.

Start-punkt for applikationen.
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import run

if __name__ == "__main__":
    run()
