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
    
    def _perform_ocr_on_images(self, image_paths: List[str]) -> Tuple[str, Optional[str]]:
        """Perform OCR on images to extract text and VIN"""
        all_text = ""
        vin_number = None
        
        if not self.vision_client:
            print("Vision API not available, skipping OCR")
            return "", None
        
        for idx, image_path in enumerate(image_paths):
            try:
                with open(image_path, 'rb') as image_file:
                    content = image_file.read()
                
                image = vision.Image(content=content)
                response = self.vision_client.text_detection(image=image)
                texts = response.text_annotations
                
                if texts:
                    # First annotation contains all text
                    full_text = texts[0].description
                    all_text += f"Image {idx+1}: {full_text}\n"
                    
                    # Extract VIN if not already found
                    if not vin_number:
                        vin_number = self._extract_vin_from_text(full_text)
                        if vin_number:
                            print(f"VIN detected: {vin_number}")
                        
            except Exception as e:
                print(f"Error performing OCR on {image_path}: {e}")
        
        return all_text, vin_number
    
    def identify_part_from_multiple_images(self, image_paths: List[str]) -> Dict:
        """
        Identify auto part from multiple images using a SINGLE Gemini API call
        Combines all three steps into one comprehensive prompt
        """
        start_time = datetime.now()
        
        # Initialize debug output with current API status
        self.debug_output = {
            "api_status": {
                "demo_mode": self.demo_mode,
                "api_client": "gemini" if hasattr(self, 'model') and self.model else None,
                "api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
                "vision_api_configured": bool(self.vision_client is not None),
                "gemini_api_configured": bool(hasattr(self, 'model') and self.model is not None)
            },
            "step1_ocr_raw": {},
            "step2_fitment_raw": {},
            "step3_analysis_raw": {},
            "raw_gemini_responses": [],
            "workflow_steps": [f"Started processing at {start_time}"],
            "processing_time": 0,
            "extracted_part_numbers": []
        }
        
        if self.demo_mode:
            demo_result = self._get_demo_response()
            demo_result["debug_output"] = self.debug_output
            return demo_result
        
        try:
            # Perform OCR on images first (using paths)
            ocr_text, vin_number = self._perform_ocr_on_images(image_paths)
            self.debug_output["step1_ocr_raw"] = {
                "ocr_text": ocr_text,
                "vin_number": vin_number,
                "timestamp": datetime.now().isoformat()
            }
            
            # Encode all images
            encoded_images = []
            for image_path in image_paths:
                with open(image_path, "rb") as image_file:
                    encoded_images.append(image_file.read())
            
            # SINGLE COMPREHENSIVE PROMPT that combines all 3 steps
            result = self._single_comprehensive_analysis(encoded_images, ocr_text, vin_number)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self.debug_output["processing_time"] = processing_time
            self.debug_output["workflow_steps"].append(f"Completed processing in {processing_time:.2f} seconds")
            
            # Ensure debug output is included in the result
            if not isinstance(result, dict):
                result = {"part_name": "Unknown Part", "description": "Analysis completed but no valid result format"}
            
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

    def _single_comprehensive_analysis(self, images: List[bytes], ocr_text: str, vin_number: Optional[str]) -> Dict:
        """
        Single comprehensive Gemini API call using dynamic scenario-based prompt
        """
        if self.demo_mode:
            return self._get_demo_response()
        
        try:
            # Extract part numbers from OCR text if available
            part_numbers_found = []
            if ocr_text:
                # Look for patterns that match part numbers
                part_numbers_found = re.findall(r'\b[A-Z0-9]{5,}[-A-Z0-9]*\b', ocr_text)
                # Filter out VIN if it was detected
                if vin_number:
                    part_numbers_found = [p for p in part_numbers_found if p != vin_number]
            
            # Determine which scenario we're in
            scenario = "C"  # Default to C (images only)
            scenario_text = ""
            
            if part_numbers_found:
                scenario = "A"
                scenario_text = f"\n**SCENARIO A: I have images AND a list of possible part numbers from an OCR scan.**\nMy OCR scan returned the following potential numbers. Please verify which of these are correct by cross-referencing all images, identify the primary part number, and use it for your research.\nOCR Results: {', '.join(part_numbers_found[:10])}\n"
            elif ocr_text and not part_numbers_found:
                scenario = "B"
                scenario_text = "\n**SCENARIO B: I have images, but OCR found NO part numbers.**\nMy OCR scan did not return any usable numbers. Your task will be to identify the part based on its visual characteristics across all images.\n"
            else:
                scenario_text = "\n**SCENARIO C: I am only providing images.**\nPlease analyze the images from scratch.\n"
            
            # Build the dynamic prompt
            prompt = f"""You are an expert eBay reseller specializing in used auto parts. Your goal is to provide all the necessary information for me to create a profitable eBay listing quickly.

I have attached {len(images)} images of a single auto part. It is critical that you analyze ALL of them to get a complete understanding of the part and its condition.
{scenario_text}"""
            
            # Add VIN if available
            if vin_number:
                prompt += f"\n--- VIN PROVIDED ---\n**VIN: {vin_number}**\nUse this VIN to dramatically improve fitment accuracy.\n"
            
            # Add the task instructions
            prompt += """
--- YOUR TASK ---

Based on a THOROUGH review of ALL images and the information I've provided, perform the following steps:

**STEP 1: VISUAL ANALYSIS & IDENTIFICATION**
1. **Part Type:** What specific type of auto part is this?
2. **Part Numbers:**"""
            
            if scenario == "A":
                prompt += "\n   * Confirm which of the provided numbers are accurate and visible. Identify the primary OEM part number."
            else:
                prompt += "\n   * Transcribe ALL visible part numbers. If none, state 'No part number visible.'"
            
            if vin_number:
                prompt += "\n   * Use the VIN to help verify the correct part number for that specific vehicle."
            
            prompt += """
3. **Brand/Manufacturer:** Identify any visible brands.
4. **Condition:** Synthesize the part's overall condition from ALL images. Note any scratches, broken tabs, cracked lenses, rust, or missing components visible across ANY of the photos.

**STEP 2: FITMENT & COMPATIBILITY RESEARCH**
1. **Vehicle Fitment:**"""
            
            if vin_number:
                prompt += "\n   * Use the VIN as the primary source of truth for the source vehicle's identity (Year, Make, Model, and Trim)."
            
            prompt += """
   * Using the primary part number (if available), list all vehicle Makes, Models, and Year range(s) this part fits.
2. **Compatibility Notes:** Mention any important details (e.g., "Fits Halogen models only," "For vehicles with 2.4L engine").

**STEP 3: PRICING & MARKET ANALYSIS**
1. **Price Range:** Provide a suggested "Buy It Now" price range for this part in its current condition on eBay.
2. **Competitive Listings (Comps):** Provide 2-3 links to current or recently sold eBay listings.

**STEP 4: EBAY LISTING OPTIMIZATION**
1. **Optimized Title:** Generate a keyword-rich eBay title. If the part number is confirmed, include it.
2. **Suggested Keywords:** List 5-10 additional keywords a buyer might use."""
            
            # Prepare content with images
            content = [prompt]
            for img_bytes in encoded_images:
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
            
            # Store COMPLETE debug data with full prompt and response
            self.debug_output["prompt_sent"] = prompt  # Store the full prompt
            self.debug_output["full_response"] = response_text  # Store the full response
            self.debug_output["scenario_used"] = scenario
            self.debug_output["images_count"] = len(encoded_images)
            
            # Legacy debug fields for compatibility
            self.debug_output["step1_ocr_raw"] = {
                "raw_text": response_text[:500],
                "confidence_score": 0.9,
                "gemini_ocr_text": "Single comprehensive call"
            }
            self.debug_output["step2_fitment_raw"] = "Included in single call"
            self.debug_output["step3_analysis_raw"] = "Included in single call"
            
            self.debug_output["raw_gemini_responses"].append({
                "step": f"dynamic_analysis_scenario_{scenario}",
                "prompt": prompt[:1000] + "..." if len(prompt) > 1000 else prompt,
                "response": response.text,  # Store FULL response
                "api_calls_made": 1,
                "scenario": scenario,
                "vin_used": bool(vin_number),
                "ocr_parts_found": len(part_numbers_found)
            })
            
            # Parse the comprehensive response
            result = self._parse_comprehensive_response(response_text)
            
            self.debug_output["workflow_steps"].append(f"Step 3: Gemini Analysis (Scenario {scenario})")
            if vin_number:
                self.debug_output["workflow_steps"].append(f"Using VIN: {vin_number}")
            if part_numbers_found:
                self.debug_output["workflow_steps"].append(f"OCR Part Numbers: {', '.join(part_numbers_found[:5])}")
            
            self.debug_output["extracted_part_numbers"] = result.get('part_numbers', [])
            
            return result
            
        except Exception as e:
            print(f"Comprehensive analysis error: {str(e)}")
            self.debug_output["workflow_steps"].append(f"Analysis error: {str(e)}")
            return self._get_fallback_response()

    def _parse_comprehensive_response(self, response_text: str) -> Dict:
        """Parse the dynamic scenario-based response format"""
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
            "suggested_keywords": [],
            "confidence_score": 0.85
        }
        
        lines = response_text.split('\n')
        current_section = ""
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect main steps
            if "STEP 1:" in line or "VISUAL ANALYSIS" in line:
                current_step = "step1"
                continue
            elif "STEP 2:" in line or "FITMENT" in line:
                current_step = "step2"
                continue
            elif "STEP 3:" in line or "PRICING" in line or "MARKET ANALYSIS" in line:
                current_step = "step3"
                continue
            elif "STEP 4:" in line or "EBAY LISTING" in line:
                current_step = "step4"
                continue
            
            # Parse based on current step
            if current_step == "step1":
                if "Part Type:" in line:
                    part_type = line.split("Part Type:", 1)[1].strip()
                    result["part_name"] = part_type.strip('*').strip()
                    result["name"] = result["part_name"]  # For compatibility
                elif "Part Number" in line:
                    # Handle various formats of part number lines
                    if ":" in line:
                        numbers_text = line.split(":", 1)[1].strip()
                        # Extract part numbers, handling various formats
                        numbers = re.findall(r'\b[A-Z0-9]{4,}[-A-Z0-9]*\b', numbers_text)
                        if numbers:
                            result["part_numbers"].extend(numbers)
                elif "Brand" in line or "Manufacturer" in line:
                    if ":" in line:
                        result["brand"] = line.split(":", 1)[1].strip().strip('*').strip()
                elif "Condition:" in line:
                    result["condition"] = line.split("Condition:", 1)[1].strip().strip('*').strip()
            
            elif current_step == "step2":
                if "Vehicle Fitment:" in line or "Fitment:" in line:
                    # Next lines will contain the fitment info
                    current_section = "fitment"
                elif current_section == "fitment" and line and not line.startswith("**"):
                    # Parse fitment lines
                    if "Make" in line or "Model" in line or "Year" in line:
                        # Extract make/model/year info
                        if not result["vehicles"]:
                            result["vehicles"] = line
                        else:
                            result["vehicles"] += ", " + line
                    elif result["vehicles"]:
                        result["vehicles"] += " " + line
                elif "Compatibility Notes:" in line:
                    current_section = "compatibility"
                elif current_section == "compatibility" and line and not line.startswith("**"):
                    result["fitment_notes"] = line
            
            elif current_step == "step3":
                if "Price Range:" in line or "Buy It Now" in line:
                    try:
                        # Extract price range
                        match = re.search(r'\$([0-9,]+)\s*[-–]\s*\$([0-9,]+)', line)
                        if match:
                            result["price_range"]["low"] = float(match.group(1).replace(',', ''))
                            result["price_range"]["high"] = float(match.group(2).replace(',', ''))
                            # Set average as recommended price
                            result["price"] = (result["price_range"]["low"] + result["price_range"]["high"]) / 2
                            result["estimated_price"] = result["price"]
                            result["market_price"] = result["price"]
                            result["quick_sale_price"] = result["price_range"]["low"]
                    except:
                        pass
            
            elif current_step == "step4":
                if "Optimized Title:" in line:
                    title = line.split("Optimized Title:", 1)[1].strip().strip('*').strip()
                    result["ebay_title"] = title[:80]  # Limit to 80 chars
                elif "Suggested Keywords:" in line:
                    keywords = line.split("Suggested Keywords:", 1)[1].strip()
                    result["suggested_keywords"] = [k.strip() for k in keywords.split(',') if k.strip()]
        
        
        # Build description from parsed data if not already set
        if not result["description"]:
            desc_parts = []
            if result["part_name"]:
                desc_parts.append(f"This is a {result['part_name']}")
            if result["brand"]:
                desc_parts.append(f"manufactured by {result['brand']}")
            if result["vehicles"]:
                desc_parts.append(f"compatible with {result['vehicles']}")
            if result["condition"]:
                desc_parts.append(f"in {result['condition'].lower()} condition")
            if result["part_numbers"]:
                desc_parts.append(f"Part numbers: {', '.join(result['part_numbers'])}")
            if result["fitment_notes"]:
                desc_parts.append(result["fitment_notes"])
            
            if desc_parts:
                result["description"] = ". ".join(desc_parts) + "."
            else:
                result["description"] = "Auto part in good condition. Please verify fitment before purchasing."
        
        # Ensure vehicles string is populated
        if not result["vehicles"] and result["make"] and result["model"]:
            vehicles = f"{result['make']} {result['model']}"
            if result["year_range"]:
                vehicles += f" {result['year_range']}"
            result["vehicles"] = vehicles
        
        # Ensure eBay title is set
        if not result["ebay_title"] and result["part_name"]:
            title_parts = []
            if result["brand"]:
                title_parts.append(result["brand"])
            title_parts.append(result["part_name"])
            if result["part_numbers"] and len(result["part_numbers"]) > 0:
                title_parts.append(result["part_numbers"][0])
            if result["vehicles"]:
                # Shorten vehicles for title
                vehicle_short = result["vehicles"].split(',')[0].strip()
                if len(vehicle_short) < 30:
                    title_parts.append(vehicle_short)
            result["ebay_title"] = " ".join(title_parts)[:80]
        
        # Ensure price fields are set
        if result["price"] > 0:
            result["estimated_price"] = result["price"]
            result["market_price"] = result["price"]
            if result["quick_sale_price"] == 0:
                result["quick_sale_price"] = result["price"] * 0.8  # 80% for quick sale
        
        # Set reasonable defaults if prices are missing
        if result["price"] == 0 and result["price_range"]["high"] > 0:
            result["price"] = (result["price_range"]["low"] + result["price_range"]["high"]) / 2
            result["estimated_price"] = result["price"]
            result["market_price"] = result["price"]
            result["quick_sale_price"] = result["price"] * 0.85
        
        # Determine category based on part type
        if result["part_name"]:
            result["category"] = self._determine_category(result["part_name"])
        
        return result

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
