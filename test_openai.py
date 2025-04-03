#!/usr/bin/env python
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_rental.settings')
django.setup()

from inventory.utils import fetch_manual_from_openai

def test_openai():
    """Test OpenAI integration by fetching a manual for a JBL speaker"""
    print("Testing OpenAI integration...")
    print(f"OpenAI API Key exists: {bool(settings.OPENAI_API_KEY)}")
    
    result = fetch_manual_from_openai("JBL", "SRX835P")
    print("\nOpenAI Response:")
    print(result)

if __name__ == '__main__':
    test_openai() 