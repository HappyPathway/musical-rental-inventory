#!/usr/bin/env python
"""
Run mobile-specific Selenium tests for inventory management

Usage:
    source venv/bin/activate
    python run_mobile_inventory_tests.py

This script specifically targets mobile inventory management tests that validate
our mobile-optimized features for equipment management.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'music_rental.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, failfast=False)
    
    # Only run mobile inventory tests
    test_suite = [
        'tests.functional.test_inventory.MobileInventoryTestCase'
    ]
    
    failures = test_runner.run_tests(test_suite)
    sys.exit(bool(failures))