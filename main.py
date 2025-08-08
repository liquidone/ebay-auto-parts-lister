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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from modules.image_processor_simple import ImageProcessor
from modules.part_identifier import PartIdentifier
from modules.enhanced_part_identifier import EnhancedPartIdentifier
from modules.feature_flags import feature_flags, is_enhanced_ui_enabled
from modules.database import Database
from modules.ebay_api import eBayAPI
from modules.ebay_pricing import eBayPricing
from modules.ebay_compliance import eBayComplianceHandler

app = FastAPI(title="eBay Auto Parts Lister", version="1.0.0")

# Initialize modules
image_processor = ImageProcessor()
part_identifier = PartIdentifier()
enhanced_part_identifier = EnhancedPartIdentifier()
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
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>eBay Auto Parts Lister</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="AI-powered auto parts identification and eBay listing creation tool">
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23007bff'%3E%3Cpath d='M19 7h-3V6a4 4 0 0 0-8 0v1H5a1 1 0 0 0-1 1v11a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V8a1 1 0 0 0-1-1zM10 6a2 2 0 0 1 4 0v1h-4V6zm8 13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V9h2v1a1 1 0 0 0 2 0V9h4v1a1 1 0 0 0 2 0V9h2v10z'/%3E%3C/svg%3E">
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                max-width: 800px; margin: 0 auto; padding: 20px; 
                background: #f8f9fa; color: #333; line-height: 1.6;
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
        <div class="upload-area" onclick="document.getElementById('fileInput').click()" style="cursor: pointer;">
            <p><strong>🖱️ CLICK HERE TO SELECT IMAGES</strong></p>
            <p style="font-size: 16px; color: #007bff; margin-top: 10px;">📁 Select up to 24 auto part images</p>
            <p style="font-size: 12px; color: #666;">Click to browse or drag & drop images here</p>
            <input type="file" id="fileInput" multiple accept="image/*" style="display: none;" onchange="handleFileSelection(this)">
        </div>
        <div id="fileCount" style="margin: 10px 0; font-weight: bold; color: #007bff;"></div>
        <button onclick="processImages()" id="processBtn" disabled style="opacity: 0.5;">Process Images</button>
        <button onclick="clearFiles()" id="clearBtn" style="margin-left: 10px; background: #dc3545; display: none;">Clear All</button>
        <button onclick="testEbayConnection()" id="testEbayBtn" style="margin-left: 10px; background: #28a745;">Test eBay Connection</button>
        <div id="results" class="results" style="display: none;"></div>
        
        <script>
            let selectedFiles = [];
            
            // Initialize drag and drop functionality
            document.addEventListener('DOMContentLoaded', function() {
                const uploadArea = document.querySelector('.upload-area');
                
                // Drag and drop event handlers
                uploadArea.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    uploadArea.style.borderColor = '#007bff';
                    uploadArea.style.backgroundColor = '#f0f8ff';
                });
                
                uploadArea.addEventListener('dragleave', function(e) {
                    e.preventDefault();
                    uploadArea.style.borderColor = '#ccc';
                    uploadArea.style.backgroundColor = 'transparent';
                });
                
                uploadArea.addEventListener('drop', function(e) {
                    e.preventDefault();
                    uploadArea.style.borderColor = '#ccc';
                    uploadArea.style.backgroundColor = 'transparent';
                    
                    const files = Array.from(e.dataTransfer.files);
                    if (files.length > 0) {
                        handleDroppedFiles(files);
                    }
                });
            });
            
            function handleFileSelection(input) {
                selectedFiles = Array.from(input.files);
                
                if (selectedFiles.length > 0) {
                    showImagePreviews();
                    document.getElementById('processBtn').disabled = false;
                    document.getElementById('processBtn').style.opacity = '1';
                } else {
                    clearFiles();
                }
            }
            
            function handleDroppedFiles(files) {
                // Filter for image files only
                const imageFiles = files.filter(file => file.type.startsWith('image/'));
                
                if (imageFiles.length === 0) {
                    alert('Please drop image files only (JPG, PNG, GIF, etc.)');
                    return;
                }
                
                // Limit to 24 files maximum
                if (imageFiles.length > 24) {
                    alert('Maximum 24 images allowed. Only the first 24 images will be used.');
                    selectedFiles = imageFiles.slice(0, 24);
                } else {
                    selectedFiles = imageFiles;
                }
                
                showImagePreviews();
                document.getElementById('processBtn').disabled = false;
                document.getElementById('processBtn').style.opacity = '1';
            }
            
            function showImagePreviews() {
                const uploadArea = document.querySelector('.upload-area');
                
                uploadArea.innerHTML = `
                    <div style="background: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>✅ ${selectedFiles.length} image(s) selected!</strong>
                        <button onclick="clearFiles()" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; margin-left: 10px;">Clear</button>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
                `;
                
                selectedFiles.forEach((file, index) => {
                    const imageDiv = document.createElement('div');
                    imageDiv.style.cssText = 'border: 2px solid #007bff; border-radius: 8px; padding: 8px; text-align: center; background: #f8f9fa;';
                    
                    if (index === 0) {
                        imageDiv.innerHTML = '<div style="background: #007bff; color: white; font-size: 10px; padding: 3px; margin-bottom: 5px;">MAIN IMAGE</div>';
                    }
                    
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 4px;';
                    
                    const filename = document.createElement('div');
                    filename.textContent = file.name.length > 15 ? file.name.substring(0, 12) + '...' : file.name;
                    filename.style.cssText = 'font-size: 10px; color: #666; margin-top: 5px;';
                    
                    imageDiv.appendChild(img);
                    imageDiv.appendChild(filename);
                    uploadArea.querySelector('div:last-child').appendChild(imageDiv);
                });
                
                uploadArea.innerHTML += '</div>';
            }
            
            function displaySelectedFiles() {
                console.log('displaySelectedFiles called with', selectedFiles.length, 'files');
                const uploadArea = document.querySelector('.upload-area');
                
                if (!uploadArea) {
                    console.error('Upload area not found!');
                    return;
                }
                
                if (selectedFiles.length === 0) {
                    // Reset to original state - don't recreate the file input as it already exists
                    uploadArea.innerHTML = `
                        <p><strong>🖱️ CLICK HERE TO SELECT IMAGES</strong></p>
                        <p style="font-size: 16px; color: #007bff; margin-top: 10px;">📁 Select up to 24 auto part images</p>
                        <p style="font-size: 12px; color: #666;">Use Ctrl+Click or Shift+Click for multiple selection</p>
                    `;
                } else {
                    console.log('Creating display for', selectedFiles.length, 'files');
                    
                    // Clear the upload area and add file count
                    uploadArea.innerHTML = `
                        <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <strong>✅ ${selectedFiles.length} image(s) selected successfully!</strong>
                            <button onclick="clearFiles()" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; margin-left: 10px; cursor: pointer;">Clear All</button>
                        </div>
                    `;
                    
                    // Create a simple grid for images
                    const imageGrid = document.createElement('div');
                    imageGrid.style.display = 'flex';
                    imageGrid.style.flexWrap = 'wrap';
                    imageGrid.style.gap = '10px';
                    imageGrid.style.marginTop = '10px';
                    imageGrid.style.justifyContent = 'center';
                    
                    selectedFiles.forEach((file, index) => {
                        console.log('Processing file', index, ':', file.name);
                        
                        const imageBox = document.createElement('div');
                        imageBox.style.border = '2px solid #007bff';
                        imageBox.style.borderRadius = '8px';
                        imageBox.style.padding = '8px';
                        imageBox.style.textAlign = 'center';
                        imageBox.style.backgroundColor = '#f8f9fa';
                        imageBox.style.minWidth = '120px';
                        
                        // Add main badge for first image
                        if (index === 0) {
                            const badge = document.createElement('div');
                            badge.textContent = 'MAIN IMAGE';
                            badge.style.background = '#007bff';
                            badge.style.color = 'white';
                            badge.style.fontSize = '10px';
                            badge.style.padding = '3px 6px';
                            badge.style.borderRadius = '3px';
                            badge.style.marginBottom = '5px';
                            imageBox.appendChild(badge);
                        }
                        
                        // Create and add the image
                        const img = document.createElement('img');
                        img.src = URL.createObjectURL(file);
                        img.style.width = '100px';
                        img.style.height = '100px';
                        img.style.objectFit = 'cover';
                        img.style.borderRadius = '4px';
                        img.style.display = 'block';
                        img.style.margin = '0 auto';
                        
                        // Add filename
                        const filename = document.createElement('div');
                        filename.textContent = file.name.length > 20 ? file.name.substring(0, 17) + '...' : file.name;
                        filename.style.fontSize = '10px';
                        filename.style.color = '#666';
                        filename.style.marginTop = '5px';
                        filename.style.wordBreak = 'break-all';
                        
                        imageBox.appendChild(img);
                        imageBox.appendChild(filename);
                        imageGrid.appendChild(imageBox);
                        
                        console.log('Added image box for', file.name);
                    });
                    
                    uploadArea.appendChild(imageGrid);
                    console.log('Image grid appended to upload area');
                }
            }
            
            function updateUI() {
                const fileCount = document.getElementById('fileCount');
                const processBtn = document.getElementById('processBtn');
                const clearBtn = document.getElementById('clearBtn');
                
                if (selectedFiles.length > 0) {
                    fileCount.textContent = `${selectedFiles.length} image(s) selected (max 24)`;
                    processBtn.disabled = false;
                    processBtn.style.opacity = '1';
                    clearBtn.style.display = 'inline-block';
                } else {
                    fileCount.textContent = '';
                    processBtn.disabled = true;
                    processBtn.style.opacity = '0.5';
                    clearBtn.style.display = 'none';
                }
            }
            
            function clearFiles() {
                selectedFiles = [];
                document.getElementById('fileInput').value = '';
                displaySelectedFiles();
                updateUI();
                document.getElementById('results').style.display = 'none';
            }
            
            // Drag and drop functionality for manual reordering
            let draggedElement = null;
            
            function handleDragStart(e) {
                draggedElement = this;
                this.style.opacity = '0.5';
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.outerHTML);
            }
            
            function handleDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                e.dataTransfer.dropEffect = 'move';
                this.style.backgroundColor = '#e3f2fd';
                return false;
            }
            
            function handleDrop(e) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                
                if (draggedElement !== this) {
                    const draggedIndex = parseInt(draggedElement.dataset.index);
                    const targetIndex = parseInt(this.dataset.index);
                    
                    // Reorder the selectedFiles array
                    const draggedFile = selectedFiles[draggedIndex];
                    selectedFiles.splice(draggedIndex, 1);
                    selectedFiles.splice(targetIndex, 0, draggedFile);
                    
                    // Refresh the display
                    displaySelectedFiles();
                    updateUI();
                }
                
                this.style.backgroundColor = '';
                return false;
            }
            
            function handleDragEnd(e) {
                this.style.opacity = '1';
                
                // Reset all background colors
                document.querySelectorAll('.image-container').forEach(container => {
                    container.style.backgroundColor = container.dataset.index == 0 ? '#f0f8ff' : 'white';
                });
            }
            
            function setAsMainImage(index) {
                if (index === 0) return; // Already main image
                
                // Move selected image to first position
                const selectedFile = selectedFiles[index];
                selectedFiles.splice(index, 1);
                selectedFiles.unshift(selectedFile);
                
                // Refresh the display
                displaySelectedFiles();
                updateUI();
            }
            
            async function processImages() {
                if (selectedFiles.length === 0) {
                    alert('Please select images first');
                    return;
                }
                
                const formData = new FormData();
                selectedFiles.forEach(file => {
                    formData.append('files', file);
                });
                
                document.getElementById('results').style.display = 'block';
                document.getElementById('results').innerHTML = '<p>Processing images...</p>';
                
                try {
                    const response = await fetch('/process-images', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    displaySingleResult(result);
                } catch (error) {
                    document.getElementById('results').innerHTML = '<p>Error: ' + error.message + '</p>';
                }
            }
            
            function displaySingleResult(result) {
                const resultsDiv = document.getElementById('results');
                
                if (result.error) {
                    resultsDiv.innerHTML = `<h2>Error</h2><p style="color: red;">${result.error}</p>`;
                    return;
                }
                
                resultsDiv.innerHTML = '<h2>Auto Part Identification Results</h2>';
                
                const resultDiv = document.createElement('div');
                resultDiv.style.border = '2px solid #007bff';
                resultDiv.style.borderRadius = '10px';
                resultDiv.style.padding = '20px';
                resultDiv.style.marginTop = '20px';
                resultDiv.style.backgroundColor = '#f8f9fa';
                
                // Create image gallery
                let imageGallery = '';
                if (result.images && result.images.length > 0) {
                    imageGallery = '<div style="margin: 15px 0;"><h4>SEO-Optimized Images (' + result.total_images + ' total):</h4><div style="display: flex; flex-wrap: wrap; gap: 10px;">';
                    result.images.forEach((img, index) => {
                        const mainBadge = img.is_main ? '<span style="position: absolute; top: 5px; left: 5px; background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">MAIN</span>' : '';
                        const seoBadge = img.seo_optimized ? '<span style="position: absolute; top: 5px; right: 5px; background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">SEO</span>' : '';
                        // Prioritize SEO-optimized images from /static/processed/, fallback to original uploads
                        const imageSrc = img.seo_optimized && img.processed ? `/static/processed/${img.processed}` : `/uploads/${img.original}`;
                        const borderColor = img.is_main ? '#007bff' : (img.seo_optimized ? '#28a745' : '#ddd');
                        
                        imageGallery += `
                            <div style="position: relative; border: 2px solid ${borderColor}; border-radius: 5px; padding: 5px; background: #f8f9fa;">
                                ${mainBadge}
                                ${seoBadge}
                                <img src="${imageSrc}" alt="${img.alt_text || 'Auto part image'}" style="width: 120px; height: 120px; object-fit: cover; border-radius: 3px;" onerror="this.src='/uploads/${img.original}'">
                                <p style="font-size: 9px; margin: 3px 0; text-align: center; color: #666; font-weight: bold;">${img.processed}</p>
                                <p style="font-size: 8px; margin: 0; text-align: center; color: #888; font-style: italic;">${img.alt_text || 'Auto part image'}</p>
                            </div>
                        `;
                    });
                    imageGallery += '</div></div>';
                }
                
                resultDiv.innerHTML = `
                    <h3 style="color: #007bff; margin-bottom: 15px;">${result.part_name}</h3>
                    ${imageGallery}
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4 style="color: #495057; margin-bottom: 10px;">🚀 SEO Optimization Status</h4>
                        <div style="background: white; padding: 10px; border-radius: 3px; border-left: 4px solid #28a745;">
                            <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 10px;">
                                <span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">✓ SEO Filenames</span>
                                <span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">✓ eBay Dimensions</span>
                                <span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">✓ Background Enhanced</span>
                                <span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">✓ Watermarked</span>
                                <span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">✓ Alt Text Generated</span>
                            </div>
                            <p style="margin: 0; color: #666; font-size: 14px;">Images optimized for maximum eBay search visibility and conversion rates</p>
                        </div>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4 style="color: #495057; margin-bottom: 10px;">📋 eBay Listing Preview</h4>
                        <div style="background: white; padding: 10px; border-radius: 3px; border-left: 4px solid #007bff;">
                            <h5 style="color: #007bff; margin: 0 0 10px 0;">SEO-Optimized Title:</h5>
                            <p style="margin: 0 0 15px 0; font-weight: bold; color: #28a745;">${result.seo_title || result.part_name}</p>
                            
                            <h5 style="color: #007bff; margin: 0 0 10px 0;">Description:</h5>
                            <p style="margin: 0 0 15px 0;">${result.description}</p>
                            
                            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 15px;">
                                <div><strong>💰 Suggested Price:</strong> <span style="color: #28a745; font-weight: bold;">$${result.estimated_price}</span></div>
                                <div><strong>📊 Market Avg:</strong> $${result.market_price || 'N/A'}</div>
                                <div><strong>⚡ Quick Sale:</strong> $${result.quick_sale_price || 'N/A'}</div>
                            </div>
                            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 15px;">
                                <div><strong>⚖️ Weight:</strong> ${result.weight_lbs || result.weight || 'Estimating...'} lbs</div>
                                <div><strong>📏 Dimensions:</strong> ${result.dimensions_inches || 'Measuring...'}</div>
                                <div><strong>📦 Shipping:</strong> ${result.shipping_class || 'Standard'}</div>
                            </div>
                            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                                <div><strong>🔧 Condition:</strong> ${result.condition}</div>
                                <div><strong>🎨 Color:</strong> ${result.color}</div>
                                <div><strong>🏭 OEM:</strong> ${result.is_oem ? 'Yes' : 'No'}</div>
                            </div>
                            ${result.price_analysis ? `<div style="margin-top: 10px; padding: 8px; background: #f0f8ff; border-radius: 4px; font-size: 13px;"><strong>📈 Market Analysis:</strong> ${result.price_analysis}</div>` : ''}
                        </div>
                    </div>
                    <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 5px;">
                        <h4 style="margin-bottom: 10px; color: #1976d2;">🚀 eBay Integration</h4>
                        <div style="display: flex; gap: 10px; margin: 10px 0; flex-wrap: wrap;">
                            <button onclick="testeBayConnection()" style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;">
                                🔍 Test eBay Connection
                            </button>
                            <button onclick="createeBayListing()" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;">
                                🏢 Create eBay Listing
                            </button>
                        </div>
                        <div id="ebayStatus" style="margin-top: 10px; padding: 8px; border-radius: 4px; display: none;"></div>
                        <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Your auto part is identified and images are SEO-optimized. Ready for eBay listing creation!</p>
                    </div>
                    <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 5px;">
                        <h4>eBay Listing Preview</h4>
                        <p><strong>Title:</strong> ${result.part_name}</p>
                        <p><strong>Images:</strong> ${result.total_images} professional photos showing multiple angles</p>
                        <p><strong>Ready for eBay:</strong> ✅ Title optimized, images processed, pricing competitive</p>
                    </div>
                `;
                
                resultsDiv.appendChild(resultDiv);
            }
            
            // Test eBay Connection function for main button
            async function testEbayConnection() {
                const testBtn = document.getElementById('testEbayBtn');
                const originalText = testBtn.textContent;
                
                // Show loading state
                testBtn.textContent = 'Testing...';
                testBtn.disabled = true;
                testBtn.style.opacity = '0.7';
                
                try {
                    const response = await fetch('/test-ebay-connection');
                    const result = await response.json();
                    
                    // Show result in results area
                    const resultsDiv = document.getElementById('results');
                    resultsDiv.style.display = 'block';
                    
                    if (result.success) {
                        resultsDiv.innerHTML = `
                            <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin-top: 10px;">
                                <h4 style="color: #155724; margin-top: 0;">✅ eBay Connection Successful!</h4>
                                <p style="color: #155724; margin-bottom: 0;">${result.message || 'eBay API connection is working properly.'}</p>
                            </div>
                        `;
                    } else {
                        resultsDiv.innerHTML = `
                            <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin-top: 10px;">
                                <h4 style="color: #721c24; margin-top: 0;">❌ eBay Connection Failed</h4>
                                <p style="color: #721c24; margin-bottom: 0;">${result.message || 'Unable to connect to eBay API.'}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    // Show error in results area
                    const resultsDiv = document.getElementById('results');
                    resultsDiv.style.display = 'block';
                    resultsDiv.innerHTML = `
                        <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin-top: 10px;">
                            <h4 style="color: #721c24; margin-top: 0;">❌ Connection Error</h4>
                            <p style="color: #721c24; margin-bottom: 0;">Failed to test eBay connection: ${error.message}</p>
                        </div>
                    `;
                }
                
                // Restore button state
                testBtn.textContent = originalText;
                testBtn.disabled = false;
                testBtn.style.opacity = '1';
            }
            
            // Test eBay Connection function for results section button
            async function testeBayConnection() {
                const statusDiv = document.getElementById('ebayStatus');
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '<div style="color: #007bff;">🔄 Testing eBay connection...</div>';
                
                try {
                    const response = await fetch('/test-ebay-connection');
                    const result = await response.json();
                    
                    if (result.success) {
                        statusDiv.innerHTML = `
                            <div style="background: #d4edda; color: #155724; padding: 10px; border-radius: 4px;">
                                ✅ eBay Connection Successful! ${result.message || 'Ready to create listings.'}
                            </div>
                        `;
                    } else {
                        statusDiv.innerHTML = `
                            <div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px;">
                                ❌ eBay Connection Failed: ${result.message || 'Unable to connect to eBay API.'}
                            </div>
                        `;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `
                        <div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px;">
                            ❌ Connection Error: ${error.message}
                        </div>
                    `;
                }
            }
            
            // Create eBay Listing function
            async function createeBayListing() {
                const statusDiv = document.getElementById('ebayStatus');
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '<div style="color: #007bff;">🔄 Creating eBay listing...</div>';
                
                // This would be implemented to create actual eBay listings
                // For now, show a demo message
                setTimeout(() => {
                    statusDiv.innerHTML = `
                        <div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 4px;">
                            🚧 eBay listing creation is in demo mode. Configure eBay API keys to enable full functionality.
                        </div>
                    `;
                }, 1500);
            }
        </script>
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
        # Use enhanced identification system
        main_image_path = uploaded_files[0]
        
        # Check if enhanced identification is enabled
        if is_enhanced_ui_enabled():
            identification_result = await enhanced_part_identifier.identify_part(main_image_path)
            part_info = identification_result.to_dict()
            print(f"Enhanced identification result: {identification_result.method_used} - Confidence: {identification_result.confidence_score:.2f}")
        else:
            # Fallback to original method
            part_info = await part_identifier.identify_part_from_multiple_images(uploaded_files)
            print(f"Standard identification from {len(uploaded_files)} images: {part_info}")
        
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
            "seo_title": generate_seo_title(part_info),
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
            "record_id": record_id
        }
        
        return result
        
    except Exception as e:
        print(f"Error identifying part from multiple images: {str(e)}")
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
        
        # Use enhanced identification
        result = await enhanced_part_identifier.identify_part(file_path, user_triggered_fallback=force_fallback)
        
        return {
            "success": True,
            "result": result.to_dict(),
            "recommendations": {
                "needs_fallback": result.needs_fallback(),
                "confidence_level": "high" if result.confidence_score > 0.8 else "medium" if result.confidence_score > 0.5 else "low",
                "suggested_actions": _get_suggested_actions(result)
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
