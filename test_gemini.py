#!/usr/bin/env python3
"""
Test script to verify Gemini API key and check account status
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API key and check account status"""
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ No GEMINI_API_KEY found in .env file")
        return False
    
    print(f"[KEY] Found Gemini API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple text generation
        print("[TEST] Testing Gemini API connection...")
        
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Simple test prompt
        test_prompt = "Hello! Please respond with 'Gemini API is working correctly' and tell me what model you are."
        
        response = model.generate_content(test_prompt)
        
        print("[SUCCESS] Gemini API Response:")
        print(f"[RESPONSE] {response.text}")
        
        # Try to get model info to check account status
        print("\n[CHECK] Checking available models...")
        
        try:
            models = genai.list_models()
            available_models = []
            
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            
            print(f"[MODELS] Available models: {len(available_models)}")
            for model_name in available_models[:5]:  # Show first 5
                print(f"   - {model_name}")
            
            if len(available_models) > 5:
                print(f"   ... and {len(available_models) - 5} more")
            
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
