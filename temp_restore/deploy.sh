#!/bin/bash

# eBay Auto Parts Lister - VPS Deployment Script
# This script automates the deployment process and dependency installation

set -e  # Exit on any error

echo "🚀 Starting eBay Auto Parts Lister deployment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Are you in the project directory?"
    exit 1
fi

# Pull latest changes from Git
echo "📥 Pulling latest changes from Git..."
git pull origin main

# Update pip to latest version
echo "🔄 Updating pip..."
/opt/ebay-auto-parts-lister/venv/bin/pip install --upgrade pip

# Install/update all Python dependencies
echo "📦 Installing Python dependencies..."
/opt/ebay-auto-parts-lister/venv/bin/pip install -r requirements.txt

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
/opt/ebay-auto-parts-lister/venv/bin/playwright install chromium

# Install system dependencies if needed
echo "🔧 Checking system dependencies..."
if ! dpkg -l | grep -q python3-pil; then
    echo "Installing system PIL dependencies..."
    apt update && apt install -y python3-pil
fi

# Set proper permissions
echo "🔒 Setting permissions..."
chown -R ebayapp:ebayapp /opt/ebay-auto-parts-lister
chmod +x /opt/ebay-auto-parts-lister/deploy.sh

# Restart the service
echo "🔄 Restarting service..."
systemctl restart ebay-auto-parts-lister

# Check service status
echo "✅ Checking service status..."
systemctl status ebay-auto-parts-lister --no-pager -l

# Show recent logs
echo "📋 Recent logs:"
journalctl -u ebay-auto-parts-lister -n 10 --no-pager

echo "🎉 Deployment complete!"
echo "🌐 Application should be available at: http://143.198.55.193"
