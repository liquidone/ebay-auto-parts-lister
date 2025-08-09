"""
Google Vision API Service
Handles interaction with Google Cloud Vision API
"""

import config
import base64
import json
from typing import Dict, Any

class VisionAPI:
    """Google Vision API wrapper"""
    
    def __init__(self):
        self.api_key = config.GOOGLE_API_KEY
        self.enabled = bool(self.api_key)
        self.vision_api_url = "https://vision.googleapis.com/v1/images:annotate"
    
    async def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """
        Analyze an image using Google Vision API with focus on TEXT_DETECTION
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dictionary containing OCR text extraction results
        """
        if not self.enabled:
            return {
                "labels": ["Demo mode - no API key"],
                "text": "Demo mode - OCR text detection disabled",
                "full_text_annotation": None,
                "text_annotations": []
            }
        
        try:
            import aiohttp
            import asyncio
            
            # Prepare the request for TEXT_DETECTION and LABEL_DETECTION
            request_body = {
                "requests": [{
                    "image": {
                        "content": image_data
                    },
                    "features": [
                        {"type": "TEXT_DETECTION", "maxResults": 50},
                        {"type": "LABEL_DETECTION", "maxResults": 10}
                    ]
                }]
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.vision_api_url}?key={self.api_key}",
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    result = await response.json()
            
            # Extract text and labels from response
            if "responses" in result and len(result["responses"]) > 0:
                response_data = result["responses"][0]
                
                # Extract all detected text
                full_text = ""
                text_annotations = []
                if "textAnnotations" in response_data:
                    text_annotations = response_data["textAnnotations"]
                    if len(text_annotations) > 0:
                        # First annotation contains the full text
                        full_text = text_annotations[0].get("description", "")
                
                # Extract labels
                labels = []
                if "labelAnnotations" in response_data:
                    labels = [label.get("description", "") for label in response_data["labelAnnotations"]]
                
                return {
                    "text": full_text,  # Full OCR text from the image
                    "text_annotations": text_annotations[1:] if len(text_annotations) > 1 else [],  # Individual text blocks
                    "labels": labels,
                    "full_response": response_data  # Keep full response for debugging
                }
            else:
                return {
                    "text": "",
                    "text_annotations": [],
                    "labels": [],
                    "error": "No response from Vision API"
                }
                
        except Exception as e:
            print(f"Vision API error: {str(e)}")
            return {
                "error": str(e),
                "text": "",
                "text_annotations": [],
                "labels": []
            }
