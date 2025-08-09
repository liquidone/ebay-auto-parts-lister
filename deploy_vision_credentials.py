#!/usr/bin/env python3
"""
Check and validate Google Vision API credentials on production server
This script checks if the credentials file exists and is valid JSON
"""

import json
import os
import sys

CREDS_PATH = '/opt/ebay-auto-parts-lister/vision-credentials.json'

def check_credentials():
    """Check if Vision API credentials exist and are valid"""
    
    # Check if file exists
    if not os.path.exists(CREDS_PATH):
        print(f"❌ Credentials file not found at {CREDS_PATH}")
        print("\nTo fix this, create the file with your Google Cloud service account JSON")
        return False
    
    # Check if it's valid JSON
    try:
        with open(CREDS_PATH, 'r') as f:
            creds = json.load(f)
        print(f"✅ Credentials file exists and is valid JSON")
        
        # Check required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing = [field for field in required_fields if field not in creds]
        
        if missing:
            print(f"❌ Missing required fields: {', '.join(missing)}")
            return False
            
        print(f"✅ All required fields present")
        print(f"   Project ID: {creds.get('project_id')}")
        print(f"   Client Email: {creds.get('client_email')}")
        
        # Check private key format
        private_key = creds.get('private_key', '')
        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            print("❌ Private key format invalid")
            return False
            
        print("✅ Private key format looks correct")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
        print("\nThe file exists but contains invalid JSON. Please recreate it.")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

if __name__ == "__main__":
    if check_credentials():
        print("\n✅ Vision API credentials are properly configured!")
        sys.exit(0)
    else:
        print("\n❌ Vision API credentials need to be fixed")
        print("\nInstructions:")
        print("1. Download your service account JSON from Google Cloud Console")
        print("2. Upload it to /opt/ebay-auto-parts-lister/vision-credentials.json")
        print("3. Restart the service: systemctl restart ebay-auto-parts-lister")
        sys.exit(1)
