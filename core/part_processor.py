"""
Part Processor Module
Orchestrates the part identification process
"""

from pathlib import Path
from typing import Dict, Any
import base64
from services.vision_api import VisionAPI
from services.gemini_api import GeminiAPI
from utils.file_io import read_prompt

class PartProcessor:
    """Handles the complete part identification workflow"""
    
    def __init__(self):
        self.vision_api = VisionAPI()
        self.gemini_api = GeminiAPI()
        self.prompt = read_prompt("part_identifier.txt")
    
    async def process_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Process a single image to identify the part
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing part information and debug data
        """
        try:
            # Read image data
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Use Vision API for initial analysis
            vision_result = await self.vision_api.analyze_image(image_data)
            
            # Use Gemini for detailed part identification
            gemini_result = await self.gemini_api.identify_part(
                image_data,
                vision_result,
                self.prompt
            )
            
            # Compile results
            result = {
                "filename": image_path.name,
                "part_name": gemini_result.get("part_name", "Unknown Part"),
                "part_number": gemini_result.get("part_number", "N/A"),
                "description": gemini_result.get("description", ""),
                "category": gemini_result.get("category", "Auto Parts"),
                "condition": gemini_result.get("condition", "Unknown"),
                "compatibility": gemini_result.get("compatibility", []),
                "brand": gemini_result.get("brand", ""),
                "raw_ocr_text": gemini_result.get("raw_ocr_text", vision_result.get("text", "")),
                "debug": {
                    "vision_labels": vision_result.get("labels", []),
                    "vision_text": vision_result.get("text", ""),
                    "gemini_prompt": self.prompt[:200] + "...",
                    "gemini_response": str(gemini_result)[:500] + "..."
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "filename": image_path.name,
                "error": str(e),
                "debug": {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            }
