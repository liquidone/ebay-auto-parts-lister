"""
Simple Browser-Only Test Script
This creates a minimal test endpoint that forces browser fallback
"""

import asyncio
import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

async def test_browser_fallback():
    """Test browser fallback directly"""
    
    print("Testing browser fallback directly...")
    
    try:
        from modules.gemini_browser_fallback import GeminiBrowserFallback
        
        # Initialize browser fallback
        browser = GeminiBrowserFallback()
        
        # Test with a sample image (use one of your test images)
        test_image = "test_images/challenging_brake_rotor.jpg"
        
        if not os.path.exists(test_image):
            print(f"Test image not found: {test_image}")
            print("Please ensure test images exist or update the path")
            return
        
        print(f"Testing browser fallback with: {test_image}")
        
        # Run browser identification
        result = await browser.identify_part(test_image)
        
        print("=== BROWSER FALLBACK RESULT ===")
        print(f"Part Name: {result.get('part_name', 'Unknown')}")
        print(f"Part Number: {result.get('part_number', 'None')}")
        print(f"Description: {result.get('description', 'No description')}")
        print(f"Method Used: Browser Gemini")
        print("=== END RESULT ===")
        
        return result
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Browser fallback module not available")
    except Exception as e:
        print(f"Browser test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Direct Browser Fallback Test")
    print("=" * 40)
    
    # Run the test
    result = asyncio.run(test_browser_fallback())
    
    if result:
        print("\nBrowser fallback test completed successfully!")
    else:
        print("\nBrowser fallback test failed!")
