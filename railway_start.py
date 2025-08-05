#!/usr/bin/env python3
"""
Ultra-simple Railway deployment test
No dependencies, just pure Python + FastAPI
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "🎉 SUCCESS! Railway deployment working!",
        "status": "healthy",
        "deployment": "railway",
        "test": "passed"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/env")
def check_env():
    return {
        "gemini_key": "✅ Set" if os.getenv("GEMINI_API_KEY") else "❌ Missing",
        "openai_key": "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing",
        "port": os.getenv("PORT", "8000")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
