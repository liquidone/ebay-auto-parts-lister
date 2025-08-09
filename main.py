"""
eBay Auto Parts Lister - Main Application
Automated system for processing auto part images and creating eBay listings
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from modules.image_processor_simple import ImageProcessor
from modules.part_identifier import PartIdentifier
from modules.feature_flags import feature_flags, is_enhanced_ui_enabled
from modules.database import Database
from modules.ebay_api import eBayAPI
from modules.ebay_pricing import eBayPricing
from modules.ebay_compliance import eBayComplianceHandler

app = FastAPI(title="eBay Auto Parts Lister", version="3.0.0")

# Initialize modules - Clean, consolidated architecture
image_processor = ImageProcessor()
part_identifier = PartIdentifier()  # Single, clean implementation
database = Database()
ebay_api = eBayAPI()
ebay_pricing = eBayPricing()
ebay_compliance = eBayComplianceHandler()

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application interface"""
    from fastapi.responses import HTMLResponse
    import time
    
    # Add cache-busting timestamp
    cache_buster = str(int(time.time()))
    
    html_content = r"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>eBay Auto Parts Lister</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="AI-powered auto parts identification and eBay listing creation tool">
        <link rel="stylesheet" href="/static/css/style.css?v="""+ cache_buster + """"">
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23007bff'%3E%3Cpath d='M19 7h-3V6a4 4 0 0 0-8 0v1H5a1 1 0 0 0-1 1v11a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V8a1 1 0 0 0-1-1zM10 6a2 2 0 0 1 4 0v1h-4V6zm8 13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V9h2v1a1 1 0 0 0 2 0V9h4v1a1 1 0 0 0 2 0V9h2v10z'/%3E%3C/svg%3E">
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                max-width: 1400px; margin: 0 auto; padding: 20px; 
                background: #f8f9fa; color: #333; line-height: 1.6;
            }
            .main-container {
                display: flex; gap: 20px; align-items: flex-start;
            }
            .left-panel {
                flex: 1; max-width: 800px;
            }
            .right-panel {
                flex: 1; max-width: 600px; position: sticky; top: 20px;
            }
            .debug-panel {
                background: #1e1e1e; color: #f8f8f2; padding: 15px; border-radius: 8px;
                font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4;
                max-height: 80vh; overflow-y: auto; border: 1px solid #444;
            }
            .debug-panel h3 {
                color: #50fa7b; margin: 0 0 10px 0; font-size: 14px;
            }
            .debug-section {
                margin-bottom: 15px; padding: 10px; background: #2d2d2d; border-radius: 4px;
                border-left: 3px solid #50fa7b;
            }
            .debug-key {
                color: #8be9fd; font-weight: bold;
            }
            .debug-value {
                color: #f1fa8c; margin-left: 10px;
            }
            h1 { 
                color: #007bff; text-align: center; margin-bottom: 30px; 
                font-size: 2.5em; font-weight: 300; 
                text-shadow: 0 2px 4px rgba(0,123,255,0.1);
            }
            .upload-area { 
                border: 3px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; 
                background: white; border-radius: 12px; transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .upload-area:hover { 
                border-color: #007bff; background: #f0f8ff; 
                transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,123,255,0.15);
            }
            .results { 
                margin-top: 20px; padding: 20px; background: white; border-radius: 12px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #007bff;
            }
            .image-preview { max-width: 300px; margin: 10px; border-radius: 8px; }
            button { 
                background: linear-gradient(135deg, #007bff, #0056b3); color: white; 
                padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; 
                font-weight: 500; transition: all 0.3s ease; margin: 5px;
                box-shadow: 0 2px 4px rgba(0,123,255,0.3);
            }
            button:hover { 
                background: linear-gradient(135deg, #0056b3, #004085); 
                transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0,123,255,0.4);
            }
            button:disabled { 
                background: #6c757d; cursor: not-allowed; transform: none; 
                box-shadow: none; opacity: 0.6;
            }
        </style>
    </head>
    <body>
        <h1>eBay Auto Parts Lister</h1>
        <div class="main-container">
            <div class="left-panel">
                <input type="file" id="fileInput" multiple accept="image/*" style="display: none;" onchange="handleFileSelection(this)">
                <div class="upload-area" id="uploadArea" style="cursor: pointer;">
                    <p><strong>🖱️ CLICK HERE TO SELECT IMAGES</strong></p>
                    <p style="font-size: 16px; color: #007bff; margin-top: 10px;">📁 Select up to 24 auto part images</p>
                    <p style="font-size: 12px; color: #666;">Click to browse or drag & drop images here</p>
                </div>
                <div id="fileCount" style="margin: 10px 0; font-weight: bold; color: #007bff;"></div>
                <button onclick="processImages()" id="processBtn" disabled style="opacity: 0.5;">Process Images</button>
                <button onclick="clearFiles()" id="clearBtn" style="margin-left: 10px; background: #dc3545; display: none;">Clear All</button>
                <button onclick="testEbayConnection()" id="testEbayBtn" style="margin-left: 10px; background: #28a745;">Test eBay Connection</button>
                <div id="results" class="results" style="display: none;"></div>
            </div>
            <div class="right-panel">
                <div class="debug-panel" id="debugPanel" style="display: none;">
                    <h3>🔍 Debug Output</h3>
                    <div id="debugContent">
                        <p style="color: #6272a4; font-style: italic;">Debug information will appear here after processing...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // External JavaScript files (app.js, debug.js, upload.js) handle all functionality
            console.log('eBay Auto Parts Lister - External JS modules loaded');
        </script>

        <!-- Load external JavaScript files for enhanced UI -->
        <script src="/static/js/app.js?v="""+ cache_buster + """"></script>
        <script src="/static/js/debug.js?v="""+ cache_buster + """"></script>
        <script src="/static/js/upload.js?v="""+ cache_buster + """"></script>
    </body>
    </html>
    """
    
    # Create response with cache-busting headers
    response = HTMLResponse(content=html_content)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

