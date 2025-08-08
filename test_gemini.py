#!/usr/bin/env python3
"""
Direct test of Gemini API to see what's actually happening on production server
"""

import os
import sys

print("=" * 60)
print("GEMINI API DIRECT TEST")
print("=" * 60)

# First, try without dotenv
print("\n1. Testing WITHOUT dotenv:")
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"   Found in system env: {api_key[:10]}...")
else:
    print("   Not in system environment")

# Now try with dotenv
print("\n2. Testing WITH dotenv:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   dotenv loaded successfully")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"   Found after dotenv: {api_key[:10]}...")
            # Check for premium models (indicates paid account)
            premium_indicators = ['gemini-1.5-pro', 'gemini-pro-vision', 'gemini-ultra']
            has_premium = any(premium in str(available_models) for premium in premium_indicators)
            
            if has_premium:
                print("[PREMIUM] PAID ACCOUNT DETECTED - Premium models available!")
            else:
                print("[FREE] Free tier account - Basic models available")
                
        except Exception as e:
            print(f"[WARNING] Could not check models: {e}")
        
        print("\n[RESULTS] Gemini API Test Results:")
        print("[OK] API Key: Valid and working")
        print("[OK] Connection: Successful") 
        print("[OK] Text Generation: Working")
        print("[OK] Ready for auto parts identification!")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini API Test Failed: {e}")
        
        # Check for specific error types
        if "quota" in str(e).lower():
            print("💳 This appears to be a quota/billing issue")
        elif "invalid" in str(e).lower():
            print("🔑 This appears to be an invalid API key")
        elif "permission" in str(e).lower():
            print("🚫 This appears to be a permissions issue")
        
        return False

if __name__ == "__main__":
    print("🚀 Testing Gemini API Key...")
    print("=" * 50)
    
    success = test_gemini_api()
    
    print("=" * 50)
    if success:
        print("🎉 Gemini API is ready for auto parts identification!")
    else:
        print("❌ Gemini API test failed - check your API key")
