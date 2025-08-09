#!/usr/bin/env python3
"""
Debug script to test Google Vision API initialization and functionality
"""
import os
import sys
import json
import traceback

# Set the credentials environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/ebay-auto-parts-lister/vision-credentials.json'

print("=" * 60)
print("Google Vision API Debug Script")
print("=" * 60)

# Check Python version
print(f"\n1. Python Version: {sys.version}")

# Check if credentials file exists
creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
print(f"\n2. Credentials Path: {creds_path}")
if os.path.exists(creds_path):
    print("   ✓ Credentials file exists")
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        print(f"   ✓ Valid JSON with project_id: {creds_data.get('project_id', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ✗ Error reading credentials: {e}")
else:
    print("   ✗ Credentials file NOT found")

# Try to import google-cloud-vision
print("\n3. Importing google-cloud-vision:")
try:
    from google.cloud import vision
    print("   ✓ google-cloud-vision imported successfully")
    print(f"   Version: {vision.__version__ if hasattr(vision, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"   ✗ Failed to import: {e}")
    print("   Try: pip install google-cloud-vision")
    sys.exit(1)

# Try to initialize the Vision client
print("\n4. Initializing Vision API Client:")
try:
    client = vision.ImageAnnotatorClient()
    print("   ✓ Vision API client initialized successfully!")
except Exception as e:
    print(f"   ✗ Failed to initialize client: {e}")
    print("\n   Full traceback:")
    traceback.print_exc()
    print("\n   Possible causes:")
    print("   - Invalid credentials format")
    print("   - Missing required Python packages")
    print("   - Network/firewall issues")
    print("   - Service account lacks necessary permissions")
    sys.exit(1)

# Test with a simple text detection
print("\n5. Testing OCR with sample text:")
try:
    # Create a simple test image with text (base64 encoded 1x1 white pixel as minimal test)
    import base64
    # This is a minimal PNG image
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    test_image = base64.b64decode(test_image_b64)
    
    image = vision.Image(content=test_image)
    response = client.text_detection(image=image)
    
    if response.error.message:
        print(f"   ✗ API Error: {response.error.message}")
    else:
        print("   ✓ Vision API call successful (no text found in test image, which is expected)")
        print("   ✓ API is working correctly!")
        
except Exception as e:
    print(f"   ✗ Test failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug complete!")
print("=" * 60)

# Additional diagnostics
print("\n6. Environment Variables:")
for key in ['GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_CLOUD_PROJECT', 'GCLOUD_PROJECT']:
    value = os.environ.get(key, 'NOT SET')
    if key == 'GOOGLE_APPLICATION_CREDENTIALS' and value != 'NOT SET':
        print(f"   {key}: {value}")
    else:
        print(f"   {key}: {value}")

print("\n7. Installed Packages:")
try:
    import pkg_resources
    relevant_packages = ['google-cloud-vision', 'google-auth', 'google-api-core', 'grpcio']
    for package in relevant_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"   ✓ {package}: {version}")
        except:
            print(f"   ✗ {package}: NOT INSTALLED")
except:
    print("   Could not check package versions")
