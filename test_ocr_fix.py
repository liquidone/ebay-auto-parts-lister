#!/usr/bin/env python3
"""
Test script to verify OCR is working with the Vision API credentials fix
"""
import os
import sys

# Add the project directory to path
sys.path.insert(0, '/opt/ebay-auto-parts-lister')

print("=" * 60)
print("Testing OCR Fix")
print("=" * 60)

# Import the part identifier module
from modules.part_identifier import PartIdentifier

# Create an instance
print("\n1. Creating PartIdentifier instance...")
identifier = PartIdentifier()

# Check if vision client is initialized
print(f"\n2. Vision client initialized: {identifier.vision_client is not None}")

if identifier.vision_client:
    print("   ✓ Vision API client is active!")
    
    # Test with a sample image if one exists
    import glob
    test_images = glob.glob('/opt/ebay-auto-parts-lister/uploads/*.jpg')[:1]
    
    if test_images:
        print(f"\n3. Testing OCR on image: {test_images[0]}")
        try:
            ocr_text, vin = identifier._perform_ocr_on_images(test_images)
            if ocr_text:
                print(f"   ✓ OCR extracted text (first 200 chars):\n   {ocr_text[:200]}")
            else:
                print("   ⚠ No text extracted from image")
        except Exception as e:
            print(f"   ✗ Error during OCR: {e}")
    else:
        print("\n3. No test images found in uploads folder")
else:
    print("   ✗ Vision API client NOT initialized")
    print("   Check if GOOGLE_APPLICATION_CREDENTIALS is set correctly")
    print(f"   Current value: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NOT SET')}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
