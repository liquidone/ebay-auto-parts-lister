#!/usr/bin/env python3
"""
Render deployment startup script for eBay Auto Parts Lister
"""

import os
import uvicorn
from pathlib import Path

# Ensure required directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Get port from environment (Render provides this)
port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    # Import the app from main_full
    from main_full import app
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
