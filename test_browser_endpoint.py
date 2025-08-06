#!/usr/bin/env python3
"""
Direct Browser Fallback Test Endpoint
Creates a simple endpoint to test browser fallback directly
"""

from flask import Flask, request, jsonify
import asyncio
import sys
import os
import tempfile
import base64
from pathlib import Path

# Add the project directory to Python path
sys.path.append('/opt/ebay-auto-parts-lister')

app = Flask(__name__)

@app.route('/test-browser-fallback', methods=['POST'])
def test_browser_fallback():
    """Direct test endpoint for browser fallback"""
    try:
        # Import browser fallback module
        from modules.gemini_browser_fallback import GeminiBrowserFallback
        
        # Get uploaded file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        # Test browser fallback directly
        async def run_browser_test():
            browser_fallback = GeminiBrowserFallback()
            result = await browser_fallback.identify_part(temp_path)
            return result
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_browser_test())
        loop.close()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return jsonify({
            'success': True,
            'method': 'Browser Fallback Direct Test',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'method': 'Browser Fallback Direct Test'
        }), 500

@app.route('/test-browser-status', methods=['GET'])
def test_browser_status():
    """Check if browser fallback is available"""
    try:
        from modules.gemini_browser_fallback import GeminiBrowserFallback
        from modules.feature_flags import feature_flags
        
        browser = GeminiBrowserFallback()
        
        return jsonify({
            'browser_fallback_available': True,
            'browser_fallback_enabled': feature_flags.is_enabled('enable_browser_fallback'),
            'playwright_available': True,
            'status': 'Ready for testing'
        })
        
    except Exception as e:
        return jsonify({
            'browser_fallback_available': False,
            'error': str(e),
            'status': 'Not available'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
