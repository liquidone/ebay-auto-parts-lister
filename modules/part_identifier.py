import os
import json
import base64
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai

# Try to import Google Cloud Vision
try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    print("WARNING: google-cloud-vision not available, Vision OCR will be disabled")

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env file successfully")
except ImportError:
    print("WARNING: python-dotenv not installed, using system environment variables")

class PartIdentifier:
    def __init__(self):
        """Initialize the Part Identifier with Gemini 2.5 Pro and Google Vision OCR"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Initialize Vision client for OCR
        self.vision_client = None
        if VISION_AVAILABLE:
            try:
                self.vision_client = vision.ImageAnnotatorClient()
                print("Google Vision API initialized for OCR")
            except Exception as e:
                print(f"WARNING: Could not initialize Vision API: {e}")
                self.vision_client = None
        
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

    def _extract_vin_from_text(self, text: str) -> Optional[str]:
        """Extract VIN number from text using regex pattern"""
        # VIN pattern: 17 alphanumeric characters, excluding I, O, Q
        # Common VIN format: [A-HJ-NPR-Z0-9]{17}
        vin_pattern = r'\b[A-HJ-NPR-Z0-9]{17}\b'
        
        # Find all potential VINs
        matches = re.findall(vin_pattern, text.upper())
        
        if matches:
            # Return the first valid VIN found
            return matches[0]
        return None
    
    def _perform_ocr_on_images(self, image_paths: List[str]) -> Tuple[List[str], str, Optional[str]]:
        """Perform OCR on images to extract part numbers and VIN"""
        all_text = ""
        part_numbers = []
        vin_number = None
        
        if not self.vision_client:
            print("Vision API not available, skipping OCR")
            return [], "", None
        
        for image_path in image_paths:
            try:
                with open(image_path, 'rb') as image_file:
                    content = image_file.read()
                
                image = vision.Image(content=content)
                response = self.vision_client.text_detection(image=image)
                texts = response.text_annotations
                
                if texts:
                    # First annotation contains all text
                    full_text = texts[0].description
                    all_text += full_text + " "
                    
                    # Extract VIN if not already found
                    if not vin_number:
                        vin_number = self._extract_vin_from_text(full_text)
                        if vin_number:
                            print(f"VIN detected: {vin_number}")
                    
                    # Extract part numbers (common patterns)
                    # Look for patterns like: XXXXX-XXXXX, XXXX-XXX-XXX, etc.
                    part_patterns = [
                        r'\b[A-Z0-9]{5}-[A-Z0-9]{5}\b',  # Toyota/Lexus style
                        r'\b[A-Z0-9]{4}-[A-Z0-9]{3}-[A-Z0-9]{3}\b',  # Honda style
                        r'\b[A-Z0-9]{2}[A-Z0-9]{3}-[A-Z0-9]{5}\b',  # Ford style
                        r'\b[0-9]{8}\b',  # GM 8-digit
                        r'\b[A-Z0-9]{6,10}\b'  # Generic 6-10 character
                    ]
                    
                    for pattern in part_patterns:
                        found = re.findall(pattern, full_text.upper())
                        part_numbers.extend(found)
                        
            except Exception as e:
                print(f"Error performing OCR on {image_path}: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_parts = []
        for num in part_numbers:
            if num not in seen and num != vin_number:  # Don't include VIN as part number
                seen.add(num)
                unique_parts.append(num)
        
        return unique_parts[:10], all_text[:500], vin_number  # Limit to top 10 part numbers
    
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
        
        # Perform OCR on images first
        part_numbers, ocr_text, vin_number = self._perform_ocr_on_images(image_paths)
        
        # Determine scenario based on OCR results
        if part_numbers:
            scenario = "A"
            ocr_info = f"OCR Results: {', '.join(part_numbers)}"
        elif ocr_text.strip():
            scenario = "B"
            ocr_info = f"OCR Text Found: {ocr_text}"
        else:
            scenario = "C"
            ocr_info = ""
        
        # Build dynamic prompt based on OCR results
        prompt = """You are an expert eBay reseller specializing in used auto parts. Your goal is to provide all the necessary information for me to create a profitable eBay listing quickly.

I have attached multiple images of a single auto part. It is critical that you analyze ALL of them to get a complete understanding of the part and its condition.

--- SCENARIO THAT APPLIES ---

"""
        
        if scenario == "A":
            prompt += f"""**SCENARIO A: I have images AND a list of possible part numbers from an OCR scan.**
My OCR scan returned the following potential numbers. Please verify which of these are correct by cross-referencing all images, identify the primary part number, and use it for your research.
{ocr_info}
"""
        elif scenario == "B":
            prompt += f"""**SCENARIO B: I have images, but OCR found NO part numbers.**
My OCR scan did not return any usable numbers. Your task will be to identify the part based on its visual characteristics across all images.
{ocr_info}
"""
        else:
            prompt += """**SCENARIO C: I am only providing images.**
Please analyze the images from scratch.
"""
        
        # Add VIN information if available
        if vin_number:
            prompt += f"""
--- VIN PROVIDED ---
**VIN from the vehicle the part was removed from: {vin_number}**
This will dramatically improve fitment accuracy. Use this VIN as the primary source of truth for the source vehicle's identity.
"""
        else:
            prompt += """
--- NO VIN AVAILABLE ---
**No VIN was detected in the images.**
"""
        
        # Add the task section
        prompt += """
--- YOUR TASK ---

Based on a THOROUGH review of ALL images and the information I've provided, perform the following steps:

**STEP 1: VISUAL ANALYSIS & IDENTIFICATION**
1.  **Part Type:** What specific type of auto part is this?
2.  **Part Numbers:**
    * For Scenario A: Confirm which of the provided numbers are accurate and visible. Identify the primary OEM part number.
    * For Scenarios B & C: Transcribe ALL visible part numbers. **(If a VIN was provided, you can use it to help verify the correct part number for that specific vehicle).** If none, state "No part number visible."
3.  **Brand/Manufacturer:** Identify any visible brands.
4.  **Condition:** Synthesize the part's overall condition from ALL images. Note any scratches, broken tabs, cracked lenses, rust, or missing components visible across ANY of the photos.

**STEP 2: FITMENT & COMPATIBILITY RESEARCH**
1.  **Vehicle Fitment:**
    * **If a VIN was provided, use it as the primary source of truth for the source vehicle's identity (Year, Make, Model, and Trim).**
    * Using the primary part number (if available), list all vehicle Makes, Models, and Year range(s) this part fits.
2.  **Compatibility Notes:** Mention any important details (e.g., "Fits Halogen models only," "For vehicles with 2.4L engine").

**STEP 3: PRICING & MARKET ANALYSIS**
1.  **Price Range:** Provide a suggested "Buy It Now" price range for this part in its current condition on eBay.
2.  **Competitive Listings (Comps):** Provide 2-3 links to current or recently sold eBay listings.

**STEP 4: EBAY LISTING OPTIMIZATION**
1.  **Optimized Title:** Generate a keyword-rich eBay title. If the part number is confirmed, include it.
2.  **Suggested Keywords:** List 5-10 additional keywords a buyer might use."""

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
