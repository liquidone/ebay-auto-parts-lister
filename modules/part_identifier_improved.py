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
    print("✅ Loaded .env file successfully")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")

class PartIdentifier:
    def __init__(self):
        """Initialize the Part Identifier with Gemini 2.5 Pro"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        print(f"DEBUG: PartIdentifier.__init__ called")
        print(f"DEBUG: GEMINI_API_KEY: {'SET' if gemini_key else 'NOT SET'}")
        
        # Initialize debug data storage
        self.debug_output = {
            "step1_ocr_raw": "",
            "step2_fitment_raw": "",
            "step3_pricing_raw": "",
            "gemini_responses": [],
            "workflow_steps": [],
            "processing_time": 0
        }
        
        if gemini_key:
            genai.configure(api_key=gemini_key)
           
            self.demo_mode = False
            print("✅ Using Google Gemini 2.5 Pro for AI analysis")
        else:
            self.model = None
            self.demo_mode = True
            print("⚠️ WARNING: Running in demo mode - no Gemini API key found")

    async def identify_part_from_multiple_images(self, image_paths: List[str]) -> Dict:
        """
        Identify auto part from multiple images using simplified, effective prompting
        Based on the working Gemini prompt that achieves high accuracy
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
            
            # Step 1: Identify the Item (Simple, Direct Approach)
            step1_result = await self._step1_identify_item(encoded_images)
            
            # Step 2: Research Market Value
            step2_result = await self._step2_research_market(step1_result, encoded_images)
            
            # Step 3: Generate Final Report
            final_result = await self._step3_final_report(step1_result, step2_result)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self.debug_output["processing_time"] = processing_time
            
            # Add debug output to result
            final_result["debug_output"] = self.debug_output
            
            return final_result
            
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

    async def _step1_identify_item(self, images: List[bytes]) -> Dict:
        """
        Step 1: Simple, direct identification
        Focus on: brand, type, style, color, unique characteristics, fitment data
        """
        self.debug_output["workflow_steps"].append("Step 1: Identifying item")
        
        prompt = """You are an expert eBay reseller specializing in auto parts. 
Your sole purpose is to help me identify and price items for quick and profitable sales.

STEP 1: IDENTIFY THE ITEM

Analyze these images and identify:
1. What TYPE of auto part is this? (Be specific: headlight, tail light, brake caliper, etc.)
2. Brand/Manufacturer visible on the part
3. Part numbers (transcribe ALL visible part numbers accurately)
4. Physical characteristics (color, style, size, mounting type)
5. Fitment data visible on the part
6. Condition assessment

CRITICAL: Distinguish between similar parts:
- Headlight vs Tail light (headlights are clear/white, tail lights are red/amber)
- Left vs Right side
- OEM vs Aftermarket

Provide your analysis in this exact format:
PART TYPE: [specific type]
BRAND: [manufacturer name]
PART NUMBERS: [all visible numbers]
CHARACTERISTICS: [physical description]
FITMENT INFO: [any vehicle compatibility visible]
CONDITION: [assessment]"""

        try:
            # Prepare content for Gemini
            content = [prompt]
            for img in images:
                content.append({"mime_type": "image/jpeg", "data": base64.b64encode(img).decode()})
            
            # Generate with Gemini 2.5 Pro
            response = self.model.generate_content(
                content,
                generation_config={
                    'temperature': 0.1,  # Low for accuracy
                    'top_p': 0.9,
                    'max_output_tokens': 1024,
                }
            )
            
            response_text = response.text
            self.debug_output["step1_ocr_raw"] = response_text
            self.debug_output["gemini_responses"].append({
                "step": "identification",
                "response": response_text
            })
            
            # Parse the response
            result = self._parse_identification_response(response_text)
            self.debug_output["workflow_steps"].append(f"Step 1 complete: {result.get('part_type', 'Unknown')}")
            
            return result
            
        except Exception as e:
            print(f"Step 1 error: {str(e)}")
            self.debug_output["workflow_steps"].append(f"Step 1 error: {str(e)}")
            return {
                "part_type": "Unknown",
                "brand": "",
                "part_numbers": [],
                "characteristics": "",
                "fitment_info": "",
                "condition": "Used"
            }

    async def _step2_research_market(self, identification: Dict, images: List[bytes]) -> Dict:
        """
        Step 2: Research market value and validate fitment
        Use part numbers to find accurate fitment and pricing
        """
        self.debug_output["workflow_steps"].append("Step 2: Researching market value")
        
        part_numbers_str = ", ".join(identification.get("part_numbers", []))
        
        prompt = f"""You are an expert eBay reseller. Based on the identification:

PART TYPE: {identification.get('part_type', 'Unknown')}
BRAND: {identification.get('brand', 'Unknown')}
PART NUMBERS: {part_numbers_str}

STEP 2: RESEARCH AND VALIDATE

1. Using the part numbers, determine the EXACT vehicle fitment:
   - Make (Toyota, Honda, Nissan, etc.)
   - Model(s) 
   - Year range
   - Any trim levels or special editions

2. Research typical eBay "SOLD" listing prices for this part in used condition
   
3. Identify key selling points for the eBay title

IMPORTANT: If the part numbers suggest a different make than initially identified, 
trust the part number research. For example:
- Part numbers starting with 89541 are typically Toyota/Lexus
- Part numbers with format XXXXX-XXXXX are often OEM
- ADVICS is a Toyota/Lexus OEM supplier

Provide your research in this format:
VERIFIED MAKE: [corrected if needed]
VERIFIED MODEL: [specific models]
YEAR RANGE: [years]
MARKET PRICE RANGE: $[low] - $[high]
AVERAGE SOLD PRICE: $[average]
KEY SELLING POINTS: [list]
FITMENT NOTES: [any special compatibility info]"""

        try:
            # Prepare content
            content = [prompt]
            for img in images:
                content.append({"mime_type": "image/jpeg", "data": base64.b64encode(img).decode()})
            
            # Generate with Gemini 2.5 Pro
            response = self.model.generate_content(
                content,
                generation_config={
                    'temperature': 0.2,  # Slightly higher for research
                    'top_p': 0.9,
                    'max_output_tokens': 1024,
                }
            )
            
            response_text = response.text
            self.debug_output["step2_fitment_raw"] = response_text
            self.debug_output["gemini_responses"].append({
                "step": "market_research",
                "response": response_text
            })
            
            # Parse the response
            result = self._parse_research_response(response_text)
            self.debug_output["workflow_steps"].append(f"Step 2 complete: {result.get('verified_make', 'Unknown')} {result.get('verified_model', '')}")
            
            return result
            
        except Exception as e:
            print(f"Step 2 error: {str(e)}")
            self.debug_output["workflow_steps"].append(f"Step 2 error: {str(e)}")
            return {
                "verified_make": identification.get('brand', ''),
                "verified_model": "",
                "year_range": "",
                "price_low": 50,
                "price_high": 150,
                "average_price": 100,
                "selling_points": [],
                "fitment_notes": ""
            }

    async def _step3_final_report(self, identification: Dict, research: Dict) -> Dict:
        """
        Step 3: Generate final eBay listing with all information
        """
        self.debug_output["workflow_steps"].append("Step 3: Generating final report")
        
        # Build eBay title (max 80 chars)
        title_parts = []
        
        # Add make/model/year if available
        if research.get('verified_make'):
            title_parts.append(research['verified_make'])
        if research.get('verified_model'):
            title_parts.append(research['verified_model'])
        if research.get('year_range'):
            title_parts.append(research['year_range'])
        
        # Add part type
        title_parts.append(identification.get('part_type', 'Auto Part'))
        
        # Add brand if different from make
        if identification.get('brand') and identification['brand'] != research.get('verified_make'):
            title_parts.append(identification['brand'])
        
        # Add first part number if space allows
        if identification.get('part_numbers'):
            title_parts.append(identification['part_numbers'][0])
        
        ebay_title = " ".join(title_parts)[:80]
        
        # Build description
        description_parts = [
            f"**Item:** {identification.get('part_type', 'Auto Part')}",
            f"**Brand:** {identification.get('brand', 'OEM')}",
            f"**Part Numbers:** {', '.join(identification.get('part_numbers', []))}",
            f"**Condition:** {identification.get('condition', 'Used')}",
            "",
            "**Fitment:**",
            f"- Make: {research.get('verified_make', 'See part numbers')}",
            f"- Model: {research.get('verified_model', 'See part numbers')}",
            f"- Years: {research.get('year_range', 'See part numbers')}",
        ]
        
        if research.get('fitment_notes'):
            description_parts.append(f"- Notes: {research['fitment_notes']}")
        
        description_parts.extend([
            "",
            "**Features:**",
            identification.get('characteristics', 'See photos for details'),
            "",
            "**What's Included:**",
            "- Exactly what is shown in the photos",
            "- No additional hardware or accessories unless shown",
            "",
            "Please verify fitment with your vehicle before purchasing.",
            "Check all photos carefully for condition details."
        ])
        
        description = "\n".join(description_parts)
        
        # Determine category
        category = self._determine_category(identification.get('part_type', ''))
        
        # Build final result
        result = {
            "name": ebay_title,
            "ebay_title": ebay_title,
            "description": description,
            "category": category,
            "vehicles": f"{research.get('verified_make', '')} {research.get('verified_model', '')} {research.get('year_range', '')}".strip(),
            "price": research.get('average_price', 100),
            "price_range": {
                "low": research.get('price_low', 50),
                "high": research.get('price_high', 150)
            },
            "condition": identification.get('condition', 'Used'),
            "part_numbers": identification.get('part_numbers', []),
            "brand": identification.get('brand', ''),
            "make": research.get('verified_make', ''),
            "model": research.get('verified_model', ''),
            "year_range": research.get('year_range', ''),
            "key_features": research.get('selling_points', []),
            "fitment_notes": research.get('fitment_notes', ''),
            "confidence_score": 8 if research.get('verified_make') else 5
        }
        
        self.debug_output["step3_pricing_raw"] = json.dumps(result, indent=2)
        self.debug_output["workflow_steps"].append(f"Step 3 complete: Generated listing for {ebay_title}")
        
        return result

    def _parse_identification_response(self, response_text: str) -> Dict:
        """Parse Step 1 identification response"""
        result = {
            "part_type": "",
            "brand": "",
            "part_numbers": [],
            "characteristics": "",
            "fitment_info": "",
            "condition": "Used"
        }
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('PART TYPE:'):
                result['part_type'] = line.replace('PART TYPE:', '').strip()
            elif line.startswith('BRAND:'):
                result['brand'] = line.replace('BRAND:', '').strip()
            elif line.startswith('PART NUMBERS:'):
                numbers = line.replace('PART NUMBERS:', '').strip()
                # Extract all part numbers using regex
                import re
                part_numbers = re.findall(r'[A-Z0-9]+-[A-Z0-9]+|[A-Z0-9]{5,}', numbers)
                result['part_numbers'] = part_numbers
            elif line.startswith('CHARACTERISTICS:'):
                result['characteristics'] = line.replace('CHARACTERISTICS:', '').strip()
            elif line.startswith('FITMENT INFO:'):
                result['fitment_info'] = line.replace('FITMENT INFO:', '').strip()
            elif line.startswith('CONDITION:'):
                result['condition'] = line.replace('CONDITION:', '').strip()
        
        return result

    def _parse_research_response(self, response_text: str) -> Dict:
        """Parse Step 2 research response"""
        result = {
            "verified_make": "",
            "verified_model": "",
            "year_range": "",
            "price_low": 50,
            "price_high": 150,
            "average_price": 100,
            "selling_points": [],
            "fitment_notes": ""
        }
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('VERIFIED MAKE:'):
                result['verified_make'] = line.replace('VERIFIED MAKE:', '').strip()
            elif line.startswith('VERIFIED MODEL:'):
                result['verified_model'] = line.replace('VERIFIED MODEL:', '').strip()
            elif line.startswith('YEAR RANGE:'):
                result['year_range'] = line.replace('YEAR RANGE:', '').strip()
            elif line.startswith('MARKET PRICE RANGE:'):
                price_range = line.replace('MARKET PRICE RANGE:', '').strip()
                # Extract prices using regex
                import re
                prices = re.findall(r'\$(\d+)', price_range)
                if len(prices) >= 2:
                    result['price_low'] = int(prices[0])
                    result['price_high'] = int(prices[1])
            elif line.startswith('AVERAGE SOLD PRICE:'):
                avg_price = line.replace('AVERAGE SOLD PRICE:', '').strip()
                import re
                price_match = re.search(r'\$(\d+)', avg_price)
                if price_match:
                    result['average_price'] = int(price_match.group(1))
            elif line.startswith('KEY SELLING POINTS:'):
                points = line.replace('KEY SELLING POINTS:', '').strip()
                result['selling_points'] = [p.strip() for p in points.split(',') if p.strip()]
            elif line.startswith('FITMENT NOTES:'):
                result['fitment_notes'] = line.replace('FITMENT NOTES:', '').strip()
        
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
            "step1_ocr_raw": "DEMO MODE - Step 1: Identification\nPART TYPE: Headlight Assembly\nBRAND: OEM\nPART NUMBERS: 12345-67890\nCHARACTERISTICS: Clear lens, halogen bulb type\nFITMENT INFO: Passenger side\nCONDITION: Used - Good",
            "step2_fitment_raw": "DEMO MODE - Step 2: Market Research\nVERIFIED MAKE: Toyota\nVERIFIED MODEL: Camry\nYEAR RANGE: 2018-2021\nMARKET PRICE RANGE: $75 - $125\nAVERAGE SOLD PRICE: $95\nKEY SELLING POINTS: OEM quality, complete assembly\nFITMENT NOTES: Fits all trim levels",
            "step3_pricing_raw": "DEMO MODE - Step 3: Final pricing analysis complete",
            "gemini_responses": [
                {"step": "demo_identification", "response": "Demo identification response"},
                {"step": "demo_research", "response": "Demo research response"}
            ],
            "workflow_steps": [
                "Demo Mode Active - No API Key",
                "Step 1: Demo identification",
                "Step 2: Demo market research", 
                "Step 3: Demo final report"
            ],
            "processing_time": 0.5
        }
        
        return {
            "name": "Toyota Camry 2018-2021 Headlight Assembly OEM 12345-67890",
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
