import os
import json
import base64
from typing import Dict, List, Optional
from datetime import datetime
import google.generativeai as genai

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env file successfully")
except ImportError:
    print("WARNING: python-dotenv not installed, using system environment variables")

class PartIdentifier:
    def __init__(self):
        """Initialize the Part Identifier with Gemini 2.5 Pro"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        print(f"DEBUG: PartIdentifier.__init__ called")
        print(f"DEBUG: GEMINI_API_KEY: {'SET' if gemini_key else 'NOT SET'}")
        
        # Set demo mode first
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')  # Using Gemini 2.5 Pro
            self.demo_mode = False
            print("Using Google Gemini 2.5 Pro for AI analysis")
        else:
            self.model = None
            self.demo_mode = True
            print("WARNING: Running in demo mode - no Gemini API key found")
        
        # Initialize debug data storage (after demo_mode is set)
        self.debug_output = {
            "api_status": {
                "demo_mode": self.demo_mode,
                "api_client": "gemini" if gemini_key else None,
                "api_key_configured": bool(gemini_key)
            },
            "step1_ocr_raw": {},
            "step2_fitment_raw": {},
            "step3_analysis_raw": {},
            "raw_gemini_responses": [],
            "workflow_steps": [],
            "processing_time": 0,
            "extracted_part_numbers": []
        }

    def identify_part_from_multiple_images(self, image_paths: List[str]) -> Dict:
        """
        Identify auto part from multiple images using a SINGLE Gemini API call
        Combines all three steps into one comprehensive prompt
        """
        start_time = datetime.now()
        
        # Add to debug workflow
        self.debug_output["workflow_steps"].append(f"Started processing at {start_time}")
        
        if self.demo_mode:
            return self._get_demo_response()
        
        try:
            # Encode all images
            encoded_images = []
            for image_path in image_paths:
                with open(image_path, "rb") as image_file:
                    encoded_images.append(image_file.read())
            
            # SINGLE COMPREHENSIVE PROMPT that combines all 3 steps
            result = self._single_comprehensive_analysis(encoded_images)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self.debug_output["processing_time"] = processing_time
            
            # Add debug output to result
            result["debug_output"] = self.debug_output
            
            return result
            
        except Exception as e:
            print(f"Error in part identification: {str(e)}")
            self.debug_output["workflow_steps"].append(f"Error: {str(e)}")
            return {
                "name": "Error in Analysis",
                "description": f"Failed to analyze images: {str(e)}",
                "category": "Unknown",
                "vehicles": "Unknown",
                "price": 0,
                "condition": "Unknown",
                "debug_output": self.debug_output
            }

    def _single_comprehensive_analysis(self, images: List[bytes]) -> Dict:
        """
        Single comprehensive Gemini API call that does everything at once
        """
        self.debug_output["workflow_steps"].append("Single comprehensive analysis started")
        
        # Comprehensive prompt that combines all 3 steps
        prompt = """You are an expert eBay reseller specializing in auto parts. 
Analyze these images and provide a COMPLETE analysis in ONE response.

COMPREHENSIVE AUTO PART ANALYSIS:

1. IDENTIFICATION:
   - Part type (be specific: headlight, tail light, brake caliper, etc.)
   - Brand/Manufacturer
   - ALL visible part numbers (transcribe accurately)
   - Physical characteristics (color, style, size, mounting)
   - Condition assessment

2. FITMENT RESEARCH:
   - Make/Model/Year range this part fits
   - Verify part numbers against known databases
   - List compatible vehicles
   - OEM vs Aftermarket status

3. MARKET ANALYSIS:
   - Research eBay sold listings for this part
   - Determine market price range
   - Suggest optimal Buy It Now price
   - Quick sale price (for fast turnover)
   - Average market price

4. EBAY LISTING:
   - SEO-optimized title (max 80 chars)
   - Professional description
   - Key selling points
   - Recommended category

CRITICAL DISTINCTIONS:
- Headlight vs Tail light (headlights are clear/white, tail lights are red/amber)
- Left vs Right side
- OEM vs Aftermarket

FORMAT YOUR RESPONSE EXACTLY AS:

PART IDENTIFICATION:
Part Type: [specific type]
Brand: [manufacturer]
Part Numbers: [all numbers]
Condition: [condition]
Characteristics: [details]

FITMENT DATA:
Make: [make]
Model: [model]
Year Range: [years]
Compatible Vehicles: [list]
OEM/Aftermarket: [status]

