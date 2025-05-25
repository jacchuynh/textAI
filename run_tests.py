#!/usr/bin/env python3
"""
Test Runner Script

This script provides a convenient way to run the integration tests
for the Magic Realms project.
"""

import os
import sys
import subprocess
import argparse

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description='Run integration tests for Magic Realms')
    parser.add_argument('--module', '-m', help='Specific test module to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Set the path to the integration tests
    test_path = os.path.join('backend', 'tests', 'integration')
    
    # Ensure the test directory exists
    if not os.path.exists(test_path):
        print(f"Error: Test directory '{test_path}' does not exist.")
        return 1
    
    # Build the pytest command
    command = ['python', '-m', 'pytest']
    
    # Add verbose flag if specified
    if args.verbose:
        command.append('-v')
    
    # Add the specific module if specified
    if args.module:
        module_path = os.path.join(test_path, f'test_{args.module}.py')
        if not os.path.exists(module_path):
            print(f"Error: Test module '{module_path}' does not exist.")
            return 1
        command.append(module_path)
    else:
        # Otherwise, run all integration tests
        command.append(test_path)
    
    # Add coverage reporting
    command.extend(['--cov=backend', '--cov-report=term'])
    
    print(f"Running command: {' '.join(command)}")
    
    # Run the tests
    result = subprocess.run(command)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())