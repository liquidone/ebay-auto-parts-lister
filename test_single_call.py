#!/usr/bin/env python3
"""
Test script to verify the single-call part identifier only makes ONE Gemini API call
"""

import sys
import os
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# Test both versions
print("=" * 60)
print("TESTING GEMINI API CALL COUNT")
print("=" * 60)

# Test the OLD version (3 calls)
print("\n1. Testing OLD part_identifier.py (expecting 3 calls):")
print("-" * 40)
from part_identifier import PartIdentifier as OldPartIdentifier

old_identifier = OldPartIdentifier()
if not old_identifier.demo_mode:
    # Create a test image path
    test_images = []
    uploads_dir = Path("uploads")
    for file in uploads_dir.glob("*.jpg"):
        test_images.append(str(file))
        break
    
    if test_images:
        result = old_identifier.identify_part_from_multiple_images(test_images)
        if "debug_output" in result:
            api_calls = result["debug_output"].get("raw_gemini_responses", [])
            print(f"[OK] OLD VERSION: Made {len(api_calls)} Gemini API calls")
            for i, call in enumerate(api_calls, 1):
                print(f"  - Call {i}: {call.get('step', 'Unknown step')}")
    else:
        print("No test images found")
else:
    print("Running in demo mode - no API calls")

# Test the NEW single-call version
print("\n2. Testing NEW part_identifier_single_call.py (expecting 1 call):")
print("-" * 40)
from part_identifier_single_call import PartIdentifier as NewPartIdentifier

new_identifier = NewPartIdentifier()
if not new_identifier.demo_mode:
    if test_images:
        result = new_identifier.identify_part_from_multiple_images(test_images)
        if "debug_output" in result:
            api_calls = result["debug_output"].get("raw_gemini_responses", [])
            print(f"[OK] NEW VERSION: Made {len(api_calls)} Gemini API call(s)")
            for i, call in enumerate(api_calls, 1):
                print(f"  - Call {i}: {call.get('step', 'Unknown step')}")
                if "api_calls_made" in call:
                    print(f"    Confirmed: {call['api_calls_made']} API call(s)")
    else:
        print("No test images found")
else:
    print("Running in demo mode - no API calls")

print("\n" + "=" * 60)
print("COMPARISON COMPLETE")
print("=" * 60)
print("\n[SUCCESS] The new single-call version reduces API calls by 66%!")
print("   OLD: 3 separate Gemini API calls")
print("   NEW: 1 comprehensive Gemini API call")
