#!/usr/bin/env python3
"""
Runner for Phase 5-7 tests with proper Python path setup.
"""
import sys
import os

# Add the backend/src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_src = os.path.join(current_dir, 'backend', 'src')
sys.path.insert(0, backend_src)

# Now run the test
if __name__ == "__main__":
    from test_phases_5_6_7 import main
    main()