MARKET ANALYSIS:
Market Price Range: $[low] - $[high]
Average Sold Price: $[average]
Suggested Buy It Now: $[price]
Quick Sale Price: $[price]

EBAY LISTING:
Title: [SEO title]
Category: [eBay category]
Description: [professional description]
Key Features: [bullet points]"""

        try:
            # Prepare content with images
            content = [prompt]
            for i, img_bytes in enumerate(images):
                content.append({
                    'mime_type': 'image/jpeg',
                    'data': base64.b64encode(img_bytes).decode('utf-8')
                })
            
            # SINGLE Gemini API call
            print("Making SINGLE Gemini API call for comprehensive analysis...")
            response = self.model.generate_content(
                content,
                generation_config={
                    'temperature': 0.1,  # Low for accuracy
                    'top_p': 0.9,
                    'max_output_tokens': 2048,  # Increased for comprehensive response
                }
            )
            
            response_text = response.text
            
            # Store debug data
            self.debug_output["step1_ocr_raw"] = {
                "raw_text": response_text[:500],
                "confidence_score": 0.9,
                "gemini_ocr_text": "Single comprehensive call"
            }
            self.debug_output["step2_fitment_raw"] = "Included in single call"
            self.debug_output["step3_analysis_raw"] = "Included in single call"
            
            self.debug_output["raw_gemini_responses"].append({
                "step": "Single Comprehensive Analysis",
                "model": "gemini-2.5-pro",
                "prompt": prompt[:500],
                "raw_response": response_text,
                "timestamp": datetime.now().isoformat(),
                "api_calls_made": 1  # ONLY ONE CALL!
            })
            
            # Parse the comprehensive response
            result = self._parse_comprehensive_response(response_text)
            
            self.debug_output["workflow_steps"].append(f"Single analysis complete: {result.get('part_name', 'Unknown')}")
            self.debug_output["extracted_part_numbers"] = result.get('part_numbers', [])
            
            return result
            
        except Exception as e:
            print(f"Comprehensive analysis error: {str(e)}")
            self.debug_output["workflow_steps"].append(f"Analysis error: {str(e)}")
            return self._get_fallback_response()

    def _parse_comprehensive_response(self, response_text: str) -> Dict:
        """Parse the comprehensive response from single Gemini call"""
        result = {
            "part_name": "",
            "name": "",  # Add 'name' field for compatibility
            "ebay_title": "",
            "description": "",
            "category": "Other Auto Parts",
            "vehicles": "",
            "price": 0,
            "estimated_price": 0,  # Add for compatibility
            "market_price": 0,  # Add for compatibility
            "quick_sale_price": 0,  # Add for compatibility
            "price_range": {"low": 0, "high": 0},
            "condition": "Used",
            "part_numbers": [],
            "brand": "",
            "make": "",
            "model": "",
            "year_range": "",
            "key_features": [],
            "fitment_notes": "",
            "confidence_score": 0.85
        }
        
        # Clean the response text first - remove any leading prompt artifacts
        clean_text = response_text
        prompt_starters = ["Of course", "Here is a detailed analysis", "Based on a thorough review"]
        for starter in prompt_starters:
            if starter in clean_text:
                parts = clean_text.split(starter, 1)
                if len(parts) > 1:
                    clean_text = parts[1]
        
        lines = clean_text.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "PART IDENTIFICATION" in line.upper():
                current_section = "identification"
            elif "FITMENT DATA" in line.upper():
                current_section = "fitment"
            elif "MARKET ANALYSIS" in line.upper():
                current_section = "market"
            elif "EBAY LISTING" in line.upper():
                current_section = "listing"
            
            # Parse based on current section
            if current_section == "identification":
                if "Part Type:" in line:
                    part_type = line.split("Part Type:", 1)[1].strip()
                    result["part_name"] = part_type
                elif "Brand:" in line:
                    result["brand"] = line.split("Brand:", 1)[1].strip()
                elif "Part Numbers:" in line or "Part Number:" in line:
                    numbers = line.split(":", 1)[1].strip()
                    result["part_numbers"] = [n.strip() for n in numbers.split(",")]
                elif "Condition:" in line:
                    result["condition"] = line.split("Condition:", 1)[1].strip()
                elif "Characteristics:" in line:
                    result["key_features"] = [line.split(":", 1)[1].strip()]
            
            elif current_section == "fitment":
                if "Make:" in line:
                    result["make"] = line.split("Make:", 1)[1].strip()
                elif "Model:" in line:
                    result["model"] = line.split("Model:", 1)[1].strip()
                elif "Year Range:" in line:
                    result["year_range"] = line.split("Year Range:", 1)[1].strip()
                elif "Compatible Vehicles:" in line:
                    result["vehicles"] = line.split(":", 1)[1].strip()
                elif "OEM/Aftermarket:" in line:
                    oem_status = line.split(":", 1)[1].strip()
                    if "OEM" in oem_status.upper():
                        result["key_features"].append("OEM Part")
            
            elif current_section == "market":
                if "Market Price Range:" in line:
                    try:
                        price_text = line.split(":", 1)[1].strip()
                        prices = price_text.replace("$", "").split("-")
                        if len(prices) == 2:
                            result["price_range"]["low"] = float(prices[0].strip())
                            result["price_range"]["high"] = float(prices[1].strip())
                    except:
                        pass
                elif "Average Sold Price:" in line:
                    try:
                        price = line.split(":", 1)[1].strip().replace("$", "")
                        result["market_price"] = float(price)
                    except:
                        pass
                elif "Suggested Buy It Now:" in line:
                    try:
                        price = line.split(":", 1)[1].strip().replace("$", "")
                        result["price"] = float(price)
                        result["estimated_price"] = float(price)
                    except:
                        pass
                elif "Quick Sale Price:" in line:
                    try:
                        price = line.split(":", 1)[1].strip().replace("$", "")
                        result["quick_sale_price"] = float(price)
                    except:
                        pass
            
            elif current_section == "listing":
                if "Title:" in line:
                    title = line.split("Title:", 1)[1].strip()
                    result["ebay_title"] = title[:80]  # Limit to 80 chars
                elif "Category:" in line:
                    result["category"] = line.split("Category:", 1)[1].strip()
                elif "Description:" in line:
                    # Extract only the description value, not the whole response
                    desc = line.split("Description:", 1)[1].strip()
                    # Stop at any section markers or prompt artifacts
                    for marker in ["Key Features:", "**", "###", "SCENARIO:", "CRITICAL:", "YOUR TASK:"]:
                        if marker in desc:
                            desc = desc.split(marker)[0].strip()
                            break
                    result["description"] = desc
                elif "Key Features:" in line:
                    features = line.split("Key Features:", 1)[1].strip()
                    if features and features not in result["key_features"]:
                        result["key_features"].append(features)
        
        # Build final part name if not set
        if not result["part_name"] and result["make"] and result["model"]:
            result["part_name"] = f"{result['make']} {result['model']} {result.get('year_range', '')} Part"
        
        # Ensure 'name' field matches 'part_name' for compatibility
        result["name"] = result["part_name"]
        
        # Build eBay title if not set
        if not result["ebay_title"]:
            title_parts = []
            if result["year_range"]:
                title_parts.append(result["year_range"])
            if result["make"]:
                title_parts.append(result["make"])
            if result["model"]:
                title_parts.append(result["model"])
            if result["part_name"]:
                title_parts.append(result["part_name"])
            if result["part_numbers"]:
                title_parts.append(result["part_numbers"][0])
            result["ebay_title"] = " ".join(title_parts)[:80]
        
        # Clean up description - remove any prompt text that leaked through
        if result["description"]:
            # Remove common prompt artifacts and clean up
            desc = result["description"]
            
            # Remove asterisks and excessive formatting
            desc = desc.replace("**", "").replace("*", "")
            
            # Remove prompt artifacts
            prompt_artifacts = [
                "SCENARIO:", "CRITICAL:", "YOUR TASK:", "Based on a thorough review",
                "perform the following steps:", "### STEP", "STEP", "Of course",
                "Here is a detailed analysis", "This is a", "It typically includes"
            ]
            for artifact in prompt_artifacts:
                if artifact in desc:
                    # Cut off at the artifact
                    desc = desc.split(artifact)[0].strip()
            
            # If description is too short or seems wrong, build a default one
            if len(desc) < 20 or desc.startswith("This is a"):
                desc_parts = []
                if result["part_name"]:
                    desc_parts.append(f"Genuine {result['part_name']}")
                if result["condition"]:
                    desc_parts.append(f"in {result['condition']} condition")
                if result["vehicles"]:
                    desc_parts.append(f"Compatible with: {result['vehicles']}")
                if desc_parts:
                    desc = ". ".join(desc_parts) + "."
                else:
                    desc = "Auto part in good condition. Please verify fitment before purchasing."
            
            result["description"] = desc[:500]  # Limit description length
        
        # Ensure price fields are set
        if result["price"] > 0:
            result["estimated_price"] = result["price"]
            result["market_price"] = result["price"]
            if result["quick_sale_price"] == 0:
                result["quick_sale_price"] = result["price"] * 0.8  # 80% for quick sale
        
        return result

    def _get_fallback_response(self) -> Dict:
        """Return fallback response when analysis fails"""
        return {
            "part_name": "Unknown Auto Part",
            "ebay_title": "Auto Part - Needs Identification",
            "description": "Auto part requiring identification",
            "category": "Other Auto Parts",
            "vehicles": "Unknown",
            "price": 0,
            "price_range": {"low": 0, "high": 0},
            "condition": "Used",
            "part_numbers": [],
            "brand": "Unknown",
            "make": "Unknown",
            "model": "Unknown",
            "year_range": "Unknown",
            "key_features": [],
            "fitment_notes": "",
            "confidence_score": 0
        }

    def _determine_category(self, part_type: str) -> str:
        """Determine eBay category based on part type"""
        part_type_lower = part_type.lower()
        
        if any(word in part_type_lower for word in ['headlight', 'tail light', 'taillight', 'fog light', 'turn signal']):
            return "Lighting"
        elif any(word in part_type_lower for word in ['brake', 'caliper', 'rotor', 'pad']):
            return "Brakes"
        elif any(word in part_type_lower for word in ['engine', 'motor', 'cylinder', 'piston']):
            return "Engine Components"
        elif any(word in part_type_lower for word in ['bumper', 'fender', 'hood', 'door', 'trunk']):
            return "Body Parts"
        elif any(word in part_type_lower for word in ['seat', 'dashboard', 'console', 'carpet']):
            return "Interior Parts"
        elif any(word in part_type_lower for word in ['battery', 'alternator', 'starter', 'fuse']):
            return "Electrical"
        elif any(word in part_type_lower for word in ['suspension', 'strut', 'shock', 'spring']):
            return "Suspension"
        elif any(word in part_type_lower for word in ['transmission', 'clutch', 'gear']):
            return "Transmission"
        elif any(word in part_type_lower for word in ['exhaust', 'muffler', 'catalytic']):
            return "Exhaust"
        elif any(word in part_type_lower for word in ['radiator', 'cooling', 'thermostat', 'water pump']):
            return "Cooling"
        elif any(word in part_type_lower for word in ['fuel', 'pump', 'injector', 'tank']):
            return "Fuel System"
        elif any(word in part_type_lower for word in ['wheel', 'tire', 'rim', 'hubcap']):
            return "Wheels & Tires"
        elif any(word in part_type_lower for word in ['mirror', 'glass', 'window', 'windshield']):
            return "Glass & Mirrors"
        else:
            return "Other Auto Parts"

    def _get_demo_response(self) -> Dict:
        """Return demo response when no API key is configured"""
        demo_debug = {
            "step1_ocr_raw": "DEMO MODE - Single comprehensive analysis",
            "step2_fitment_raw": "DEMO MODE - Included in single call",
            "step3_analysis_raw": "DEMO MODE - Included in single call",
            "raw_gemini_responses": [
                {
                    "step": "demo_single_analysis", 
                    "response": "Demo comprehensive response",
                    "api_calls_made": 1
                }
            ],
            "workflow_steps": [
                "Demo Mode Active - No API Key",
                "Single comprehensive analysis (demo)"
            ],
            "processing_time": 0.5
        }
        
        return {
            "part_name": "Toyota Camry 2018-2021 Headlight Assembly OEM 12345-67890",
            "ebay_title": "Toyota Camry 2018-2021 Headlight Assembly OEM 12345-67890",
            "description": "**DEMO MODE**\n\nThis is a demo response. Configure your Gemini API key to enable real analysis.",
            "category": "Lighting",
            "vehicles": "Toyota Camry 2018-2021",
            "price": 95,
            "price_range": {"low": 75, "high": 125},
            "condition": "Used - Good",
            "part_numbers": ["12345-67890"],
            "brand": "OEM",
            "make": "Toyota",
            "model": "Camry",
            "year_range": "2018-2021",
            "key_features": ["OEM quality", "Complete assembly"],
            "fitment_notes": "Fits all trim levels",
            "confidence_score": 0,
            "debug_output": demo_debug
        }
