"""
Configuration file for eBay Auto Parts Lister
Contains all configuration variables and settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
PROMPTS_DIR = BASE_DIR / "prompts"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EBAY_APP_ID = os.getenv("EBAY_APP_ID", "")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID", "")
EBAY_DEV_ID = os.getenv("EBAY_DEV_ID", "")
EBAY_USER_TOKEN = os.getenv("EBAY_USER_TOKEN", "")

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"
VISION_MODEL = "gemini-1.5-flash"

# Application Settings
APP_NAME = "eBay Auto Parts Lister"
APP_VERSION = "4.0.0"
MAX_UPLOAD_FILES = 24
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

# Server Settings
HOST = "0.0.0.0"
PORT = 8000
RELOAD = False  # Set to True for development

# Feature Flags
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
ENABLE_DEBUG_PANEL = True
ENABLE_DEMO_MODE = not bool(GOOGLE_API_KEY and GEMINI_API_KEY)
ENABLE_EBAY_INTEGRATION = bool(EBAY_APP_ID and EBAY_USER_TOKEN)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "app.log"
