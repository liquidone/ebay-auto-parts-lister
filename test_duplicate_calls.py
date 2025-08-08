#!/usr/bin/env python3
"""
Test script to investigate duplicate Gemini API calls
This will upload test images and monitor the debug output
"""

import requests
import os
import time
from pathlib import Path

# Production server URL
API_URL = "http://143.198.55.193/process-images"

def test_duplicate_calls():
    """Upload test images to check for duplicate Gemini API calls"""
    
    print("=" * 60)
    print("TESTING FOR DUPLICATE GEMINI API CALLS")
    print("=" * 60)
    
    # Find test images in uploads folder
    uploads_dir = Path("uploads")
    test_images = []
    
    # Get first 3 image files from uploads folder
    for file in uploads_dir.glob("*.jpg"):
        test_images.append(file)
        if len(test_images) >= 3:
            break
    
    for file in uploads_dir.glob("*.png"):
        if len(test_images) >= 3:
            break
        test_images.append(file)
    
    if not test_images:
        print("ERROR: No test images found in uploads folder")
        return
    
    print(f"\nFound {len(test_images)} test images:")
    for img in test_images:
        print(f"  - {img.name}")
    
    # Prepare files for upload
    files = []
    for img_path in test_images:
        files.append(('files', (img_path.name, open(img_path, 'rb'), 'image/jpeg')))
    
    print(f"\nSending {len(test_images)} images to API...")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    try:
        # Send request
        response = requests.post(API_URL, files=files)
        
        # Close file handles
        for _, (_, file_handle, _) in files:
            file_handle.close()
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check debug output for multiple Gemini calls
            if 'debug_output' in result:
                debug = result['debug_output']
                
                # Check raw_gemini_responses for multiple calls
                if 'raw_gemini_responses' in debug:
                    gemini_calls = debug['raw_gemini_responses']
                    print(f"\n[!] GEMINI API CALLS DETECTED: {len(gemini_calls)}")
                    
                    if len(gemini_calls) > 1:
                        print("WARNING: MULTIPLE GEMINI API CALLS FOUND!")
                        for i, call in enumerate(gemini_calls, 1):
                            print(f"\n  Call #{i}:")
                            print(f"    - Images: {call.get('images_count', 'unknown')}")
                            print(f"    - Timestamp: {call.get('timestamp', 'unknown')}")
                            print(f"    - Model: {call.get('model', 'unknown')}")
                    else:
                        print("[OK] Only 1 Gemini API call made (expected behavior)")
                
                # Also check step3_gemini_analysis
                if 'step3_gemini_analysis' in debug:
                    analysis = debug['step3_gemini_analysis']
                    print(f"\nGemini Analysis Results:")
                    print(f"  - Part Name: {analysis.get('part_name', 'N/A')}")
                    print(f"  - SEO Title: {analysis.get('seo_title', 'N/A')}")
            
            print("\n" + "=" * 60)
            print("TEST COMPLETE")
            print("=" * 60)
            
            # Save full response for analysis
            with open("test_duplicate_response.json", "w") as f:
                import json
                json.dump(result, f, indent=2)
                print(f"\nFull response saved to: test_duplicate_response.json")
            
        else:
            print(f"ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_duplicate_calls()
