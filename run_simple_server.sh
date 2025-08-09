#!/bin/bash
# Simple server runner - no nginx, no cache, no complexity
# Just pure FastAPI with anti-caching headers

echo "========================================="
echo "Starting SIMPLE server (no nginx, no cache)"
echo "========================================="

# Kill any existing uvicorn processes
pkill -f uvicorn || true

# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS="/opt/ebay-auto-parts-lister/vision-credentials.json"
export PYTHONUNBUFFERED=1

# Change to app directory
cd /opt/ebay-auto-parts-lister

# Run uvicorn directly with:
# - No workers (simpler)
# - Reload on changes
# - Verbose logging
# - Direct port 8000 access
/opt/ebay-auto-parts-lister/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level debug \
    --access-log \
    --no-use-colors

echo "Server stopped"
