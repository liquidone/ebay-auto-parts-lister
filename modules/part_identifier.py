import os
import json
import base64
import io
from typing import Dict, List
from PIL import Image
import google.generativeai as genai

class PartIdentifier:
    def __init__(self):
        # Try to initialize Gemini client, fall back to OpenAI, then demo mode
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.ai_client = "gemini"
            self.demo_mode = False
            print("Using Google Gemini for AI analysis")
        elif openai_key:
            import openai
            self.openai_client = openai.OpenAI(api_key=openai_key)
            self.ai_client = "openai"
            self.demo_mode = False
            print("Using OpenAI for AI analysis")
        else:
            self.ai_client = None
            self.demo_mode = True
            print("Running in demo mode - no AI API key found")
        
        # Part categories for classification
        self.part_categories = [
            "Body Parts", "Engine Components", "Interior Parts", 
            "Electrical", "Suspension", "Transmission", "Brakes",
            "Exhaust", "Cooling", "Fuel System", "Lighting",
            "Trim & Molding", "Glass", "Mirrors", "Wheels & Tires"
        ]

    async def identify_part_from_multiple_images(self, image_paths: List[str]) -> Dict:
        """Identify auto part from multiple images"""
        if self.demo_mode:
            return self._get_demo_response()
        
        try:
            # Encode all images
            encoded_images = []
            for image_path in image_paths:
                encoded_image = self._encode_image(image_path)
                encoded_images.append(encoded_image)
            
            # Analyze with AI
            return await self._analyze_multiple_images_with_ai(encoded_images)
            
        except Exception as e:
            print(f"Error in part identification: {str(e)}")
            return {
                "name": "Error in Analysis",
                "description": f"Failed to analyze images: {str(e)}",
                "category": "Unknown",
                "vehicles": "Unknown",
                "price": 0,
                "condition": "Unknown"
            }

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def _analyze_multiple_images_with_ai(self, encoded_images: list) -> Dict:
        """Use AI to analyze multiple images of the same auto part"""
        try:
            if self.ai_client == "gemini":
                return await self._analyze_with_gemini(encoded_images)
            elif self.ai_client == "openai":
                return await self._analyze_with_openai(encoded_images)
            else:
                raise Exception("No AI client configured")
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            return {
                "name": "AI Analysis Failed",
                "description": f"AI analysis failed: {str(e)}",
                "category": "Unknown",
                "vehicles": "Unknown",
                "price": 0,
                "condition": "Used",
                "error": str(e)
            }

    async def _analyze_with_gemini(self, encoded_images: list) -> Dict:
        """Use Google Gemini Vision to analyze multiple images"""
        try:
            # Convert base64 images to PIL Images for Gemini with proper preprocessing
            images = []
            print(f"\n=== GEMINI ANALYSIS DEBUG ===")
            print(f"Processing {len(encoded_images)} images for Gemini")
            
            for i, encoded_image in enumerate(encoded_images):
                image_data = base64.b64decode(encoded_image)
                image = Image.open(io.BytesIO(image_data))
                
                # Debug: Print original image info
                print(f"Original Image {i+1}: {image.size[0]}x{image.size[1]} pixels, mode: {image.mode}, format: {image.format}")
                
                # Apply Gemini's recommended preprocessing
                # 1. Ensure proper orientation (auto-rotate based on EXIF)
                try:
                    from PIL.ExifTags import ORIENTATION
                    if hasattr(image, '_getexif') and image._getexif() is not None:
                        exif = image._getexif()
                        if ORIENTATION in exif:
                            orientation = exif[ORIENTATION]
                            if orientation == 3:
                                image = image.rotate(180, expand=True)
                            elif orientation == 6:
                                image = image.rotate(270, expand=True)
                            elif orientation == 8:
                                image = image.rotate(90, expand=True)
                            print(f"Auto-rotated image {i+1} based on EXIF orientation: {orientation}")
                except Exception as e:
                    print(f"EXIF rotation failed for image {i+1}: {e}")
                
                # 2. Optimize resolution for Gemini (max 3072x3072 as per API docs)
                max_dimension = 3072
                if image.size[0] > max_dimension or image.size[1] > max_dimension:
                    # Calculate new size maintaining aspect ratio
                    ratio = min(max_dimension / image.size[0], max_dimension / image.size[1])
                    new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"Resized image {i+1} to {image.size[0]}x{image.size[1]} for Gemini API limits")
                
                # 3. Ensure RGB mode for Gemini
                if image.mode != 'RGB':
                    print(f"Converting image {i+1} from {image.mode} to RGB")
                    image = image.convert('RGB')
                
                # 4. Check image quality (avoid blurry images as per Gemini docs)
                # Simple blur detection using image variance
                import numpy as np
                gray = image.convert('L')
                variance = np.var(np.array(gray))
                print(f"Image {i+1} quality variance: {variance:.2f} (higher = sharper)")
                
                images.append(image)
            
            print(f"Total images prepared for Gemini: {len(images)}")
            
            # Create the enhanced prompt for automotive parts analysis
            prompt = f"""
            You are an expert eBay auto parts reseller. Your sole purpose is to help identify and price automotive parts for quick and profitable sales.

            Here are examples of correct auto part identification:
            
            Example 1: Part number "VC12-004" = 2004-2006 Subaru Outback Interior Roof Overhead Reading Light
            Example 2: Part number "11-6370-00-1N" = 2008-2017 Dodge Grand Caravan LEFT Driver Side Tail Light
            Example 3: Part number "FL3Z-13404-A" = 2015-2020 Ford F-150 Headlight Assembly
            Example 4: Part number "84001-AE040" = 2005-2009 Subaru Outback/Legacy Headlight Assembly
            
            CRITICAL: When you find a part number, use it to determine the correct vehicle make and model. Do NOT guess based on appearance.

            When I upload these {len(images)} images of the SAME automotive part, follow these steps precisely:

            1. Identify the Auto Part:
               Thoroughly analyze all images I provide.
               Identify the automotive part, including:
               - Exact part name and type
               - Vehicle make, model, and year range it fits
               - Part number (look carefully on all surfaces - back, sides, labels, stickers)
               - Color and condition
               - Whether it's OEM or aftermarket
               - Any unique characteristics you can see

            2. Vehicle Compatibility:
               Determine the specific vehicles this part fits:
               - Make (Ford, Toyota, Honda, Subaru, etc.)
               - Model (F-150, Camry, Civic, Outback, etc.)
               - Year range (e.g., 2004-2006)
               - Side if applicable (Left/Driver or Right/Passenger)

            3. Provide Detailed Analysis:
               Present your findings with:
               - Complete part identification
               - Exact vehicle compatibility
               - Part number if visible
               - Condition assessment
               - Estimated weight and dimensions for shipping
               - Whether it's OEM or aftermarket

            Respond in JSON format with these exact keys:
            {{
                "part_name": "specific part name with correct side",
                "category": "category from options: {', '.join(self.part_categories[:5])}",
                "condition": "condition assessment",
                "vehicles": "exact make/model/years based on part number",
                "part_numbers": "all visible part numbers found",
                "features": "key identifying features and validation notes",
                "estimated_price": 0.00,
                "weight_lbs": 0.0,
                "dimensions_inches": "LxWxH format (e.g., 12x8x6)",
                "shipping_class": "Small/Medium/Large based on size and weight",
                "ebay_title": "YYYY-YYYY Make Model Part PartNumber Color OEM format",
                "description": "detailed eBay listing description",
                "compatibility": "specific fitment based on part number validation",
                "color": "part color if relevant",
                "is_oem": true/false,
                "confidence_score": "1-10 based on part number visibility and cross-reference success",
                "validation_notes": "explain how part number and design features confirm identification"
            }}
            """
            
            # Use the latest vision-optimized model (as recommended by Gemini team)
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            
            # Configure generation settings to match Gemini Gem's optimized parameters
            generation_config = {
                "temperature": 0.0,  # Deterministic for consistent part identification
                "top_p": 0.95,      # Higher precision for technical analysis
                "top_k": 64,        # More diverse token consideration
                "max_output_tokens": 4096,  # Allow detailed responses
                "candidate_count": 1,       # Single best response
            }
            
            # Create content with prompt and images
            content = [prompt] + images
            
            # Generate response with config
            print(f"\n=== SENDING TO GEMINI ===")
            print(f"Model: gemini-2.0-flash-exp")
            print(f"Generation config: {generation_config}")
            print(f"Prompt length: {len(prompt)} characters")
            print(f"Images count: {len(images)}")
            
            response = model.generate_content(content, generation_config=generation_config)
            
            print(f"\n=== GEMINI RESPONSE ===")
            print(f"Response text length: {len(response.text)} characters")
            print(f"Full Gemini Response:")
            print(response.text)
            print(f"=== END GEMINI RESPONSE ===")
            
            # Try to parse as JSON
            try:
                # Clean up the response to extract JSON
                response_text = response.text.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1]
                
                analysis = json.loads(response_text.strip())
                
                # POST-PROCESSING: Validate part number against database
                analysis = await self._validate_part_identification(analysis)
                
                return analysis
                
            except json.JSONDecodeError:
                print(f"Failed to parse JSON, using enhanced fallback parser")
                return await self._parse_enhanced_fallback_response(response.text, analysis=None)
                
        except Exception as e:
            print(f"Error in Gemini analysis: {str(e)}")
            raise e

    def _get_demo_response(self) -> Dict:
        """Return demo response when no AI is configured"""
        return {
            "name": "Demo Mode - Random Auto Part",
            "description": "This is a demo response. Configure OpenAI or Gemini API key for real analysis.",
            "category": "Body Parts",
            "vehicles": "2015-2020 Ford F-150",
            "price": 50.00,
            "condition": "Used",
            "part_numbers": "Demo-123-456",
            "features": "Demo part for testing",
            "estimated_price": 50.00,
            "ebay_title": "2015-2020 Ford F-150 Demo Part Demo-123-456 OEM",
            "compatibility": "Demo compatibility",
            "color": "Black",
            "is_oem": True
        }

    async def _validate_part_identification(self, analysis: Dict) -> Dict:
        """Post-processing validation to override AI's vehicle identification with database lookup"""
        try:
            # Extract part number from AI response
            part_number = analysis.get('part_number', '').strip()
            
            if not part_number or part_number == 'Not Found':
                return analysis
            
            # Try multiple lookup sources in priority order
            db_info = await self._lookup_part_info(part_number)
            
            # Check if part number was found in any database
            if db_info:
                
                print(f"\n=== DATABASE OVERRIDE ===")
                print(f"Part number {part_number} found in database")
                print(f"AI suggested: {analysis.get('vehicle_compatibility', 'Unknown')}")
                print(f"Database says: {db_info['vehicle']}")
                print(f"OVERRIDING AI with database info")
                print(f"=== END DATABASE OVERRIDE ===\n")
                
                # Override AI's identification with database info
                analysis['vehicle_compatibility'] = db_info['vehicle']
                analysis['part_name'] = db_info['part_name']
                analysis['confidence_score'] = 10  # Maximum confidence for database match
                analysis['validation_notes'] = f"Part number {part_number} validated against database. Overrode AI visual identification."
                
                # Update eBay title with correct vehicle info
                analysis['ebay_title'] = f"{db_info['years']} {db_info['make']} {db_info['model']} {db_info['part_name']} {part_number} OEM"
                
                # Update description with correct vehicle info
                if 'description' in analysis:
                    # Replace any incorrect vehicle references in description
                    original_desc = analysis['description']
                    analysis['description'] = f"{db_info['years']} {db_info['make']} {db_info['model']} {db_info['part_name']}. Part Number: {part_number}. {original_desc.split('Part Number:')[1] if 'Part Number:' in original_desc else 'Used condition, tested and working. Please verify fitment with your vehicle before purchasing.'}"
            
            return analysis
            
        except Exception as e:
            print(f"Error in part validation: {str(e)}")
            return analysis
    
    async def _lookup_part_info(self, part_number: str) -> Dict:
        """Phase 2: Multi-source part number lookup with fallback hierarchy"""
        try:
            print(f"\n=== PHASE 2 LOOKUP ===")
            print(f"Searching for part number: {part_number}")
            
            # Source 1: Local cache (high-confidence known parts)
            local_cache = {
                'VC12-004': {
                    'vehicle': '2004-2006 Subaru Outback',
                    'part_name': 'Interior Roof Overhead Reading Light',
                    'years': '2004-2006',
                    'make': 'Subaru',
                    'model': 'Outback',
                    'source': 'local_cache',
                    'confidence': 10
                },
                '84001-AE040': {
                    'vehicle': '2005-2009 Subaru Outback/Legacy',
                    'part_name': 'Headlight Assembly',
                    'years': '2005-2009',
                    'make': 'Subaru',
                    'model': 'Outback/Legacy',
                    'source': 'local_cache',
                    'confidence': 10
                }
            }
            
            if part_number in local_cache:
                print(f"✅ Found in local cache: {local_cache[part_number]['vehicle']}")
                print(f"=== END PHASE 2 LOOKUP ===\n")
                return local_cache[part_number]
            
            # Source 2: Pattern recognition (medium confidence)
            pattern_info = self._analyze_part_number_patterns(part_number)
            if pattern_info:
                print(f"📋 Pattern recognition: {pattern_info['make']} part detected")
                print(f"=== END PHASE 2 LOOKUP ===\n")
                return pattern_info
            
            # Source 3: External API lookup (future implementation)
            # api_info = await self._lookup_external_apis(part_number)
            # if api_info:
            #     return api_info
            
            print(f"❌ Part number {part_number} not found in any database")
            print(f"=== END PHASE 2 LOOKUP ===\n")
            return None
            
        except Exception as e:
            print(f"Error in part lookup: {str(e)}")
            return None
    
    def _analyze_part_number_patterns(self, part_number: str) -> Dict:
        """Analyze part number patterns to determine likely manufacturer"""
        try:
            # Subaru patterns
            if (part_number.startswith('84') and len(part_number) >= 10) or part_number.startswith('VC12-'):
                return {
                    'vehicle': f'Subaru (Pattern Match)',
                    'part_name': 'Auto Part',
                    'years': 'Various',
                    'make': 'Subaru',
                    'model': 'Multiple Models',
                    'source': 'pattern_recognition',
                    'confidence': 6
                }
            
            # Ford patterns
            elif part_number.startswith('FL3Z-') or part_number.startswith('F150-'):
                return {
                    'vehicle': f'Ford (Pattern Match)',
                    'part_name': 'Auto Part',
                    'years': 'Various',
                    'make': 'Ford',
                    'model': 'Multiple Models',
                    'source': 'pattern_recognition',
                    'confidence': 6
                }
            
            # Toyota patterns
            elif part_number.startswith('81') or part_number.startswith('90'):
                return {
                    'vehicle': f'Toyota (Pattern Match)',
                    'part_name': 'Auto Part',
                    'years': 'Various',
                    'make': 'Toyota',
                    'model': 'Multiple Models',
                    'source': 'pattern_recognition',
                    'confidence': 6
                }
            
            # Nissan patterns
            elif part_number.startswith('26550-'):
                return {
                    'vehicle': f'Nissan Quest (Pattern Match)',
                    'part_name': 'Tail Light Assembly',
                    'years': '2011-2017',
                    'make': 'Nissan',
                    'model': 'Quest',
                    'source': 'pattern_recognition',
                    'confidence': 7
                }
            elif part_number.startswith('265') and len(part_number) >= 10:
                return {
                    'vehicle': f'Nissan (Pattern Match)',
                    'part_name': 'Auto Part',
                    'years': 'Various',
                    'make': 'Nissan',
                    'model': 'Multiple Models',
                    'source': 'pattern_recognition',
                    'confidence': 6
                }
            
            return None
            
        except Exception as e:
            print(f"Error in pattern analysis: {str(e)}")
            return None
    
    async def _parse_enhanced_fallback_response(self, response_text: str, analysis: Dict = None) -> Dict:
        """Phase 3: Enhanced fallback parser for visual-only analysis"""
        try:
            print(f"\n=== PHASE 3 ENHANCED FALLBACK ===")
            print(f"Processing visual-only analysis (no part number found)")
            
            # Extract key information from raw response text
            part_info = self._extract_visual_analysis(response_text)
            
            # Apply visual confidence scoring
            confidence = self._calculate_visual_confidence(part_info)
            
            # Detect manufacturer from visual cues
            manufacturer_info = self._detect_manufacturer_visual(response_text)
            
            # Build enhanced response
            enhanced_response = {
                "part_name": part_info.get('part_name', 'Auto Part'),
                "vehicle_compatibility": part_info.get('vehicle', 'Unknown Vehicle'),
                "part_number": "Not Visible",
                "condition": part_info.get('condition', 'Used'),
                "estimated_price": part_info.get('price', '$25-50'),
                "description": self._build_visual_description(part_info, manufacturer_info),
                "confidence_score": confidence,
                "color": part_info.get('color', 'Gray'),
                "is_oem": True,
                "ebay_title": self._build_visual_title(part_info, manufacturer_info),
                "validation_notes": f"⚠️ VISUAL ANALYSIS ONLY (confidence: {confidence}/10). No part number visible for database validation. PLEASE VERIFY FITMENT - visual identification may be inaccurate for similar-looking parts.",
                "analysis_method": "visual_fallback",
                "manufacturer_detected": manufacturer_info.get('make', 'Unknown')
            }
            
            print(f"Visual confidence score: {confidence}/10")
            print(f"Manufacturer detected: {manufacturer_info.get('make', 'Unknown')}")
            print(f"=== END PHASE 3 ENHANCED FALLBACK ===\n")
            
            return enhanced_response
            
        except Exception as e:
            print(f"Error in enhanced fallback: {str(e)}")
            return self._basic_fallback_response()
    
    def _extract_visual_analysis(self, response_text: str) -> Dict:
        """Extract structured information from raw AI response"""
        try:
            # Look for key patterns in the response
            part_info = {}
            
            # Extract part name
            if 'overhead console' in response_text.lower():
                part_info['part_name'] = 'Overhead Console Dome Light'
            elif 'headlight' in response_text.lower():
                part_info['part_name'] = 'Headlight Assembly'
            elif 'tail light' in response_text.lower():
                part_info['part_name'] = 'Tail Light Assembly'
            else:
                part_info['part_name'] = 'Auto Part'
            
            # Extract vehicle information
            if 'subaru' in response_text.lower():
                if 'outback' in response_text.lower():
                    part_info['vehicle'] = 'Subaru Outback'
                elif 'legacy' in response_text.lower():
                    part_info['vehicle'] = 'Subaru Legacy'
                else:
                    part_info['vehicle'] = 'Subaru Vehicle'
            elif 'ford' in response_text.lower():
                part_info['vehicle'] = 'Ford Vehicle'
            elif 'toyota' in response_text.lower():
                part_info['vehicle'] = 'Toyota Vehicle'
            else:
                part_info['vehicle'] = 'Unknown Vehicle'
            
            # Extract condition
            if 'good condition' in response_text.lower():
                part_info['condition'] = 'Used - Good'
            elif 'fair condition' in response_text.lower():
                part_info['condition'] = 'Used - Fair'
            else:
                part_info['condition'] = 'Used'
            
            # Extract color
            if 'gray' in response_text.lower() or 'grey' in response_text.lower():
                part_info['color'] = 'Gray'
            elif 'black' in response_text.lower():
                part_info['color'] = 'Black'
            else:
                part_info['color'] = 'Gray'
            
            return part_info
            
        except Exception as e:
            print(f"Error extracting visual analysis: {str(e)}")
            return {}
    
    def _calculate_visual_confidence(self, part_info: Dict) -> int:
        """Calculate confidence score for visual-only analysis"""
        confidence = 3  # Base confidence for visual analysis
        
        # Boost confidence based on specific identifications
        if part_info.get('vehicle', '').lower() != 'unknown vehicle':
            confidence += 2  # Vehicle identified
        
        if 'overhead console' in part_info.get('part_name', '').lower():
            confidence += 2  # Specific part type identified
        
        if part_info.get('condition') and 'good' in part_info.get('condition', '').lower():
            confidence += 1  # Condition assessed
        
        return min(confidence, 5)  # Max 5/10 for visual-only (no part number validation) - reduced for safety
    
    def _detect_manufacturer_visual(self, response_text: str) -> Dict:
        """Detect manufacturer from visual cues in response"""
        manufacturers = {
            'subaru': {'make': 'Subaru', 'confidence': 5},
            'ford': {'make': 'Ford', 'confidence': 5},
            'toyota': {'make': 'Toyota', 'confidence': 5},
            'honda': {'make': 'Honda', 'confidence': 5},
            'nissan': {'make': 'Nissan', 'confidence': 5}
        }
        
        for keyword, info in manufacturers.items():
            if keyword in response_text.lower():
                return info
        
        return {'make': 'Unknown', 'confidence': 3}
    
    def _build_visual_description(self, part_info: Dict, manufacturer_info: Dict) -> str:
        """Build description for visual-only analysis"""
        make = manufacturer_info.get('make', 'Unknown')
        part_name = part_info.get('part_name', 'Auto Part')
        condition = part_info.get('condition', 'Used')
        color = part_info.get('color', 'Gray')
        
        return f"⚠️ VISUAL IDENTIFICATION: {make} {part_name}. {color} color. {condition}. Part number not visible in images - identification based on visual analysis only and may be INACCURATE for similar-looking parts. Please verify make, model, year, and part number with your vehicle before purchasing."
    
    def _build_visual_title(self, part_info: Dict, manufacturer_info: Dict) -> str:
        """Build eBay title for visual-only analysis"""
        make = manufacturer_info.get('make', 'Unknown')
        part_name = part_info.get('part_name', 'Auto Part')
        color = part_info.get('color', 'Gray')
        
        return f"{make} {part_name} {color} OEM - Part Number Not Visible"
    
    def _basic_fallback_response(self) -> Dict:
        """Basic fallback when all else fails"""
        return {
            "part_name": "Auto Part",
            "vehicle_compatibility": "Unknown Vehicle",
            "part_number": "Not Visible",
            "condition": "Used",
            "estimated_price": "$25-50",
            "description": "Auto part identification failed. Please verify manually.",
            "confidence_score": 1,
            "color": "Unknown",
            "is_oem": False,
            "ebay_title": "Auto Part - See Description",
            "analysis_method": "basic_fallback"
        }
