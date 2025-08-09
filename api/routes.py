"""
API Routes
All endpoint definitions for the application
"""

from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List
import asyncio
import time
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import config
from core.image_handler import ImageHandler
from core.part_processor import PartProcessor
from services.ebay_api import test_ebay_connection

# Create router
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application page"""
    templates = request.app.state.templates
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cache_buster": str(int(time.time())),
        "enable_debug": config.ENABLE_DEBUG_PANEL,
        "demo_mode": config.ENABLE_DEMO_MODE,
        "debug_mode": config.DEBUG_MODE
    })

@router.post("/process-images")
async def process_images(files: List[UploadFile] = File(...)):
    """Process uploaded images and identify parts"""
    try:
        # Validate file count
        if len(files) > config.MAX_UPLOAD_FILES:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {config.MAX_UPLOAD_FILES} files allowed"
            )
        
        # Initialize handlers
        image_handler = ImageHandler()
        part_processor = PartProcessor()
        
        # Process each image
        results = []
        debug_output = []
        
        for file in files:
            # Validate and save image
            image_path = await image_handler.save_upload(file)
            
            # Process the image
            result = await part_processor.process_image(image_path)
            results.append(result)
            
            # Collect debug info if enabled
            if config.ENABLE_DEBUG_PANEL:
                debug_output.append(result.get("debug", {}))
        
        return JSONResponse({
            "success": True,
            "results": results,
            "debug_output": debug_output if config.ENABLE_DEBUG_PANEL else None,
            "total_processed": len(results)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.get("/test-ebay")
async def test_ebay():
    """Test eBay API connection"""
    try:
        if not config.ENABLE_EBAY_INTEGRATION:
            return JSONResponse({
                "success": False,
                "message": "eBay integration is not configured"
            })
        
        result = await test_ebay_connection()
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "demo_mode": config.ENABLE_DEMO_MODE
    }
