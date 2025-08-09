"""
FastAPI Application Setup
Handles app initialization, middleware, and route registration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import config
from api.routes import router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Initialize FastAPI app
    app = FastAPI(
        title=config.APP_NAME,
        version=config.APP_VERSION,
        description="AI-powered auto parts identification and eBay listing creation"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
    
    # Initialize templates and attach to app state
    app.state.templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))
    
    # Include API routes
    app.include_router(router)
    
    return app
