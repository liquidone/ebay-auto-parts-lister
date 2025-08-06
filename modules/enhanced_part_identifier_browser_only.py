"""
Enhanced Part Identifier - BROWSER-ONLY MODE FOR TESTING
This version forces browser fallback for testing purposes
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .feature_flags import feature_flags, is_browser_fallback_enabled
from .gemini_browser_fallback import GeminiBrowserFallback

class IdentificationResult:
    """Result from part identification"""
    
    def __init__(self, part_name: str, part_number: Optional[str], description: str,
                 confidence_score: float, method_used: str, issues: list = None,
                 raw_response: Dict = None, timestamp: datetime = None):
        self.part_name = part_name
        self.part_number = part_number
        self.description = description
        self.confidence_score = confidence_score
        self.method_used = method_used
        self.issues = issues or []
        self.raw_response = raw_response or {}
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "part_name": self.part_name,
            "part_number": self.part_number,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "method_used": self.method_used,
            "issues": self.issues,
            "timestamp": self.timestamp.isoformat(),
            "raw_response": self.raw_response
        }
    
    def needs_fallback(self) -> bool:
        """Check if this result needs fallback processing"""
        return self.confidence_score < 0.7 or len(self.issues) > 0

class EnhancedPartIdentifier:
    """BROWSER-ONLY VERSION - Enhanced part identification with browser fallback"""
    
    def __init__(self):
        """Initialize browser-only identifier"""
        self.logger = logging.getLogger(__name__)
        self.browser_fallback = None
        
        # Initialize browser fallback
        try:
            self.browser_fallback = GeminiBrowserFallback()
            self.logger.info("Browser fallback initialized for TESTING MODE")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser fallback: {e}")
    
    async def identify_part(self, image_path: str, user_triggered_fallback: bool = False) -> IdentificationResult:
        """
        BROWSER-ONLY identification for testing
        Skips all other phases and goes directly to browser fallback
        """
        
        self.logger.info("=== BROWSER-ONLY MODE ACTIVATED ===")
        self.logger.info("Skipping API phases, going directly to browser fallback...")
        
        # Force browser fallback (Phase 4 only)
        if self.browser_fallback:
            try:
                self.logger.info("Starting browser fallback identification...")
                browser_result = await self._phase4_browser_fallback(image_path)
                self.logger.info(f"Browser fallback completed: {browser_result.method_used}")
                return browser_result
                
            except Exception as e:
                self.logger.error(f"Browser fallback failed: {e}")
                return self._create_error_result("Browser fallback failed", str(e))
        else:
            return self._create_error_result("Browser fallback not available", "Browser not initialized")
    
    async def _phase4_browser_fallback(self, image_path: str) -> IdentificationResult:
        """Phase 4: Browser-based Gemini fallback"""
        if not self.browser_fallback:
            raise Exception("Browser fallback not available")
        
        self.logger.info("Executing browser-based identification...")
        result = await self.browser_fallback.identify_part(image_path)
        
        # Simple confidence scoring for browser results
        confidence = 0.8  # Browser fallback gets high confidence
        issues = []
        
        return IdentificationResult(
            part_name=result.get("part_name", "Unknown Part"),
            part_number=result.get("part_number"),
            description=result.get("description", ""),
            confidence_score=confidence,
            method_used="Browser Gemini (TESTING MODE)",
            issues=issues,
            raw_response=result,
            timestamp=datetime.now()
        )
    
    def _create_error_result(self, error_type: str, error_message: str) -> IdentificationResult:
        """Create error result"""
        return IdentificationResult(
            part_name="Error",
            part_number=None,
            description=f"{error_type}: {error_message}",
            confidence_score=0.0,
            method_used="Error",
            issues=[error_type],
            raw_response={"error": error_message},
            timestamp=datetime.now()
        )

# Global instance for browser-only testing
enhanced_part_identifier = EnhancedPartIdentifier()
