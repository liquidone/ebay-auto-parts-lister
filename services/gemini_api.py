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
            # Construct the full prompt with vision results
            full_prompt = f"""
            {prompt}
            
            Vision API Results:
            Labels: {', '.join(vision_result.get('labels', []))}
            Detected Text: {vision_result.get('text', 'None')}
            
            Please identify this auto part and provide:
            1. Part name
            2. Part number (if visible)
            3. Description
            4. Category
            5. Condition
            6. Compatible vehicles
            
            Return the response as a JSON object.
            """
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response.text)
            except:
                # Fallback if response isn't valid JSON
                result = {
                    "part_name": "Unknown Part",
                    "part_number": "N/A",
                    "description": response.text[:200],
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
