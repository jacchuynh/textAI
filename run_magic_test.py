"""
Runner script for the magic integration test.

This script adds the necessary path to import our modules.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.abspath('.'))

# Now import and run the test
from test_magic_integration import test_full_integration

if __name__ == "__main__":
    # Run the full integration test
    test_full_integration()