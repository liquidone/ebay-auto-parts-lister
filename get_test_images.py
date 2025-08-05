#!/usr/bin/env python3
"""
Test Image Helper for eBay Auto Parts Lister
Helps you find and organize test images for the recognition system
"""

import os
import requests
from pathlib import Path

def create_test_image_urls():
    """
    Sample URLs for auto part images that would be good for testing
    These are examples - you'll need to find actual images to download
    """
    
    test_cases = {
        "headlight_assembly": {
            "description": "Headlight assembly with visible part number",
            "expected_results": {
                "part_type": "Headlight Assembly",
                "side": "Left/Right",
                "part_number": "Should be visible on housing"
            }
        },
        "tail_light": {
            "description": "Tail light with OEM part number",
            "expected_results": {
                "part_type": "Tail Light",
                "side": "Left/Right", 
                "part_number": "Should be molded or stamped"
            }
        },
        "alternator": {
            "description": "Alternator with manufacturer label",
            "expected_results": {
                "part_type": "Alternator",
                "part_number": "Usually on metal tag",
                "amperage": "Should be identified"
            }
        },
        "starter": {
            "description": "Starter motor with part number",
            "expected_results": {
                "part_type": "Starter Motor",
                "part_number": "Usually stamped on housing",
                "vehicle_compatibility": "Should be determined"
            }
        }
    }
    
    return test_cases

def suggest_image_sources():
    """Print suggestions for finding good test images"""
    
    print("BEST SOURCES FOR AUTO PART TEST IMAGES:")
    print("\n1. eBay Listings:")
    print("   - Search: 'used headlight assembly'")
    print("   - Look for: Clear part numbers in photos")
    print("   - Save: Right-click images and save")
    
    print("\n2. Auto Parts Store Websites:")
    print("   - AutoZone, O'Reilly, Advance Auto Parts")
    print("   - Search specific part numbers")
    print("   - Good quality product photos")
    
    print("\n3. Automotive Forums:")
    print("   - Reddit r/MechanicAdvice")
    print("   - Car-specific forums")
    print("   - Users often post clear part photos")
    
    print("\n4. Manufacturer Websites:")
    print("   - OEM part catalogs")
    print("   - Aftermarket suppliers (TYC, Depo, etc.)")
    print("   - Technical documentation photos")
    
    print("\nWHAT TO LOOK FOR IN TEST IMAGES:")
    print("   - Visible part numbers/labels")
    print("   - Clear, well-lit photos")
    print("   - Multiple angles of same part")
    print("   - OEM vs aftermarket examples")
    print("   - Different vehicle makes/models")

def create_test_structure():
    """Create organized test directory structure"""
    
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    categories = [
        "headlights",
        "tail_lights", 
        "alternators",
        "starters",
        "brake_parts",
        "suspension",
        "body_parts"
    ]
    
    for category in categories:
        category_dir = test_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Create a README for each category
        readme_path = category_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(f"# {category.replace('_', ' ').title()} Test Images\n\n")
            f.write("## Instructions:\n")
            f.write("1. Add test images to this folder\n")
            f.write("2. Name files descriptively (e.g., 'ford_f150_headlight_left_oem.jpg')\n")
            f.write("3. Include part numbers in filename if visible\n")
            f.write("4. Test with multiple angles of same part\n\n")
            f.write("## Expected Results:\n")
            f.write("- Part identification accuracy\n")
            f.write("- Vehicle compatibility detection\n")
            f.write("- Part number recognition\n")
            f.write("- Side determination (L/R)\n")
    
    print(f"Created test directory structure in: {test_dir.absolute()}")
    print("\nTest Categories Created:")
    for category in categories:
        print(f"   - {category}")

if __name__ == "__main__":
    print("eBay Auto Parts Lister - Test Image Helper\n")
    
    # Create test directory structure
    create_test_structure()
    
    print("\n" + "="*60)
    
    # Show test cases
    test_cases = create_test_image_urls()
    print("\nRECOMMENDED TEST CASES:")
    for name, info in test_cases.items():
        print(f"\n{name.replace('_', ' ').title()}:")
        print(f"   Description: {info['description']}")
        print("   Expected Results:")
        for key, value in info['expected_results'].items():
            print(f"     - {key}: {value}")
    
    print("\n" + "="*60)
    
    # Show image source suggestions
    suggest_image_sources()
    
    print("\nNEXT STEPS:")
    print("1. Find and download 2-3 images for each category")
    print("2. Place them in the appropriate test_images/ subdirectories")
    print("3. Run your eBay Auto Parts Lister application")
    print("4. Upload and test the recognition accuracy")
    print("5. Compare results with expected outcomes")
