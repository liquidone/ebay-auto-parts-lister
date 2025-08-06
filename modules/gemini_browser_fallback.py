"""
Gemini Browser Fallback - Headless browser automation for enhanced accuracy
Uses Playwright to interact with Gemini's web interface when API fails
"""

import os
import asyncio
import logging
import tempfile
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .feature_flags import feature_flags

class GeminiBrowserFallback:
    """Browser-based Gemini interaction for enhanced part identification"""
    
    def __init__(self):
        """Initialize browser fallback system"""
        self.logger = logging.getLogger(__name__)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_authenticated = False
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed. Run: pip install playwright")
        
        # Configuration - Updated for 2025
        self.gemini_url = "https://aistudio.google.com/app/prompts/new"
        self.timeout = 30000  # 30 seconds
        self.max_retries = 3
        
        self.logger.info("Browser fallback initialized")
    
    async def identify_part(self, image_path: str) -> Dict[str, Any]:
        """
        Identify auto part using Gemini's web interface
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with part identification results
        """
        
        if not feature_flags.is_enabled("enable_browser_fallback"):
            raise Exception("Browser fallback is disabled")
        
        try:
            # Initialize browser if needed
            if not self.browser:
                await self._initialize_browser()
            
            # Upload image and get analysis
            result = await self._analyze_image_with_browser(image_path)
            
            self.logger.info("Browser fallback analysis completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Browser fallback failed: {e}")
            await self._cleanup_browser()
            raise
    
    async def _initialize_browser(self):
        """Initialize headless browser with stealth settings"""
        
        self.logger.info("Initializing headless browser...")
        
        playwright = await async_playwright().start()
        
        # Launch browser with stealth settings
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-default-apps',
                '--disable-extensions'
            ]
        )
        
        # Create new page with realistic user agent
        self.page = await self.browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Set realistic viewport
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Add stealth scripts
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        self.logger.info("Browser initialized successfully")
    
    async def _analyze_image_with_browser(self, image_path: str) -> Dict[str, Any]:
        """Analyze image using Gemini's web interface"""
        
        if not self.page:
            raise Exception("Browser not initialized")
        
        try:
            # Navigate to Gemini
            self.logger.info("Navigating to Gemini...")
            await self.page.goto(self.gemini_url, wait_until="networkidle", timeout=self.timeout)
            
            # Wait for page to load
            await self.page.wait_for_timeout(3000)
            
            # Handle authentication if needed
            if not self.is_authenticated:
                await self._handle_authentication()
            
            # Upload image
            await self._upload_image(image_path)
            
            # Send auto parts analysis prompt
            prompt = self._create_auto_parts_prompt()
            await self._send_prompt(prompt)
            
            # Wait for and extract response
            response = await self._extract_response()
            
            # Parse response into structured format
            return self._parse_gemini_response(response)
            
        except Exception as e:
            self.logger.error(f"Browser analysis failed: {e}")
            raise
    
    async def _handle_authentication(self):
        """Handle Google authentication if required"""
        
        try:
            # Check if we need to sign in
            sign_in_button = await self.page.query_selector('text="Sign in"')
            
            if sign_in_button:
                self.logger.warning("Authentication required - using guest mode")
                # For now, we'll try to use guest mode or skip auth
                # In production, you might want to handle OAuth properly
                
            # Check if we can proceed without full authentication
            await self.page.wait_for_timeout(2000)
            
            # Look for the main input area
            input_area = await self.page.query_selector('[data-testid="input-area"], .input-area, textarea')
            
            if input_area:
                self.is_authenticated = True
                self.logger.info("Successfully accessed Gemini interface")
            else:
                self.logger.warning("May need authentication - proceeding with caution")
                
        except Exception as e:
            self.logger.warning(f"Authentication handling failed: {e}")
            # Continue anyway - sometimes it works without explicit auth
    
    async def _upload_image(self, image_path: str):
        """Upload image to Gemini interface"""
        
        self.logger.info(f"Uploading image: {image_path}")
        
        try:
            # Look for file upload button/input
            file_inputs = [
                'input[type="file"]',
                '[data-testid="file-upload"]',
                '.file-upload',
                'input[accept*="image"]'
            ]
            
            file_input = None
            for selector in file_inputs:
                # Try current Gemini UI selectors (updated for 2025)
                upload_buttons = [
                    'input[type="file"]',  # Direct file input
                    '[data-testid="upload-button"]',  # Gemini's upload button
                    '[aria-label="Add image"]',  # New Gemini UI
                    '[aria-label="Upload image"]',  # Alternative label
                    'button[aria-label*="image"]',  # Any image button
                    'button[aria-label*="upload"]',  # Any upload button
                    '.upload-area',  # Upload drop zone
                    '[role="button"][title*="image"]',  # Image buttons
                    '[data-upload]',  # Data attribute
                    '.file-upload-button'  # Class name
                ]
                
                for selector in upload_buttons:
                    button = await self.page.query_selector(selector)
                    if button:
                        file_input = button
                        break
                        await button.click()
                        await self.page.wait_for_timeout(1000)
                        file_input = await self.page.query_selector('input[type="file"]')
                        if file_input:
                            break
            
            if file_input:
                # Upload the file
                await file_input.set_input_files(image_path)
                await self.page.wait_for_timeout(2000)
                self.logger.info("Image uploaded successfully")
            else:
                raise Exception("Could not find file upload mechanism")
                
        except Exception as e:
            self.logger.error(f"Image upload failed: {e}")
            raise
    
    async def _send_prompt(self, prompt: str):
        """Send analysis prompt to Gemini"""
        
        self.logger.info("Sending analysis prompt...")
        
        try:
            # Find text input area
            input_selectors = [
                'textarea',
                '[contenteditable="true"]',
                '[data-testid="input-area"]',
                '.input-area',
                'input[type="text"]'
            ]
            
            text_input = None
            for selector in input_selectors:
                text_input = await self.page.query_selector(selector)
                if text_input:
                    break
            
            if text_input:
                # Clear any existing text and type prompt
                await text_input.click()
                await text_input.fill(prompt)
                await self.page.wait_for_timeout(1000)
                
                # Submit the prompt
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_timeout(2000)
                
                self.logger.info("Prompt sent successfully")
            else:
                raise Exception("Could not find text input area")
                
        except Exception as e:
            self.logger.error(f"Failed to send prompt: {e}")
            raise
    
    async def _extract_response(self) -> str:
        """Extract response from Gemini interface"""
        
        self.logger.info("Extracting response...")
        
        try:
            # Wait for response to appear
            await self.page.wait_for_timeout(5000)
            
            # Look for response content
            response_selectors = [
                '[data-testid="response"]',
                '.response',
                '.message-content',
                '.ai-response',
                'div[role="main"] p',
                '.markdown-content'
            ]
            
            response_text = ""
            for selector in response_selectors:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    text = await element.inner_text()
                    if text and len(text) > 20:  # Reasonable response length
                        response_text += text + "\n"
            
            if not response_text:
                # Fallback: get all text from main content area
                main_content = await self.page.query_selector('main, [role="main"], .main-content')
                if main_content:
                    response_text = await main_content.inner_text()
            
            if response_text:
                self.logger.info("Response extracted successfully")
                return response_text.strip()
            else:
                raise Exception("No response content found")
                
        except Exception as e:
            self.logger.error(f"Failed to extract response: {e}")
            raise
    
    def _create_auto_parts_prompt(self) -> str:
        """Create specialized prompt for auto parts identification"""
        
        return """
        Please analyze this automotive part image with extreme precision and provide the following information:

        1. PART IDENTIFICATION:
        - Exact part name and type
        - Primary function and system it belongs to
        - Any visible part numbers, model numbers, or manufacturer codes

        2. TECHNICAL DETAILS:
        - Material composition (metal, plastic, rubber, etc.)
        - Approximate dimensions if discernible
        - Condition assessment (new, used, worn, damaged)
        - Any visible wear patterns or damage

        3. VEHICLE COMPATIBILITY:
        - Likely vehicle makes/models this fits
        - Year ranges if identifiable
        - Engine types or specifications if relevant

        4. MARKETPLACE INFORMATION:
        - Estimated market value range
        - Rarity or availability
        - Key selling points for listing

        Please be as specific as possible with part numbers and technical details. If you're uncertain about any aspect, please indicate your confidence level.
        """
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's response into structured format"""
        
        try:
            # Basic parsing - extract key information
            lines = response_text.split('\n')
            
            result = {
                "part_name": "Unknown Part",
                "part_number": None,
                "description": response_text,
                "condition": "Unknown",
                "material": "Unknown",
                "compatibility": "Unknown",
                "estimated_value": "Unknown",
                "confidence_notes": [],
                "raw_response": response_text
            }
            
            # Simple keyword extraction
            text_lower = response_text.lower()
            
            # Extract part name (look for common auto part terms)
            auto_parts = [
                "brake rotor", "brake pad", "brake disc", "brake caliper",
                "air filter", "oil filter", "fuel filter",
                "spark plug", "ignition coil", "alternator", "starter",
                "radiator", "thermostat", "water pump",
                "shock absorber", "strut", "spring",
                "tie rod", "ball joint", "control arm",
                "headlight", "taillight", "mirror",
                "bumper", "fender", "hood", "door"
            ]
            
            for part in auto_parts:
                if part in text_lower:
                    result["part_name"] = part.title()
                    break
            
            # Extract part numbers (look for alphanumeric codes)
            import re
            part_number_patterns = [
                r'\b[A-Z0-9]{6,}\b',  # 6+ character alphanumeric
                r'\b\d{4,}-[A-Z0-9]+\b',  # Number-letter pattern
                r'\bOEM[:\s]*([A-Z0-9-]+)\b'  # OEM number
            ]
            
            for pattern in part_number_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    result["part_number"] = matches[0]
                    break
            
            # Extract condition
            conditions = ["new", "used", "refurbished", "damaged", "worn"]
            for condition in conditions:
                if condition in text_lower:
                    result["condition"] = condition.title()
                    break
            
            self.logger.info("Response parsed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            return {
                "part_name": "Parse Error",
                "part_number": None,
                "description": response_text,
                "raw_response": response_text,
                "error": str(e)
            }
    
    async def _cleanup_browser(self):
        """Clean up browser resources"""
        
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            self.is_authenticated = False
            self.logger.info("Browser cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Browser cleanup failed: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_browser()

# Convenience function for one-off usage
async def analyze_part_with_browser(image_path: str) -> Dict[str, Any]:
    """
    Convenience function for one-off browser analysis
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dict with part identification results
    """
    
    async with GeminiBrowserFallback() as browser_fallback:
        return await browser_fallback.identify_part(image_path)
