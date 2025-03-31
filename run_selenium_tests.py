#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add the project to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

def setup_environment():
    """Set up the test environment variables"""
    # Make sure we're using the test database
    os.environ['DJANGO_SETTINGS_MODULE'] = 'music_rental.settings'
    os.environ.setdefault('PYTHONUNBUFFERED', '1')

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run ROKNSOUND Selenium tests')
    
    parser.add_argument(
        '--browser', 
        choices=['chrome', 'firefox'], 
        default='chrome',
        help='Browser to use for Selenium tests (default: chrome)'
    )
    
    parser.add_argument(
        '--headless', 
        action='store_true',
        help='Run tests in headless mode'
    )
    
    parser.add_argument(
        'test_path', 
        nargs='?',
        default='tests/functional',
        help='Path to tests to run (default: tests/functional)'
    )
    
    return parser.parse_args()

def run_tests(args):
    """Run the tests using Django's test runner"""
    # Set environment variables based on arguments
    os.environ['BROWSER'] = args.browser
    os.environ['HEADLESS'] = 'true' if args.headless else 'false'
    
    # Display test configuration
    print(f"\n=== Running ROKNSOUND Selenium Tests ===")
    print(f"Browser: {args.browser}")
    print(f"Headless Mode: {args.headless}")
    print(f"Test Path: {args.test_path}")
    print("="*40 + "\n")
    
    # Build the Django test command
    test_command = [
        'python', 'manage.py', 'test', 
        args.test_path,
        '--keepdb',  # Keep the test database between runs for speed
    ]
    
    # Run the tests
    return subprocess.call(test_command)

if __name__ == "__main__":
    args = parse_args()
    setup_environment()
    sys.exit(run_tests(args))