@app.post("/process-images")
async def process_images(files: list[UploadFile] = File(...)):
    """Process uploaded auto part images as a single part with multiple views"""
    if not files:
        return {"error": "No files uploaded"}
    
    print(f"Processing {len(files)} images as a single auto part")
    
    # Save all uploaded files
    uploaded_files = []
    processed_images = []
    
    for file in files:
        try:
            # Save uploaded file
            file_path = f"uploads/{file.filename}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append(file_path)
            print(f"Saved file: {file.filename}")
            
        except Exception as e:
            print(f"Error saving {file.filename}: {str(e)}")
            return {"error": f"Failed to save {file.filename}: {str(e)}"}
    
    # Analyze all images together to identify the single auto part
    try:
        # Use clean, consolidated part identification system
        print(f"🔍 Starting part identification with {len(uploaded_files)} images")
        part_info = part_identifier.identify_part_from_multiple_images(uploaded_files)
        print(f"✅ Part identification complete: {part_info.get('part_name', 'Unknown')}")
        
        # Get competitive pricing from eBay sold listings
        part_number = part_info.get("part_numbers", part_info.get("part_number", ""))
        part_name = part_info.get("part_name", "")
        condition = part_info.get("condition", "Used")
        
        print(f"Fetching eBay pricing for: {part_number} - {part_name}")
        pricing_data = await ebay_pricing.get_sold_listings_price(part_number, part_name, condition)
        
        # Update part_info with pricing data
        if pricing_data.get("success"):
            part_info["estimated_price"] = pricing_data.get("suggested_price", part_info.get("estimated_price", 0))
            part_info["market_price"] = pricing_data.get("average_price", 0)
            part_info["quick_sale_price"] = pricing_data.get("quick_sale_price", 0)
            part_info["price_analysis"] = pricing_data.get("market_analysis", "")
            part_info["pricing_strategy"] = pricing_data.get("pricing_strategy", "")
            print(f"eBay pricing updated: Suggested ${pricing_data.get('suggested_price')} (Market avg: ${pricing_data.get('average_price')})")
        else:
            part_info["market_price"] = pricing_data.get("average_price", 0)
            part_info["price_analysis"] = pricing_data.get("market_analysis", "Estimated pricing")
            print(f"Using estimated pricing: ${pricing_data.get('suggested_price')}")
        
        # Process each image with SEO optimization
        for i, file_path in enumerate(uploaded_files):
            try:
                # Determine if this is the main image (first image by default)
                is_main = (i == 0)
                
                # Use SEO optimization pipeline
                seo_filename, processed_filename, alt_text = await image_processor.seo_process_image(
                    file_path, part_info, i, is_main
                )
                
                processed_images.append({
                    "original": os.path.basename(file_path),
                    "processed": seo_filename,
                    "alt_text": alt_text,
                    "is_main": is_main,
                    "seo_optimized": True
                })
                
                print(f"SEO optimized image {i+1}/{len(uploaded_files)}: {seo_filename}")
                
            except Exception as e:
                print(f"Error in SEO processing {file_path}: {e}")
                # Fallback to basic processing
                try:
                    processed_filename = await image_processor.process_image(file_path)
                    processed_images.append({
                        "original": os.path.basename(file_path),
                        "processed": os.path.basename(processed_filename),
                        "alt_text": f"Auto part image {i + 1}",
                        "is_main": (i == 0),
                        "seo_optimized": False
                    })
                except:
                    processed_images.append({
                        "original": os.path.basename(file_path),
                        "processed": os.path.basename(file_path),
                        "alt_text": f"Auto part image {i + 1}",
                        "is_main": (i == 0),
                        "seo_optimized": False
                    })
        
        # Store in database with all images
        try:
            record_id = database.store_part_info_with_images(processed_images, part_info)
        except Exception as db_error:
            print(f"Database error: {db_error}")
            record_id = "demo_record"
        
        # Generate SEO-optimized title following user's format requirements
        def generate_seo_title(part_info):
            """Generate SEO title following user's exact specification: [Year Range] + Make + Model + Part Name + Part Number + Color + OEM (in that order)"""
            MAX_TITLE_LENGTH = 80
            
            # Build components in USER'S EXACT ORDER
            title_parts = []
            
            # 1. Year range (fitment data) - NOW ENABLED with enhanced Gemini prompt
            year_range = part_info.get("year_range")
            if year_range and year_range.lower() not in ["unknown", "n/a", "none", ""]:
                title_parts.append(year_range)
            
            # 2. Make
            make = part_info.get("make")
            if make and make.lower() != "unknown":
                title_parts.append(make)
            
            # 3. Model  
            model = part_info.get("model")
            if model and model.lower() != "unknown":
                title_parts.append(model)
            
            # 4. Part Name (always required)
            part_name = part_info.get("part_name", "Auto Part")
            # Clean up part name - remove brand if it's already in make
            if make and make.lower() in part_name.lower():
                # Remove brand from part name to avoid duplication
                part_name_clean = part_name
                for brand_word in make.split():
                    part_name_clean = part_name_clean.replace(brand_word, "").strip()
                if part_name_clean:
                    part_name = part_name_clean
            title_parts.append(part_name)
            
            # 5. Part Number (include ALL part numbers if available)
            part_numbers = part_info.get("part_numbers") or part_info.get("part_number")
            if part_numbers and part_numbers != "Unknown":
                if isinstance(part_numbers, list):
                    # Include multiple part numbers if they fit
                    for pn in part_numbers[:2]:  # Limit to first 2 to save space
                        if pn and pn.strip():
                            title_parts.append(pn.strip())
                elif isinstance(part_numbers, str) and part_numbers.strip():
                    # Handle comma-separated part numbers
                    pn_list = [pn.strip() for pn in part_numbers.split(',') if pn.strip()]
                    for pn in pn_list[:2]:  # Limit to first 2 to save space
                        title_parts.append(pn)
            
            # 6. Color (if applicable)
            color = part_info.get("color")
            if color and color.lower() not in ["unknown", "n/a", "none", "", "black"]:  # Skip common/default colors
                title_parts.append(color)
            
            # 7. OEM (if applicable) - ALWAYS AT THE END
            if part_info.get("is_oem", False):
                title_parts.append("OEM")
            
            # Join and apply 80-character limit with smart truncation
            current_title = " ".join(title_parts)
            
            if len(current_title) <= MAX_TITLE_LENGTH:
                return current_title
            
            # Smart truncation - remove elements from the end until it fits
            # Priority order: Keep Year, Make, Model, Part Name. Remove Color, then Part Numbers if needed
            while len(current_title) > MAX_TITLE_LENGTH and len(title_parts) > 4:
                # Remove the least important elements first (color, extra part numbers)
                if len(title_parts) > 6 and title_parts[-2] not in ["OEM"]:  # Remove color if present
                    title_parts.pop(-2)  # Remove color (keeping OEM at end)
                elif len(title_parts) > 5:  # Remove extra part numbers
                    # Find and remove part numbers (but keep at least one if possible)
                    part_num_count = 0
                    for i, part in enumerate(title_parts):
                        if any(char.isdigit() for char in part) and len(part) > 3:  # Likely a part number
                            part_num_count += 1
                    
                    if part_num_count > 1:
                        # Remove one part number
                        for i in range(len(title_parts) - 1, -1, -1):
                            if (any(char.isdigit() for char in title_parts[i]) and 
                                len(title_parts[i]) > 3 and 
                                title_parts[i] != "OEM"):
                                title_parts.pop(i)
                                break
                    else:
                        break
                else:
                    break
                
                current_title = " ".join(title_parts)
            
            # Final truncation if still too long
            if len(current_title) > MAX_TITLE_LENGTH:
                current_title = current_title[:MAX_TITLE_LENGTH].strip()
                # Avoid cutting in middle of word
                if current_title[-1] != ' ' and ' ' in current_title:
                    current_title = current_title.rsplit(' ', 1)[0]
            
            return current_title

        # Return single comprehensive result with proper key mapping
        result = {
            "part_name": part_info.get("part_name", "Unknown Part"),
            "ebay_title": part_info.get("ebay_title") or part_info.get("seo_title") or generate_seo_title(part_info),
            "seo_title": part_info.get("ebay_title") or part_info.get("seo_title") or generate_seo_title(part_info),
            "description": part_info.get("description", "Auto part in good condition"),
            "estimated_price": part_info.get("estimated_price", 0),
            "market_price": part_info.get("market_price", 0),
            "quick_sale_price": part_info.get("quick_sale_price", 0),
            "price_analysis": part_info.get("price_analysis", ""),
            "pricing_strategy": part_info.get("pricing_strategy", ""),
            "condition": part_info.get("condition", "Used"),
            "weight": part_info.get("weight", "Unknown"),
            "weight_lbs": part_info.get("weight_lbs", 0),
            "dimensions_inches": part_info.get("dimensions_inches", "Unknown"),
            "shipping_class": part_info.get("shipping_class", "Standard"),
            "color": part_info.get("color", "Unknown"),
            "category": part_info.get("category", "Auto Parts"),
            "vehicles": part_info.get("vehicles", "Unknown"),
            "part_numbers": part_info.get("part_numbers", part_info.get("part_number", "Unknown")),
            "features": part_info.get("features", ""),
            "compatibility": part_info.get("compatibility", ""),
            "is_oem": part_info.get("is_oem", False),
            "confidence_score": part_info.get("confidence_score", "Unknown"),
            "validation_notes": part_info.get("validation_notes", ""),
            "total_images": len(processed_images),
            "images": processed_images,
            "record_id": record_id,
            # Enhanced debug output for UI inspection
            "debug_output": part_info.get("debug_output", {
                "error": "No debug data was generated by the part identifier",
                "api_status": {
                    "demo_mode": part_identifier.demo_mode,
                    "api_client": "gemini",
                    "api_key_configured": bool(part_identifier.model),
                    "vision_api_configured": bool(part_identifier.vision_client),
                    "gemini_api_configured": bool(part_identifier.model)
                }
            }),
            "system_version": part_info.get("system_version", "v3.1-Debug-Output")
        }
        
        # Ensure debug panel has required fields
        if "debug_output" not in result or not result["debug_output"]:
            result["debug_output"] = {
                "api_status": {
                    "demo_mode": part_identifier.demo_mode,
                    "api_client": "gemini",
                    "api_key_configured": bool(part_identifier.model),
                    "vision_api_configured": bool(part_identifier.vision_client),
                    "gemini_api_configured": bool(part_identifier.model)
                },
                "step1_ocr_raw": {},
                "step2_fitment_raw": {},
                "step3_analysis_raw": {},
                "raw_gemini_responses": [],
                "workflow_steps": ["Processed through main.py endpoint"],
                "processing_time": 0,
                "extracted_part_numbers": []
            }
        
        # Ensure debug_output is a dictionary
        if not isinstance(result["debug_output"], dict):
            result["debug_output"] = {"raw_debug_output": str(result["debug_output"])}
        
        # Initialize api_status if not present
        if "api_status" not in result["debug_output"]:
            result["debug_output"]["api_status"] = {}
            
        # Update api_status with current values
        result["debug_output"]["api_status"].update({
            "demo_mode": part_identifier.demo_mode,
            "vision_api_configured": bool(part_identifier.vision_client),
            "gemini_api_configured": bool(part_identifier.model),
            "api_client": "gemini",
            "api_key_configured": bool(part_identifier.model)
        })
        
        # Add system information
        result["debug_output"]["system_info"] = {
            "system_version": "v3.1-Debug-Output",
            "processing_timestamp": datetime.now().isoformat(),
            "total_images_processed": len(processed_images)
        }
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error identifying part from multiple images: {str(e)}")
        print(f"Full traceback:\n{error_details}")
        return {"error": f"Failed to identify part: {str(e)}"}

