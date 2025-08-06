#!/usr/bin/env python3
"""
Direct Browser Fallback Test - No Flask Required
Simple script to test browser fallback directly
"""

import asyncio
import sys
import os
import tempfile
from pathlib import Path

# Add the project directory to Python path
sys.path.append('/opt/ebay-auto-parts-lister')

async def test_browser_fallback():
    """Test browser fallback directly"""
    print("🧪 Testing Browser Fallback Directly...")
    
    try:
        # Test 1: Import modules
        print("1. Testing module imports...")
        from modules.gemini_browser_fallback import GeminiBrowserFallback
        from modules.feature_flags import feature_flags
        print("   ✅ Modules imported successfully")
        
        # Test 2: Check feature flags
        print("2. Checking feature flags...")
        browser_enabled = feature_flags.is_enabled('enable_browser_fallback')
        print(f"   Browser fallback enabled: {browser_enabled}")
        
        # Test 3: Initialize browser fallback
        print("3. Initializing browser fallback...")
        browser = GeminiBrowserFallback()
        print("   ✅ Browser fallback initialized")
        
        # Test 4: Check Playwright availability
        print("4. Checking Playwright availability...")
        try:
            from playwright.async_api import async_playwright
            print("   ✅ Playwright is available")
        except ImportError as e:
            print(f"   ❌ Playwright not available: {e}")
            return
        
        # Test 5: Test with a sample image (if provided)
        test_image_path = "/opt/ebay-auto-parts-lister/test_image.jpg"
        if os.path.exists(test_image_path):
            print("5. Testing with sample image...")
            try:
                result = await browser.identify_part(test_image_path)
                print(f"   ✅ Browser identification successful!")
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   ❌ Browser identification failed: {e}")
        else:
            print("5. No test image found - skipping image test")
            print("   (Create /opt/ebay-auto-parts-lister/test_image.jpg to test with an image)")
        
        print("\n🎉 Browser fallback test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Run the async test
    asyncio.run(test_browser_fallback())
