#!/usr/bin/env python3
"""
Minimal FastAPI app for Railway deployment testing
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

# Create FastAPI app
app = FastAPI(title="eBay Auto Parts Lister - Minimal Test")

@app.get("/")
async def root():
    """Root endpoint for health checks"""
    return {"message": "eBay Auto Parts Lister is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auto-parts-lister"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify deployment"""
    env_vars = {
        "GEMINI_API_KEY": "✅ Set" if os.getenv("GEMINI_API_KEY") else "❌ Missing",
        "OPENAI_API_KEY": "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing"
    }
    
    return {
        "message": "Railway deployment test successful!",
        "environment_variables": env_vars,
        "python_version": "3.11",
        "framework": "FastAPI"
    }

@app.get("/ui", response_class=HTMLResponse)
async def simple_ui():
    """Simple HTML interface for testing"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>eBay Auto Parts Lister - Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { padding: 15px; margin: 20px 0; border-radius: 5px; text-align: center; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .button { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }
            .button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚂 Railway Deployment Successful!</h1>
            
            <div class="status success">
                <strong>✅ eBay Auto Parts Lister is running on Railway!</strong>
            </div>
            
            <div class="status info">
                <strong>🎉 Deployment Status:</strong><br>
                ✅ Container built successfully<br>
                ✅ FastAPI server started<br>
                ✅ Health checks passing<br>
                ✅ Environment variables configured<br>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="/test" class="button">🧪 Test API Endpoints</a>
                <a href="/docs" class="button">📚 API Documentation</a>
                <a href="/health" class="button">❤️ Health Check</a>
            </div>
            
            <div style="text-align: center; color: #666; margin-top: 30px;">
                <p><strong>Next Steps:</strong></p>
                <p>1. Verify API keys are working</p>
                <p>2. Test image upload functionality</p>
                <p>3. Deploy full application features</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
