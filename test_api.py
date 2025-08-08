#!/usr/bin/env python3
"""
Simple test to check what's really happening with Gemini API
"""

import os
import sys

print("=" * 60)
print("GEMINI API DIRECT TEST")
print("=" * 60)

# Check environment variable
print("\nChecking for API key...")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Trying to load from .env file...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print(f"✅ Found API key from .env: {api_key[:10]}...")
    except:
        pass

if not api_key:
    print("❌ NO API KEY FOUND")
    sys.exit(1)

print(f"✅ API key found: {api_key[:10]}...")
print(f"   Key length: {len(api_key)} chars")

# Test the actual API
print("\n" + "=" * 60)
print("TESTING ACTUAL API CALL")
print("=" * 60)

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    print("✅ Gemini client configured")
    
    # Try simple model
    print("\nTrying gemini-pro model...")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say TEST OK")
    print(f"✅ SUCCESS! Response: {response.text}")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    
    # Try different model
    try:
        print("\nTrying gemini-1.5-flash model...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say TEST OK")
        print(f"✅ SUCCESS with gemini-1.5-flash! Response: {response.text}")
    except Exception as e2:
        print(f"❌ ALSO FAILED: {e2}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
