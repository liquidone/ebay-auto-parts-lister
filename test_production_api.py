#!/usr/bin/env python3
"""
Test the production API to verify Gemini data is being returned properly
"""
import requests
import json
from pathlib import Path

# Production server URL
API_URL = "http://143.198.55.193/process-images"

def test_with_sample_image():
    """Test with a sample image from the web"""
    
    # Download a sample auto part image
    image_url = "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=800"
    response = requests.get(image_url)
    
    # Save temporarily
    temp_file = Path("temp_test_image.jpg")
    temp_file.write_bytes(response.content)
    
    try:
        # Send to production API
        print("Sending image to production server...")
        with open(temp_file, 'rb') as f:
            files = {'files': ('test_part.jpg', f, 'image/jpeg')}
            response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n=== API RESPONSE STRUCTURE ===")
            print(f"Status Code: {response.status_code}")
            
            # Check main fields
            print("\n=== MAIN RESULT FIELDS ===")
            fields_to_check = [
                'part_name', 'seo_title', 'description', 
                'make', 'model', 'year_range', 'condition',
                'estimated_price', 'weight_lbs', 'dimensions_inches'
            ]
            
            for field in fields_to_check:
                value = result.get(field, 'MISSING')
                if value and value != 'MISSING':
                    print(f"[OK] {field}: {value[:100] if isinstance(value, str) else value}")
                else:
                    print(f"[MISSING] {field}: MISSING or EMPTY")
            
            # Check debug output
            if 'debug_output' in result:
                debug = result['debug_output']
                
                if 'step3_gemini_analysis' in debug:
                    print("\n=== GEMINI ANALYSIS IN DEBUG ===")
                    gemini_data = debug['step3_gemini_analysis']
                    
                    for field in ['part_name', 'seo_title', 'description']:
                        value = gemini_data.get(field, 'MISSING')
                        if value and value != 'MISSING':
                            print(f"[OK] {field}: {value[:100] if isinstance(value, str) else value}")
                        else:
                            print(f"[MISSING] {field}: MISSING or EMPTY")
                else:
                    print("\n[ERROR] No step3_gemini_analysis in debug output")
            else:
                print("\n[ERROR] No debug_output in response")
                
            # Save full response for inspection
            with open('test_response.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\n[SAVED] Full response saved to test_response.json")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()

if __name__ == "__main__":
    print("Testing Production API at http://143.198.55.193")
    print("=" * 50)
    test_with_sample_image()
