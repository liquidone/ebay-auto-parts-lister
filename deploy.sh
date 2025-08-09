#!/bin/bash

# Auto-deploy script for eBay Auto Parts Lister
# This script is run by cron every 2 minutes to pull latest changes

cd /opt/ebay-auto-parts-lister

# Pull latest changes from GitHub
git pull origin main

# Check if there were any changes
if [ $? -eq 0 ]; then
    # Install/update dependencies if requirements.txt changed
    if git diff HEAD@{1} --name-only | grep -q "requirements.txt"; then
        echo "Requirements changed, updating dependencies..."
        /opt/ebay-auto-parts-lister/venv/bin/pip install -r requirements.txt
    fi
    
    # Always restart the service to load new code
    echo "Restarting service to load new code..."
    systemctl restart ebay-auto-parts-lister
    
    echo "Deploy completed at $(date)"
else
    echo "No changes to deploy at $(date)"
fi
