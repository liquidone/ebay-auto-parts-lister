#!/usr/bin/env python3
"""Test script to check Optimized Title extraction from Gemini response"""

import re

# Sample Gemini response with Optimized Title
sample_response = """
This is a Left (Driver Side) outer tail light assembly, which mounts on the quarter panel of the vehicle.

**Part Type:** Tail Light Assembly
**Position:** Left (Driver Side)
**Mounting:** Quarter Panel Mounted
**OEM:** Yes

**Part Numbers:**
- 26555-ET00A
- 26555ET00A

**Vehicle Fitment:** 2007-2012 Nissan Sentra

**Condition:** Used - Good condition with minor wear

**Brand:** Nissan (OEM)

**Keywords:** Nissan Sentra tail light, driver side tail lamp, left rear light, quarter panel light, OEM 26555-ET00A

**Optimized Title:**
"OEM 2007-2012 Nissan Sentra Left Driver Side Outer Tail Light Lamp Assembly"

**Suggested Keywords:**
- Nissan Sentra
- Tail Light
- Left Driver Side
- Quarter Panel Mounted
- OEM
- 26555-ET00A
"""

def test_extraction():
    print("Testing Optimized Title extraction...")
    print("-" * 50)
    
    # Test the regex pattern we're using
    pattern = r'\*?\*?Optimized Title:\*?\*?\s*([^\n]+)'
    
    match = re.search(pattern, sample_response, re.IGNORECASE)
    
    if match:
        optimized_title = match.group(1).strip().replace('**', '').replace('*', '')
        # Remove quotes if present
        optimized_title = optimized_title.strip('"').strip("'")
        print(f"[SUCCESS] Found Optimized Title: {optimized_title}")
    else:
        print("[FAILED] No Optimized Title found with current pattern")
        
        # Try alternative patterns
        alt_patterns = [
            r'Optimized Title:\s*"([^"]+)"',
            r'Optimized Title:\s*([^\n]+)',
            r'\*\*Optimized Title:\*\*\s*"([^"]+)"',
            r'\*\*Optimized Title:\*\*\s*([^\n]+)',
        ]
        
        for i, alt_pattern in enumerate(alt_patterns, 1):
            alt_match = re.search(alt_pattern, sample_response, re.IGNORECASE)
            if alt_match:
                print(f"  Alternative pattern {i} works: {alt_match.group(1).strip()}")

if __name__ == "__main__":
    test_extraction()
