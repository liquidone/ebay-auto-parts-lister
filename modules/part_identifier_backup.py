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
            # Convert base64 images to PIL Images for Gemini
            images = []
            for i, encoded_image in enumerate(encoded_images):
                image_data = base64.b64decode(encoded_image)
                image = Image.open(io.BytesIO(image_data))
                
                # Debug: Print image info to verify quality
                print(f"Image {i+1}: {image.size[0]}x{image.size[1]} pixels, mode: {image.mode}")
                
                # Ensure image is in RGB mode for Gemini
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                images.append(image)
            
            # Create the prompt for automotive parts analysis
            prompt = f"""
            You are an expert eBay auto parts reseller. Your sole purpose is to help me identify and price auto parts for quick and profitable sales.

            When I upload these {len(images)} images of the SAME auto part, follow these steps precisely:

            1. Identify the Auto Part:
            Thoroughly analyze all images I provide.
            Identify the part, including its make, model, year range, part type, side (if applicable), part numbers, and any other unique characteristics you can see.

            Look specifically for:
            - Part numbers or codes stamped or printed on the part
            - Vehicle make/model compatibility markings
            - OEM manufacturer logos or stamps
            - Left/Right or Driver/Passenger side indicators
            - Design features that indicate specific vehicle fitment

            Respond in JSON format with these exact keys:
            {{
                "part_name": "specific part name with side if applicable",
                "category": "category from options: {', '.join(self.part_categories[:5])}",
                "condition": "condition assessment",
                "vehicles": "compatible makes/models with years",
                "part_numbers": "any visible part numbers or codes",
                "features": "key identifying features",
                "estimated_price": 0.00,
                "ebay_title": "YYYY-YYYY Make Model Part PartNumber Color OEM format",
                "description": "detailed eBay listing description",
                "compatibility": "specific fitment information",
                "color": "part color if relevant",
                "is_oem": true/false
            }}
            """
            
            # Use Gemini 2.0 Flash model (same as user's successful Gemini Gem)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Configure generation settings to match Gemini Gem
            generation_config = {
                "temperature": 0.1,  # Lower temperature for more consistent results
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            # Create content with prompt and images
            content = [prompt] + images
            
            # Generate response with config
            response = model.generate_content(content, generation_config=generation_config)
            
            print(f"Gemini Response: {response.text}")
            
            # Try to parse as JSON
            try:
                # Clean up the response to extract JSON
                response_text = response.text.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1]
                
                analysis = json.loads(response_text.strip())
                return analysis
                
            except json.JSONDecodeError:
                print(f"Failed to parse JSON, using fallback parser")
                return self._parse_fallback_response(response.text)
                
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

    def _parse_fallback_response(self, response_text: str) -> Dict:
        """Parse response when JSON parsing fails"""
        return {
            "name": "Parsed from AI Response",
            "description": response_text[:500] + "..." if len(response_text) > 500 else response_text,
            "category": "Unknown",
            "vehicles": "Unknown",
            "price": 0,
            "condition": "Used",
            "part_numbers": "Unknown",
            "features": "See description",
            "estimated_price": 0.00,
            "ebay_title": "Auto Part - See Description",
            "compatibility": "Unknown",
            "color": "Unknown",
            "is_oem": False
        }
