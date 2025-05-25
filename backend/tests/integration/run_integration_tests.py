#!/usr/bin/env python3
"""
Integration Test Runner

This script provides a convenient way to run all integration tests or
specific test modules. It handles import errors gracefully and provides
detailed reporting of test results.
"""

import unittest
import sys
import os
import argparse
import time
from typing import List, Optional

def discover_and_run_tests(test_modules: Optional[List[str]] = None, verbose: bool = False) -> unittest.TestResult:
    """
    Discover and run integration tests.
    
    Args:
        test_modules: Optional list of specific test modules to run
        verbose: Whether to print verbose output
    
    Returns:
        The test result object
    """
    # Set up test loader
    loader = unittest.TestLoader()
    
    # Determine the test directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create test suite
    suite = unittest.TestSuite()
    
    if test_modules:
        # Run specific test modules
        for module_name in test_modules:
            # Ensure .py extension is not included
            if module_name.endswith('.py'):
                module_name = module_name[:-3]
            
            try:
                # Try to import the module
                module = __import__(module_name)
                
                # Add tests from the module to the suite
                module_tests = loader.loadTestsFromName(module_name)
                suite.addTest(module_tests)
                
                print(f"Added tests from module: {module_name}")
            except ImportError as e:
                print(f"Error importing module {module_name}: {e}")
    else:
        # Discover all test modules in the integration directory
        pattern = "test_*.py"
        suite = loader.discover(current_dir, pattern=pattern)
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    
    # Run the tests
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Return result for further processing
    return result, end_time - start_time

def print_test_summary(result: unittest.TestResult, duration: float) -> None:
    """
    Print a summary of the test results.
    
    Args:
        result: The test result object
        duration: The duration of the test run in seconds
    """
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    # Print statistics
    print(f"Run duration: {duration:.2f} seconds")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Calculate success rate
    success_count = result.testsRun - len(result.errors) - len(result.failures)
    if result.testsRun > 0:
        success_rate = (success_count / result.testsRun) * 100
    else:
        success_rate = 0
    
    print(f"Success rate: {success_rate:.2f}%")
    
    # Print details of errors and failures if any
    if result.errors:
        print("\nERRORS:")
        for test, error in result.errors:
            print(f"\n{test}")
            print("-" * 70)
            print(error)
    
    if result.failures:
        print("\nFAILURES:")
        for test, failure in result.failures:
            print(f"\n{test}")
            print("-" * 70)
            print(failure)
    
    # Print overall result
    print("\n" + "=" * 70)
    if not result.errors and not result.failures:
        print("ALL TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED!")
    print("=" * 70)

def main():
    """Main function to parse arguments and run tests."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run integration tests for the Magic Realms system')
    parser.add_argument('--modules', nargs='+', help='Specific test modules to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Add the parent directory to sys.path to make the modules importable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, parent_dir)
    
    # Run tests
    print("Running integration tests...")
    if args.modules:
        print(f"Running specific modules: {', '.join(args.modules)}")
    else:
        print("Running all integration tests")
    
    result, duration = discover_and_run_tests(args.modules, args.verbose)
    
    # Print summary
    print_test_summary(result, duration)
    
    # Return appropriate exit code
    return 0 if not result.errors and not result.failures else 1

if __name__ == '__main__':
    sys.exit(main())