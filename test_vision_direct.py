#!/usr/bin/env python3
"""Direct test of Google Vision API on the server"""

import os
import sys

# Check if credentials are set
creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
print(f"GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")

if creds_path:
    print(f"Credentials file exists: {os.path.exists(creds_path)}")
else:
    print("ERROR: GOOGLE_APPLICATION_CREDENTIALS not set!")
    sys.exit(1)

try:
    from google.cloud import vision
    print("✓ google-cloud-vision package imported successfully")
except ImportError as e:
    print(f"✗ Failed to import google-cloud-vision: {e}")
    sys.exit(1)

# Initialize the Vision client
try:
    client = vision.ImageAnnotatorClient()
    print("✓ Vision client initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize Vision client: {e}")
    sys.exit(1)

# Test with a public image URL (Google's sample)
print("Testing with Google's sample image from URL...")

# Use a public image URL for testing
image = vision.Image()
image.source.image_uri = "https://cloud.google.com/vision/docs/images/sign_text.png"

print("Image URL: https://cloud.google.com/vision/docs/images/sign_text.png")

# Perform text detection
try:
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if texts:
        print("\n✓ Vision API OCR successful!")
        print(f"Found {len(texts)} text annotations")
        print("\nFull extracted text:")
        print("-" * 40)
        if texts:
            print(texts[0].description)  # First annotation contains all text
        print("-" * 40)
        
        # Show individual text blocks
        if len(texts) > 1:
            print("\nIndividual text blocks found:")
            for i, text in enumerate(texts[1:6], 1):  # Show first 5 blocks
                print(f"  {i}. '{text.description}'")
            if len(texts) > 6:
                print(f"  ... and {len(texts) - 6} more text blocks")
    else:
        print("✗ No text found in the image")
    
    # Check for errors
    if response.error.message:
        print(f"\n✗ API Error: {response.error.message}")
        
except Exception as e:
    print(f"\n✗ Failed to perform OCR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n✓ Test completed!")
