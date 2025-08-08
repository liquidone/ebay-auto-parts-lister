#!/usr/bin/env python3
"""
Test script to verify debug output from part_identifier.py
"""

import json
import sys
import os
from pprint import pprint

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.part_identifier import PartIdentifier

def test_debug_output():
    """Test the debug output structure"""
    
    print("=" * 60)
    print("TESTING DEBUG OUTPUT STRUCTURE")
    print("=" * 60)
    
    # Initialize the part identifier
    identifier = PartIdentifier()
    
    # Check if we're in demo mode
    print(f"\nDemo Mode: {identifier.demo_mode}")
    print(f"API Key Configured: {identifier.debug_output['api_status']['api_key_configured']}")
    
    # Get a demo response to check structure
    if identifier.demo_mode:
        print("\nRunning in DEMO MODE - testing debug structure...")
        result = identifier._get_demo_response()
        
        print("\n" + "=" * 40)
        print("DEBUG OUTPUT STRUCTURE:")
        print("=" * 40)
        
        if 'debug_output' in result:
            debug = result['debug_output']
            
            # Check each expected field
            fields_to_check = [
                'step1_ocr_raw',
                'step2_fitment_raw', 
                'step3_pricing_raw',
                'workflow_steps',
                'processing_time'
            ]
            
            for field in fields_to_check:
                if field in debug:
                    print(f"✓ {field}: {type(debug[field]).__name__}")
                    if isinstance(debug[field], str):
                        print(f"  Content: {debug[field][:100]}...")
                    elif isinstance(debug[field], list):
                        print(f"  Items: {len(debug[field])}")
                else:
                    print(f"✗ {field}: MISSING")
            
            print("\n" + "=" * 40)
            print("FULL DEBUG OUTPUT:")
            print("=" * 40)
            print(json.dumps(debug, indent=2))
        else:
            print("ERROR: No debug_output field in result!")
            print("Result keys:", list(result.keys()))
    else:
        print("\nAPI Key is configured - would need test images to run full test")
        print("Debug output structure initialized:")
        pprint(identifier.debug_output)

if __name__ == "__main__":
    test_debug_output()