@app.get("/test-ebay-connection")
async def test_ebay_connection():
    """Test eBay API connection and authentication"""
    try:
        result = ebay_api.test_connection()
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"eBay connection test failed: {str(e)}"
        }

@app.post("/create-ebay-listing")
async def create_ebay_listing(request: dict):
    """Create eBay draft listing from processed part information"""
    try:
        part_info = request.get('part_info', {})
        image_paths = request.get('image_paths', [])
        
        if not part_info:
            return {"error": "Part information is required"}
        
        # Upload images to eBay first
        print(f"Uploading {len(image_paths)} images to eBay...")
        upload_result = ebay_api.upload_images_to_ebay(image_paths)
        
        if not upload_result.get('success'):
            return {
                "error": f"Image upload failed: {upload_result.get('message')}"
            }
        
        image_urls = upload_result.get('image_urls', [])
        print(f"Images uploaded successfully: {len(image_urls)} URLs received")
        
        # Create draft listing
        print("Creating eBay draft listing...")
        listing_result = ebay_api.create_draft_listing(part_info, image_urls)
        
        if listing_result.get('success'):
            return {
                "success": True,
                "message": "eBay listing created successfully!",
                "item_id": listing_result.get('item_id'),
                "listing_url": listing_result.get('listing_url'),
                "demo_mode": listing_result.get('demo_mode', False),
                "images_uploaded": len(image_urls)
            }
        else:
            return {
                "error": f"Listing creation failed: {listing_result.get('message')}"
            }
            
    except Exception as e:
        return {
            "error": f"eBay listing creation error: {str(e)}"
        }

