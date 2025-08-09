"""
Gemini API Service
Handles interaction with Google's Gemini AI model
"""

import config
import google.generativeai as genai
from typing import Dict, Any
import json

class GeminiAPI:
    """Gemini API wrapper for part identification"""
    
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model_name = config.GEMINI_MODEL
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
    
    async def identify_part(
        self, 
        image_data: str, 
        vision_result: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """
        Identify a part using Gemini AI
        
        Args:
            image_data: Base64 encoded image
            vision_result: Results from Vision API
            prompt: The identification prompt
            
        Returns:
            Dictionary containing part identification results
        """
        if not self.enabled:
            # Demo mode response
            return {
                "part_name": "Demo Part - Brake Caliper",
                "part_number": "DEMO-12345",
                "description": "This is a demo response. Configure API keys for real results.",
                "category": "Brakes",
                "condition": "Used - Good",
                "compatibility": ["2010-2015 Toyota Camry", "2011-2016 Honda Accord"]
            }
        
        try:
            # Construct the full prompt to parse OCR text
            full_prompt = f"""
            Parse the OCR text extracted from an auto part label/sticker to extract part information.
            
            OCR Extracted Text:
            {vision_result.get('text', 'None')}
            
            Visual Labels (for context): {', '.join(vision_result.get('labels', []))}
            
            Extract and parse the following information from the OCR text:
            - Part numbers (look for patterns like numbers with dashes, alphanumeric codes)
            - Brand/manufacturer names
            - Part descriptions or names
            - Model numbers or compatibility info
            - Any condition indicators (new, used, remanufactured, etc.)
            
            Respond ONLY with a valid JSON object in this exact format:
            {{
                "part_name": "extracted part name or type",
                "part_number": "extracted part number or N/A if not found",
                "description": "description based on OCR text",
                "category": "category based on part type",
                "condition": "condition if mentioned or 'Unknown'",
                "compatibility": ["vehicle models if mentioned"],
                "brand": "manufacturer or brand if found",
                "raw_ocr_text": "the full OCR text for reference"
            }}
            
            Do not include any text before or after the JSON object.
            """
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Parse JSON response
            try:
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                
                # Try to find JSON object in the response
                if '{' in response_text and '}' in response_text:
                    json_start = response_text.index('{')
                    json_end = response_text.rindex('}') + 1
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Ensure all required fields are present with defaults
                    result.setdefault("part_name", "Unknown Part")
                    result.setdefault("part_number", "N/A")
                    result.setdefault("description", "")
                    result.setdefault("category", "Auto Parts")
                    result.setdefault("condition", "Unknown")
                    result.setdefault("compatibility", [])
                    result.setdefault("brand", "")
                    result.setdefault("raw_ocr_text", vision_result.get("text", ""))
                else:
                    raise ValueError("No JSON object found in response")
                    
            except Exception as parse_error:
                # Fallback if response isn't valid JSON
                print(f"Failed to parse Gemini response: {parse_error}")
                print(f"Raw response: {response.text[:500]}")
                
                result = {
                    "part_name": "Unknown Part",
                    "part_number": "N/A",
                    "description": "Unable to identify part from image",
                    "category": "Auto Parts",
                    "condition": "Used",
                    "compatibility": []
                }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "part_name": "Error identifying part",
                "part_number": "N/A",
                "description": f"Error: {str(e)}",
                "category": "Unknown",
                "condition": "Unknown",
                "compatibility": []
            }
