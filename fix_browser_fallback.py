"""
Fix Browser Fallback Logic - Force browser-only mode for testing
This script creates a temporary patch to force browser fallback testing
"""

import os
import shutil
from datetime import datetime

def create_browser_only_patch():
    """Create a patch that forces browser-only identification"""
    
    print("Creating browser-only mode patch...")
    
    # Backup original files
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to patch
    files_to_patch = [
        "main_full.py",
        "modules/enhanced_part_identifier.py"
    ]
    
    for file_path in files_to_patch:
        if os.path.exists(file_path):
            shutil.copy2(file_path, os.path.join(backup_dir, os.path.basename(file_path)))
            print(f"Backed up: {file_path}")
    
    # Create browser-only version of enhanced_part_identifier.py
    patch_enhanced_identifier()
    
    # Create browser-only version of main_full.py
    patch_main_application()
    
    print(f"Patch created! Backup stored in: {backup_dir}")
    print("\nTo apply patch:")
    print("1. Upload these files to your VPS")
    print("2. Restart the service")
    print("3. Test browser fallback")

def patch_enhanced_identifier():
    """Patch enhanced identifier to force browser fallback"""
    
    browser_only_code = '''"""
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
'''
    
    with open("modules/enhanced_part_identifier_browser_only.py", "w") as f:
        f.write(browser_only_code)
    
    print("Created: modules/enhanced_part_identifier_browser_only.py")

def patch_main_application():
    """Create a patched version of main application that uses browser-only mode"""
    
    # Read original main_full.py
    try:
        with open("main_full.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("main_full.py not found, skipping main app patch")
        return
    
    # Replace the import to use browser-only version
    patched_content = content.replace(
        "from modules.enhanced_part_identifier import enhanced_part_identifier",
        "from modules.enhanced_part_identifier_browser_only import enhanced_part_identifier"
    )
    
    # Also force enhanced mode to always be enabled
    patched_content = patched_content.replace(
        "if is_enhanced_ui_enabled():",
        "if True:  # FORCED BROWSER-ONLY MODE"
    )
    
    with open("main_full_browser_only.py", "w") as f:
        f.write(patched_content)
    
    print("Created: main_full_browser_only.py")

def create_deployment_script():
    """Create script to deploy browser-only mode to VPS"""
    
    deploy_script = '''#!/bin/bash
# Deploy browser-only mode for testing

echo "=== DEPLOYING BROWSER-ONLY MODE ==="

# Backup current files
cp main_full.py main_full.py.backup
cp modules/enhanced_part_identifier.py modules/enhanced_part_identifier.py.backup

# Deploy browser-only versions
cp main_full_browser_only.py main_full.py
cp modules/enhanced_part_identifier_browser_only.py modules/enhanced_part_identifier.py

# Restart service
systemctl restart ebay-auto-parts-lister

echo "=== BROWSER-ONLY MODE DEPLOYED ==="
echo "Service restarted. Browser fallback will now activate immediately."

# Show status
systemctl status ebay-auto-parts-lister
'''
    
    with open("deploy_browser_only.sh", "w") as f:
        f.write(deploy_script)
    
    print("Created: deploy_browser_only.sh")

def create_restore_script():
    """Create script to restore normal mode"""
    
    restore_script = '''#!/bin/bash
# Restore normal mode from browser-only testing

echo "=== RESTORING NORMAL MODE ==="

# Restore original files
cp main_full.py.backup main_full.py
cp modules/enhanced_part_identifier.py.backup modules/enhanced_part_identifier.py

# Restart service
systemctl restart ebay-auto-parts-lister

echo "=== NORMAL MODE RESTORED ==="
systemctl status ebay-auto-parts-lister
'''
    
    with open("restore_normal_mode.sh", "w") as f:
        f.write(restore_script)
    
    print("Created: restore_normal_mode.sh")

if __name__ == "__main__":
    print("Creating Browser-Only Mode Patch...")
    create_browser_only_patch()
    create_deployment_script()
    create_restore_script()
    
    print("\nNext Steps:")
    print("1. Upload these files to your VPS:")
    print("   - main_full_browser_only.py")
    print("   - modules/enhanced_part_identifier_browser_only.py")
    print("   - deploy_browser_only.sh")
    print("   - restore_normal_mode.sh")
    print("\n2. Run on VPS: bash deploy_browser_only.sh")
    print("3. Test browser fallback")
    print("4. When done: bash restore_normal_mode.sh")
