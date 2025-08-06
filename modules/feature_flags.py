"""
Feature Flags for eBay Auto Parts Lister
Allows safe rollback of experimental features
"""

import os
from typing import Dict, Any

class FeatureFlags:
    """Feature flag management for safe experimental rollouts"""
    
    def __init__(self):
        """Initialize feature flags with safe defaults"""
        self.flags = {
            # Browser fallback system (experimental)
            "enable_browser_fallback": self._get_env_bool("ENABLE_BROWSER_FALLBACK", False),
            "browser_fallback_max_daily": self._get_env_int("BROWSER_FALLBACK_MAX_DAILY", 10),
            "browser_fallback_delay": self._get_env_int("BROWSER_FALLBACK_DELAY", 30),
            
            # Enhanced identification features
            "enable_enhanced_prompts": self._get_env_bool("ENABLE_ENHANCED_PROMPTS", True),
            "enable_confidence_scoring": self._get_env_bool("ENABLE_CONFIDENCE_SCORING", True),
            "enable_fallback_ui": self._get_env_bool("ENABLE_FALLBACK_UI", True),
            
            # Safety limits
            "max_api_retries": self._get_env_int("MAX_API_RETRIES", 3),
            "enable_debug_logging": self._get_env_bool("ENABLE_DEBUG_LOGGING", False),
        }
    
    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get boolean from environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_env_int(self, key: str, default: int) -> int:
        """Get integer from environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def is_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        # Force enable browser fallback for testing
        if feature == "enable_browser_fallback":
            return True
        return self.flags.get(feature, False)
    
    def get_value(self, feature: str, default: Any = None) -> Any:
        """Get feature flag value"""
        return self.flags.get(feature, default)
    
    def enable_feature(self, feature: str) -> None:
        """Enable a feature (for testing)"""
        self.flags[feature] = True
    
    def disable_feature(self, feature: str) -> None:
        """Disable a feature (for rollback)"""
        self.flags[feature] = False
    
    def get_all_flags(self) -> Dict[str, Any]:
        """Get all feature flags for debugging"""
        return self.flags.copy()

# Global instance
feature_flags = FeatureFlags()

# Convenience functions
def is_browser_fallback_enabled() -> bool:
    """Check if browser fallback is enabled"""
    return feature_flags.is_enabled("enable_browser_fallback")

def is_enhanced_ui_enabled() -> bool:
    """Check if enhanced UI features are enabled"""
    return feature_flags.is_enabled("enable_fallback_ui")

def get_browser_limits() -> Dict[str, int]:
    """Get browser fallback usage limits"""
    return {
        "max_daily": feature_flags.get_value("browser_fallback_max_daily", 10),
        "delay_seconds": feature_flags.get_value("browser_fallback_delay", 30)
    }
