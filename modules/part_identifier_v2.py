import os
import json
import base64
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai

# Try to import Vision API - make it optional
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
        """Initialize the Part Identifier with Google Vision OCR and Gemini 2.5 Pro"""
        
        # Initialize Vision API client
        if VISION_AVAILABLE:
            try:
                # Check if credentials are set
                if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                    self.vision_client = vision.ImageAnnotatorClient()
                    self.vision_available = True
                    print("Google Vision API initialized successfully")
                else:
                    self.vision_client = None
                    self.vision_available = False
                    print("WARNING: GOOGLE_APPLICATION_CREDENTIALS not set, Vision OCR will be disabled")
            except Exception as e:
                print(f"WARNING: Could not initialize Vision API: {e}")
                self.vision_client = None
                self.vision_available = False
        else:
            self.vision_client = None
            self.vision_available = False
            print("Vision API not available - OCR features disabled")
        
        # Initialize Gemini API
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            self.demo_mode = False
            print("Using Google Gemini 2.5 Pro for AI analysis")
        else:
            self.model = None
            self.demo_mode = True
            print("WARNING: Running in demo mode - no Gemini API key found")
        
        # Initialize debug data storage
        self.debug_output = {
            "api_status": {
                "demo_mode": self.demo_mode,
                "vision_api_configured": bool(self.vision_client),
                "gemini_api_configured": bool(gemini_key),
                "api_client": "gemini" if gemini_key else None,
                "api_key_configured": bool(gemini_key)
            },
            "workflow_steps": [],
            "step1_vision_ocr": {},
            "step2_dynamic_prompt": {},
            "step3_gemini_analysis": {},
            "raw_api_responses": [],
            "raw_gemini_responses": [],  # Add this for frontend compatibility
            "extracted_part_numbers": [],
            "timing": {}
        }
    
    def identify_part_from_multiple_images(self, image_paths: List[str]) -> Dict:
        """
        Main entry point for part identification using OCR-first approach
        """
        start_time = datetime.now()
        
        if self.demo_mode:
            return self._get_demo_response()
        
        try:
            # Step 1: Google Vision OCR on all images
            ocr_results = self._perform_vision_ocr(image_paths)
            
            # Step 2: Process OCR results and determine scenario
            scenario, part_numbers, ocr_text = self._process_ocr_results(ocr_results)
            
            # Step 3: Build dynamic prompt based on OCR results
            dynamic_prompt = self._build_dynamic_prompt(
                image_count=len(image_paths),
                scenario=scenario,
                ocr_results=ocr_text,
                part_numbers=part_numbers
            )
            
            # Step 4: Send to Gemini with all images
            result = self._analyze_with_gemini(image_paths, dynamic_prompt)
            
            # Calculate processing time
            self.debug_output["processing_time"] = (datetime.now() - start_time).total_seconds()
            
            # Add debug output to result
            result["debug_output"] = self.debug_output
            
            return result
            
        except Exception as e:
            print(f"ERROR in identify_part_from_multiple_images: {e}")
            return self._get_error_response(str(e))
    
    def _perform_vision_ocr(self, image_paths: List[str]) -> List[Dict]:
        """
        Step 1: Use Google Vision API to extract text from all images
        """
        self.debug_output["workflow_steps"].append("Step 1: Google Vision OCR on all images")
        ocr_results = []
        
        if not self.vision_available or not self.vision_client:
            print("Vision API not available, skipping OCR step")
            self.debug_output["step1_vision_ocr"] = {
                "status": "skipped",
                "reason": "Vision API not configured or not available"
            }
            return []
        
        for idx, image_path in enumerate(image_paths):
            try:
                with open(image_path, 'rb') as image_file:
                    content = image_file.read()
                
                if VISION_AVAILABLE:
                    image = vision.Image(content=content)
                    response = self.vision_client.text_detection(image=image)
                else:
                    raise Exception("Vision API not available")
                texts = response.text_annotations
                
                if texts:
                    full_text = texts[0].description if texts else ""
                    ocr_results.append({
                        "image_index": idx,
                        "image_path": image_path,
                        "full_text": full_text,
                        "text_blocks": [text.description for text in texts[1:]]  # Individual text blocks
                    })
                    
                    # Create response dict for debug output
                    response_dict = {
                        "full_text": full_text,
                        "text_blocks": [text.description for text in texts[1:20]]  # First 20 blocks for debug
                    }
                    
                    # Add to debug output
                    vision_response_data = {
                        "step": "Step 1: Google Vision OCR",
                        "api": "Google Vision API",
                        "raw_request": {
                            "method": "TEXT_DETECTION",
                            "image_size": len(image_content)
                        },
                        "raw_response": response_dict,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Add to both fields for compatibility
                    self.debug_output["raw_api_responses"].append(vision_response_data)
                    self.debug_output["raw_gemini_responses"].append(vision_response_data)
                
            except Exception as e:
                print(f"Error performing OCR on image {idx}: {e}")
                ocr_results.append({
                    "image_index": idx,
                    "image_path": image_path,
                    "error": str(e)
                })
        
        # Store OCR summary in debug
        all_text = " ".join([r.get("full_text", "") for r in ocr_results if "full_text" in r])
        self.debug_output["step1_vision_ocr"] = {
            "images_processed": len(image_paths),
            "ocr_success_count": len([r for r in ocr_results if "full_text" in r]),
            "combined_text": all_text[:1000]  # First 1000 chars
        }
        
        return ocr_results
    
    def _process_ocr_results(self, ocr_results: List[Dict]) -> Tuple[str, List[str], str]:
        """
        Process OCR results to extract part numbers and determine scenario
        """
        self.debug_output["workflow_steps"].append("Processing OCR results for part numbers")
        
        # Combine all OCR text
        all_text = " ".join([r.get("full_text", "") for r in ocr_results if "full_text" in r])
        
        # Extract potential part numbers using various patterns
        part_number_patterns = [
            r'\b[A-Z0-9]{2,}-[A-Z0-9]{2,}(?:-[A-Z0-9]+)*\b',  # XX-XXXX-XXX format
            r'\b[0-9]{5,}[A-Z]{1,3}\b',  # 12345ABC format
            r'\b[A-Z]{2,4}[0-9]{4,}\b',  # ABC1234 format
            r'\b[0-9]{8,12}\b',  # Pure numeric 8-12 digits
            r'\b[A-Z0-9]{10,}\b',  # Long alphanumeric
        ]
        
        part_numbers = []
        for pattern in part_number_patterns:
            matches = re.findall(pattern, all_text.upper())
            part_numbers.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_part_numbers = []
        for pn in part_numbers:
            if pn not in seen:
                seen.add(pn)
                unique_part_numbers.append(pn)
        
        # Store in debug output
        self.debug_output["extracted_part_numbers"] = unique_part_numbers
        
        # Determine scenario
        if unique_part_numbers:
            scenario = "A"  # OCR found part numbers
        elif all_text.strip():
            scenario = "B"  # OCR found text but no clear part numbers
        else:
            scenario = "C"  # No OCR results
        
        self.debug_output["step2_dynamic_prompt"]["scenario"] = scenario
        self.debug_output["step2_dynamic_prompt"]["part_numbers_found"] = len(unique_part_numbers)
        
        return scenario, unique_part_numbers, all_text
    
    def _build_dynamic_prompt(self, image_count: int, scenario: str, 
                             ocr_results: str, part_numbers: List[str]) -> str:
        """
        Build the Ultimate Dynamic Prompt based on OCR results
        """
        self.debug_output["workflow_steps"].append(f"Building dynamic prompt for Scenario {scenario}")
        
        # Base prompt template
        prompt = f"""You are an expert eBay reseller specializing in used auto parts. Your goal is to provide all the necessary information for me to create a profitable eBay listing quickly.

**I have attached {image_count} images of a single auto part for your review. It is critical that you analyze ALL of them to get a complete understanding of the part and its condition.**

"""
        
        # Add scenario-specific section
        if scenario == "A":
            prompt += f"""**SCENARIO A: I have images AND a list of possible part numbers from an OCR scan.**
My OCR scan returned the following potential numbers. Please verify which of these are correct by cross-referencing all images, identify the primary part number, and use it for your research.
OCR Results: {', '.join(part_numbers)}

"""
        elif scenario == "B":
            prompt += f"""**SCENARIO B: I have images, but OCR found NO clear part numbers.**
My OCR scan found the following text but no clear part numbers. Your task will be to identify the part based on its visual characteristics across all images.
OCR Text Found: {ocr_results[:500]}

"""
        else:  # scenario == "C"
            prompt += """**SCENARIO C: I am only providing images.**
Please analyze the images from scratch.

"""
        
        # Add the task instructions
        prompt += """**YOUR TASK**

Based on a THOROUGH review of ALL images and the scenario above, perform the following steps:

**STEP 1: VISUAL ANALYSIS & IDENTIFICATION**
1. **Part Type:** What specific type of auto part is this?
2. **Part Numbers:**"""
        
        if scenario == "A":
            prompt += """
   * Confirm which of the provided OCR numbers are accurate and visible. Identify the primary OEM part number."""
        else:
            prompt += """
   * Transcribe ALL visible part numbers, manufacturer IDs, and casting numbers (check all images for different angles and labels). If none, state "No part number visible."""
        
        prompt += """
3. **Brand/Manufacturer:** Identify any visible brands.
4. **Condition:** Synthesize the part's overall condition from ALL images. Note any scratches, broken tabs, cracked lenses, rust, missing components, or other damage visible across ANY of the photos. Be thorough, as if you were creating a damage report for a listing.

**STEP 2: FITMENT & COMPATIBILITY RESEARCH**
1. **Vehicle Fitment:** Using the primary part number (if available), list the Make, Model, and Year range(s) this part fits.
2. **Compatibility Notes:** Mention any important details (e.g., "Fits Halogen models only")."""
        
        if scenario == "B":
            prompt += """
3. **No Number Notice:** State clearly that fitment is a "best guess" based on visual matching and recommend the buyer verify compatibility."""
        
        prompt += """

**STEP 3: PRICING & MARKET ANALYSIS**
1. **Price Range:** Provide a suggested "Buy It Now" price range for this part in its current condition on eBay.
2. **Competitive Listings:** Mention typical price ranges you would expect for this type of part.

**STEP 4: EBAY LISTING OPTIMIZATION**
1. **Optimized Title:** Generate a keyword-rich eBay title (max 80 characters). If the part number is confirmed, include it. If not, make the title descriptive.
2. **Suggested Keywords:** List 5-10 additional keywords a buyer might use to find this part.

Please be thorough and accurate, as this information will be used to create a real eBay listing."""
        
        # Store FULL prompt in debug output (no truncation)
        self.debug_output["step2_dynamic_prompt"]["prompt_preview"] = prompt  # Show full prompt
        self.debug_output["step2_dynamic_prompt"]["full_prompt_length"] = len(prompt)
        
        return prompt
    
    def _analyze_with_gemini(self, image_paths: List[str], prompt: str) -> Dict:
        """
        Send images and dynamic prompt to Gemini 2.5 Pro for analysis
        """
        self.debug_output["workflow_steps"].append("Step 3: Sending to Gemini 2.5 Pro for analysis")
        
        try:
            # Prepare images for Gemini
            encoded_images = []
            for image_path in image_paths:
                with open(image_path, "rb") as image_file:
                    encoded_images.append(image_file.read())
            
            # Build content for Gemini - using inline_data format
            from PIL import Image
            import io
            
            # First add the text prompt
            content_parts = []
            
            # Add images using the proper inline_data format
            for img_bytes in encoded_images:
                # Open as PIL Image to verify it's valid
                img = Image.open(io.BytesIO(img_bytes))
                # Add as inline_data blob
                content_parts.append({
                    'inline_data': {
                        'mime_type': 'image/jpeg',
                        'data': base64.b64encode(img_bytes).decode('utf-8')
                    }
                })
            
            # Add the prompt text after images
            content_parts.append({'text': prompt})
            
            # Debug: Check content structure before sending
            print(f"DEBUG: Content parts type: {type(content_parts)}, Length: {len(content_parts)}")
            for i, part in enumerate(content_parts):
                if 'text' in part:
                    print(f"DEBUG: Part {i} is text, length: {len(part['text'])}")
                elif 'inline_data' in part:
                    print(f"DEBUG: Part {i} is image with mime_type: {part['inline_data']['mime_type']}")
            
            # Send to Gemini with proper format
            try:
                print(f"DEBUG: About to call model.generate_content")
                response = self.model.generate_content(content_parts)
                print(f"DEBUG: Response received, type: {type(response)}")
                response_text = response.text
                print(f"DEBUG: Response text extracted, length: {len(response_text)}")
            except Exception as e:
                print(f"DEBUG: Exception in generate_content: {type(e).__name__}: {str(e)}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                raise
            
            # Add FULL content to debug output (no truncation)
            gemini_response_data = {
                "step": "Gemini Analysis",
                "model": "gemini-2.5-pro",
                "prompt": prompt,  # Full prompt, not truncated
                "raw_response": response_text,  # Full response
                "images_count": len(image_paths),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to both fields for compatibility
            self.debug_output["raw_api_responses"].append(gemini_response_data)
            self.debug_output["raw_gemini_responses"].append(gemini_response_data)
            
            # Parse the response first
            parsed_result = self._parse_gemini_response(response_text)
            
            # Create properly mapped result for frontend
            result = {
                "part_name": parsed_result.get("name", "Unknown Part"),
                "seo_title": parsed_result.get("ebay_title", ""),
                "description": parsed_result.get("description", ""),
                "part_number": parsed_result.get("part_numbers", [""])[0] if parsed_result.get("part_numbers") else "",
                "part_numbers": parsed_result.get("part_numbers", []),
                "estimated_price": parsed_result.get("price", 100),
                "weight_lbs": parsed_result.get("weight", ""),
                "dimensions_inches": parsed_result.get("dimensions", ""),
                "make": parsed_result.get("make", ""),
                "model": parsed_result.get("model", ""),
                "year_range": parsed_result.get("year_range", ""),
                "condition": parsed_result.get("condition", "Used"),
                "color": parsed_result.get("color", ""),
                "is_oem": parsed_result.get("is_oem", False),
                "brand": parsed_result.get("brand", ""),
                "vehicles": parsed_result.get("vehicles", ""),
                "category": parsed_result.get("category", ""),
                "price_range": parsed_result.get("price_range", dict()),
                "key_features": parsed_result.get("key_features", []),
                "fitment_notes": parsed_result.get("fitment_notes", ""),
                "confidence_score": parsed_result.get("confidence_score", 7)
            }
            
            # Add parsed data to debug output for frontend use
            self.debug_output["step3_gemini_analysis"] = {
                "response_preview": response_text,  # Full response, not truncated
                "response_length": len(response_text),
                # Add all parsed fields for frontend to use
                "part_name": result["part_name"],
                "seo_title": result["seo_title"],
                "description": result["description"],
                "part_numbers": result["part_numbers"],
                "make": result["make"],
                "model": result["model"],
                "year_range": result["year_range"],
                "condition": result["condition"],
                "color": result["color"],
                "is_oem": result["is_oem"],
                "brand": result["brand"],
                "price": result["estimated_price"],
                "price_range": f"${result.get('price_range', {}).get('low', 0)}-${result.get('price_range', {}).get('high', 0)}",
                "weight": result["weight_lbs"],
                "dimensions": result["dimensions_inches"],
                "fitment_notes": result["fitment_notes"],
                "vehicles": result["vehicles"]
            }
            
            return result
            
        except Exception as e:
            print(f"Error in Gemini analysis: {e}")
            return self._get_error_response(str(e))
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """
        Parse Gemini's response into structured data
        """
        result = {
            "name": "Auto Part",
            "ebay_title": "",
            "description": "",
            "category": "eBay Motors > Parts & Accessories",
            "vehicles": "",
            "price": 100,
            "price_range": {"low": 50, "high": 150},
            "condition": "Used",
            "part_numbers": [],
            "brand": "",
            "make": "",
            "model": "",
            "year_range": "",
            "color": "",
            "weight": "",
            "dimensions": "",
            "is_oem": False,
            "key_features": [],
            "fitment_notes": "",
            "confidence_score": 7
        }
        
        # First, let's look for specific patterns in the response
        # Look for "PART TYPE:" or similar
        part_type_match = re.search(r'(?:PART TYPE|Part Type|IDENTIFICATION):\s*([^\n]+)', response_text, re.IGNORECASE)
        if part_type_match:
            result["name"] = part_type_match.group(1).strip().replace('**', '').replace('*', '')
        else:
            # Try to extract from first substantive line
            lines = response_text.split('\n')
            for line in lines:
                clean_line = line.strip().replace('**', '').replace('*', '')
                if clean_line and len(clean_line) > 10:
                    # Remove common prefixes
                    for prefix in ['This is an', 'This is a', 'This appears to be an', 'This appears to be a', 'The part is an', 'The part is a']:
                        if clean_line.lower().startswith(prefix.lower()):
                            clean_line = clean_line[len(prefix):].strip()
                            break
                    
                    # Extract the part name (up to first period or comma)
                    if '.' in clean_line:
                        part_name = clean_line.split('.')[0].strip()
                    elif ',' in clean_line:
                        part_name = clean_line.split(',')[0].strip()
                    else:
                        part_name = clean_line
                    
                    # Limit length and clean up
                    if part_name and len(part_name) > 5:
                        result["name"] = part_name[:100] if len(part_name) > 100 else part_name
                        break
        
        # Clean text for further processing
        clean_text = str(response_text).replace('**', '').replace('*', '')
        
        # Build description from the full response (cleaned)
        result["description"] = clean_text[:500] if len(clean_text) > 500 else clean_text
        
        # Extract part numbers
        if "Part Number" in clean_text:
            pn_section = re.search(r'Part Numbers?:([^:]+?)(?:\n[A-Z]|\n\n|$)', clean_text, re.DOTALL)
            if pn_section:
                # Look for part numbers in various formats
                pn_text = pn_section.group(1)
                part_nums = re.findall(r'[A-Z0-9]{2,}(?:-[A-Z0-9]+)+|[0-9]{5,}[A-Z]+|[A-Z]{2,}[0-9]{4,}', pn_text)
                # Safely handle deduplication - part_nums should be strings from regex, but let's be safe
                try:
                    unique_parts = []
                    seen = set()
                    for pn in part_nums:
                        if isinstance(pn, str) and pn not in seen:
                            seen.add(pn)
                            unique_parts.append(pn)
                    result["part_numbers"] = unique_parts[:5]  # Keep top 5 unique
                except Exception as e:
                    print(f"DEBUG: Error processing part numbers: {e}")
                    result["part_numbers"] = part_nums[:5] if isinstance(part_nums, list) else []
        
        # Extract brand
        if "Brand" in clean_text or "Manufacturer" in clean_text:
            brand_match = re.search(r'(?:Brand|Manufacturer):\s*([^\n]+)', clean_text)
            if brand_match:
                brand = brand_match.group(1).strip()
                # Clean up brand name
                if brand and not brand.startswith('Unknown'):
                    result["brand"] = brand.split('.')[0].strip()  # Take first part before period
        
        # Extract fitment
        if "Vehicle Fitment:" in response_text:
            fitment_match = re.search(r'Vehicle Fitment:\s*([^\n]+)', response_text)
            if fitment_match:
                fitment = fitment_match.group(1).strip()
                result["vehicles"] = fitment
                
                # Try to extract make/model/year
                make_model_match = re.search(r'(\w+)\s+(\w+).*?(\d{4}(?:-\d{4})?)', fitment)
                if make_model_match:
                    result["make"] = make_model_match.group(1)
                    result["model"] = make_model_match.group(2)
                    result["year_range"] = make_model_match.group(3)
        
        # Extract condition
        if "Condition:" in response_text:
            condition_section = re.search(r'Condition:([^*]+?)(?:\n\*|\n\n)', response_text, re.DOTALL)
            if condition_section:
                condition_text = condition_section.group(1).strip()
                result["fitment_notes"] = condition_text[:200]  # Use as fitment notes
        
        # Extract price
        price_matches = re.findall(r'\$(\d+)(?:\s*-\s*\$?(\d+))?', response_text)
        if price_matches:
            prices = []
            for match in price_matches:
                prices.append(int(match[0]))
                if match[1]:
                    prices.append(int(match[1]))
            if prices:
                result["price"] = sum(prices) // len(prices)
                result["price_range"]["low"] = min(prices)
                result["price_range"]["high"] = max(prices)
        
        # Extract price
        if "Price" in response_text:
            price_match = re.search(r'\$(\d+)(?:-\$?(\d+))?', response_text)
            if price_match:
                low = int(price_match.group(1))
                high = int(price_match.group(2)) if price_match.group(2) else low + 50
                result["price"] = (low + high) // 2
                result["price_range"] = {"low": low, "high": high}
        
        # Build eBay title (SEO optimized)
        title_parts = []
        
        # Add year/make/model if available
        if result["year_range"]:
            title_parts.append(result["year_range"])
        if result["make"]:
            title_parts.append(result["make"])
        if result["model"]:
            title_parts.append(result["model"])
            
        # Add the part name (cleaned)
        if result["name"]:
            # Remove redundant info already in make/model
            clean_name = result["name"]
            for word in title_parts:
                clean_name = clean_name.replace(word, "").strip()
            if clean_name:
                title_parts.append(clean_name)
        
        # Add part number if available
        if result["part_numbers"] and len(" ".join(title_parts)) < 60:
            title_parts.append(result["part_numbers"][0])
            
        # Add OEM if applicable
        if result.get("is_oem"):
            title_parts.append("OEM")
        
        result["ebay_title"] = " ".join(title_parts)[:80].strip()  # eBay title limit
        
        # If no title was built, use the part name
        if not result["ebay_title"]:
            result["ebay_title"] = result["name"][:80] if result["name"] else "Auto Part"
        
        # Extract keywords for features
        if "Keywords" in response_text or "Suggested Keywords" in response_text:
            keywords_match = re.search(r'(?:Suggested )?Keywords:\s*([^\n*]+)', response_text)
            if keywords_match:
                keywords = keywords_match.group(1).strip()
                result["key_features"] = [k.strip() for k in re.split(r'[,;]', keywords)][:5]
        
        # Build description
        description_parts = [
            f"**{result['name']}**",
            "",
{{ ... }}
        ]
        
        if result["part_numbers"]:
            description_parts.append(f"- Part Numbers: {', '.join(result['part_numbers'])}")
        if result["brand"]:
            description_parts.append(f"- Brand: {result['brand']}")
        
        description_parts.extend([
            "",
            "**Fitment Information:**",
            f"- {result['vehicles'] or 'Please verify fitment for your vehicle'}",
            ""
        ])
        
        if result["fitment_notes"]:
            description_parts.extend([
                "**Condition Notes:**",
                result["fitment_notes"],
                ""
            ])
        
        description_parts.extend([
            "**What's Included:**",
            "- Exactly what is shown in the photos",
            "- No additional hardware or accessories unless shown",
            "",
            "Please verify fitment with your vehicle before purchasing.",
            "Check all photos carefully for condition details."
        ])
        
        result["description"] = "\n".join(description_parts)
        
        # Set confidence based on how much info we extracted
        confidence = 5
        if result["part_numbers"]:
            confidence += 2
        if result["make"] and result["model"]:
            confidence += 2
        if result["price"] != 100:  # Not default price
            confidence += 1
        result["confidence_score"] = min(confidence, 10)
        
        return result
    
    def _get_demo_response(self) -> Dict:
        """Return demo response when in demo mode"""
        self.debug_output["workflow_steps"] = [
            "Step 1: Google Vision OCR (Demo Mode)",
            "Step 2: Building Dynamic Prompt (Demo Mode)",
            "Step 3: Gemini Analysis (Demo Mode)"
        ]
        
        self.debug_output["step1_vision_ocr"] = {
            "images_processed": 3,
            "ocr_success_count": 3,
            "combined_text": "DEMO: 89541-12C10 ADVICS ABS HYDRAULIC CONTROL UNIT TOYOTA LEXUS"
        }
        
        self.debug_output["extracted_part_numbers"] = ["89541-12C10", "ADVICS"]
        
        self.debug_output["step2_dynamic_prompt"] = {
            "scenario": "A",
            "part_numbers_found": 2,
            "prompt_preview": "You are an expert eBay reseller... SCENARIO A: OCR found part numbers..."
        }
        
        self.debug_output["step3_gemini_analysis"] = {
            "response_preview": "Part Type: ABS Hydraulic Control Unit...",
            "response_length": 2500
        }
        
        return {
            "name": "ABS Hydraulic Control Unit",
            "ebay_title": "Toyota Lexus ABS Control Module 89541-12C10 ADVICS OEM",
            "description": "**ABS Hydraulic Control Unit**\n\nDEMO MODE - This is a sample response",
            "category": "eBay Motors > Parts & Accessories > Car & Truck Parts",
            "vehicles": "Toyota Camry, Lexus ES350 2007-2011",
            "price": 125,
            "price_range": {"low": 80, "high": 180},
            "condition": "Used",
            "part_numbers": ["89541-12C10"],
            "brand": "ADVICS",
            "make": "Toyota",
            "model": "Camry",
            "year_range": "2007-2011",
            "key_features": ["OEM Part", "Tested Working", "Fast Shipping"],
            "fitment_notes": "Fits 2007-2011 Toyota Camry and Lexus ES350",
            "confidence_score": 9,
            "debug_output": self.debug_output
        }
    
    def _get_error_response(self, error_msg: str) -> Dict:
        """Return error response"""
        self.debug_output["workflow_steps"].append(f"Error: {error_msg}")
        
        return {
            "name": "Unknown Part",
            "ebay_title": "Auto Part - See Photos",
            "description": f"Error during identification: {error_msg}",
            "category": "eBay Motors > Parts & Accessories",
            "vehicles": "",
            "price": 50,
            "price_range": {"low": 25, "high": 100},
            "condition": "Used",
            "part_numbers": [],
            "confidence_score": 0,
            "debug_output": self.debug_output
        }