# Enhanced Part Identification Endpoints
# Multi-phase identification with browser fallback

@app.post("/enhanced-identify")
async def enhanced_identify_part(file: UploadFile = File(...), force_fallback: bool = False):
    """Enhanced part identification with multi-phase analysis"""
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Use clean, consolidated identification system
        result = await part_identifier.identify_part_from_multiple_images([file_path])
        
        return {
            "success": True,
            "result": result,
            "system_info": {
                "version": result.get("system_version", "v3.0-Consolidated-Clean"),
                "workflow": "3-step OCR→Research→Validation",
                "timestamp": result.get("workflow_timestamp", "")
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback_available": False
        }

@app.get("/feature-flags")
async def get_feature_flags():
    """Get current feature flag status for UI"""
    return {
        "flags": feature_flags.get_all_flags(),
        "browser_fallback_enabled": False,
        "enhanced_ui_enabled": is_enhanced_ui_enabled()
    }

@app.post("/toggle-feature")
async def toggle_feature(feature_name: str, enabled: bool):
    """Toggle feature flags (for rollback/testing)"""
    try:
        if enabled:
            feature_flags.enable_feature(feature_name)
        else:
            feature_flags.disable_feature(feature_name)
        
        return {
            "success": True,
            "feature": feature_name,
            "enabled": enabled,
            "message": f"Feature '{feature_name}' {'enabled' if enabled else 'disabled'}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _get_suggested_actions(result):
    """Get suggested actions based on identification result"""
    actions = []
    
    if result.confidence_score < 0.7:
        actions.append("Try enhanced analysis for better accuracy")
    
    if not result.part_number:
        actions.append("Manual part number entry recommended")
    
    if "unknown" in result.part_name.lower():
        actions.append("Consider using browser fallback for difficult parts")
    
    if not actions:
        actions.append("Result looks good - proceed with listing")
    
    return actions

# eBay Marketplace Account Deletion/Closure Notification Endpoints
# Required for eBay API compliance

@app.post("/ebay/account-deletion-notification")
async def ebay_account_deletion_notification(notification_data: dict):
    """Handle eBay marketplace account deletion/closure notifications"""
    try:
        result = await ebay_compliance.handle_account_deletion_notification(notification_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ebay/verification-challenge")
async def ebay_verification_challenge(challenge_data: dict):
    """Handle eBay verification challenges for the notification endpoint"""
    try:
        result = await ebay_compliance.handle_verification_challenge(challenge_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ebay/compliance-status")
async def ebay_compliance_status():
    """Get current eBay compliance status and information"""
    try:
        status = ebay_compliance.get_compliance_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
