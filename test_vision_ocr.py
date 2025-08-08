"""
Test script for Google Vision OCR integration
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.part_identifier_v2 import PartIdentifier
import json

def test_vision_ocr():
    """Test the new Vision OCR pipeline"""
    
    print("=" * 60)
    print("Testing Google Vision OCR Integration")
    print("=" * 60)
    
    # Initialize the part identifier
    identifier = PartIdentifier()
    
    # Check for test images
    test_images_dir = Path("test_images")
    if not test_images_dir.exists():
        print("\nNo test_images directory found. Creating demo test...")
        # Use demo mode
        result = identifier.identify_part_from_multiple_images([])
        print("\nDemo Mode Result:")
        print(json.dumps(result, indent=2))
        
        if 'debug_output' in result:
            debug = result['debug_output']
            print("\n" + "=" * 60)
            print("DEBUG OUTPUT STRUCTURE:")
            print("=" * 60)
            
            # Check API status
            if 'api_status' in debug:
                print("\nAPI Status:")
                print(f"  - Demo Mode: {debug['api_status'].get('demo_mode', False)}")
                print(f"  - Vision API: {debug['api_status'].get('vision_api_configured', False)}")
                print(f"  - Gemini API: {debug['api_status'].get('gemini_api_configured', False)}")
            
            # Check Vision OCR step
            if 'step1_vision_ocr' in debug:
                print("\nStep 1 - Vision OCR:")
                ocr = debug['step1_vision_ocr']
                print(f"  - Images Processed: {ocr.get('images_processed', 0)}")
                print(f"  - OCR Success Count: {ocr.get('ocr_success_count', 0)}")
                print(f"  - Combined Text Length: {len(ocr.get('combined_text', ''))}")
            
            # Check Dynamic Prompt step
            if 'step2_dynamic_prompt' in debug:
                print("\nStep 2 - Dynamic Prompt:")
                prompt = debug['step2_dynamic_prompt']
                print(f"  - Scenario: {prompt.get('scenario', 'N/A')}")
                print(f"  - Part Numbers Found: {prompt.get('part_numbers_found', 0)}")
                print(f"  - Prompt Length: {prompt.get('full_prompt_length', 0)}")
            
            # Check Gemini Analysis step
            if 'step3_gemini_analysis' in debug:
                print("\nStep 3 - Gemini Analysis:")
                analysis = debug['step3_gemini_analysis']
                print(f"  - Part Name: {analysis.get('part_name', 'N/A')}")
                print(f"  - Part Numbers: {analysis.get('part_numbers', [])}")
                print(f"  - Make/Model: {analysis.get('make', 'N/A')} {analysis.get('model', 'N/A')}")
                print(f"  - Price Range: {analysis.get('price_range', 'N/A')}")
            
            # Check extracted part numbers
            if 'extracted_part_numbers' in debug:
                print(f"\nExtracted Part Numbers: {debug['extracted_part_numbers']}")
    else:
        # Use real test images
        test_images = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
        if test_images:
            print(f"\nFound {len(test_images)} test images")
            print("Processing with Vision OCR pipeline...")
            
            # Read image data
            image_data = []
            for img_path in test_images[:3]:  # Limit to 3 images for testing
                with open(img_path, 'rb') as f:
                    image_data.append(f.read())
            
            # Pass image paths, not raw data
            image_path_strings = [str(img_path) for img_path in test_images[:3]]
            result = identifier.identify_part_from_multiple_images(image_path_strings)
            print("\nResult with Real Images:")
            print(json.dumps(result, indent=2))
        else:
            print("\nNo images found in test_images directory")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_vision_ocr()
