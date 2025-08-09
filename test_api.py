#!/usr/bin/env python3
"""Test script to verify Gemini API is working"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 50)
print("GEMINI API TEST SCRIPT")
print("=" * 50)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"\n1. API Key exists: {bool(api_key)}")
if api_key:
    print(f"   Key starts with: {api_key[:15]}...")
else:
    print("   ERROR: No API key found in environment!")
    print("   Check your .env file")
    sys.exit(1)

# Test Gemini API
print("\n2. Testing Gemini API connection...")
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Simple test prompt
    response = model.generate_content("Say exactly: API_WORKING")
    print(f"   Response: {response.text.strip()}")
    
    if "API_WORKING" in response.text:
        print("   ✓ API is working correctly!")
    else:
        print(f"   WARNING: Unexpected response: {response.text}")
        
except Exception as e:
    print(f"   ERROR: {str(e)}")
    print(f"   Type: {type(e).__name__}")

# Test with image
print("\n3. Testing with image...")
try:
    from PIL import Image
    import io
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    # Convert to PIL Image for Gemini
    img_pil = Image.open(io.BytesIO(img_bytes))
    
    response = model.generate_content([
        "What color is this image? Reply with just the color name.",
        img_pil
    ])
    print(f"   Response: {response.text.strip()}")
    
    if "red" in response.text.lower():
        print("   ✓ Image processing works!")
    else:
        print(f"   WARNING: Expected 'red', got: {response.text}")
        
except Exception as e:
    print(f"   ERROR: {str(e)}")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
