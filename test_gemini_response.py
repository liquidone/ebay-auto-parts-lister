#!/usr/bin/env python3
"""Test script to see raw Gemini response from production API"""

import requests
import json
import base64

# Production server URL
API_URL = "http://143.198.55.193/process-images"

# Read the test image
import os
# Try to use a real auto part image from uploads
test_images = [
    "uploads/IMG_20250803_114946.jpg",  # Real auto part image
    "uploads/IMG_20250803_115010.jpg",
    "test_images/challenging_brake_rotor.jpg",
    "test_images/worn_engine_part.jpg",
    "test_images/multiple_auto_parts.jpg"
]

image_path = None
for path in test_images:
    if os.path.exists(path):
        image_path = path
        print(f"Using test image: {path}")
        break

if not image_path:
    print("No test image found. Creating a simple test image...")
    # Create a simple test image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    image_path = "test_image.jpg"
    img.save(image_path)

with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Prepare the request as multipart form data
files = [
    ('files', ('test_image.jpg', open(image_path, 'rb'), 'image/jpeg'))
]

print("Sending request to production API...")
print("-" * 50)

try:
    response = requests.post(API_URL, files=files, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        
        # Check if there's debug output with the raw Gemini response
        if 'debug_output' in result:
            debug = result['debug_output']
            
            # Look for the Gemini response in step3
            if 'step3_gemini_analysis' in debug:
                gemini_data = debug['step3_gemini_analysis']
                
                # Print the raw response
                if 'response_preview' in gemini_data:
                    print("Raw Gemini Response:")
                    print("=" * 50)
                    print(gemini_data['response_preview'])
                    print("=" * 50)
                    
                    # Check for Optimized Title in the response
                    import re
                    response_text = gemini_data['response_preview']
                    
                    # Look for Optimized Title
                    patterns = [
                        r'\*?\*?Optimized Title:\*?\*?\s*([^\n]+)',
                        r'Optimized Title:\s*"([^"]+)"',
                        r'Optimized Title:\s*([^\n]+)',
                        r'\*\*Optimized Title:\*\*\s*"([^"]+)"',
                        r'\*\*Optimized Title:\*\*\s*([^\n]+)',
                    ]
                    
                    found = False
                    for pattern in patterns:
                        match = re.search(pattern, response_text, re.IGNORECASE)
                        if match:
                            print(f"\n[FOUND] Optimized Title with pattern: {pattern}")
                            print(f"Extracted: {match.group(1).strip()}")
                            found = True
                            break
                    
                    if not found:
                        print("\n[NOT FOUND] No 'Optimized Title' found in response")
                        print("\nSearching for any title-like patterns...")
                        
                        # Look for any title mentions
                        if "title" in response_text.lower():
                            lines = response_text.split('\n')
                            for line in lines:
                                if "title" in line.lower():
                                    print(f"  Found line with 'title': {line.strip()}")
                
                # Also check what's being set as seo_title
                if 'seo_title' in gemini_data:
                    print(f"\nCurrent seo_title in debug: {gemini_data['seo_title']}")
                if 'ebay_title' in gemini_data:
                    print(f"Current ebay_title in debug: {gemini_data['ebay_title']}")
        
        # Check the main result
        print("\n" + "=" * 50)
        print("Main API Result:")
        print(f"SEO Title: {result.get('seo_title', 'NOT SET')}")
        print(f"Part Name: {result.get('part_name', 'NOT SET')}")
        
    else:
        print(f"Error: Status code {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
