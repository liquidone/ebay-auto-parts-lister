"""
eBay Auto Parts Lister - Main Entry Point
Clean, modular implementation following best practices
"""

import uvicorn
from core.app import create_app
import config

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main_new:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL.lower()
    )
