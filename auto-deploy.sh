#!/bin/bash

# Auto-deployment script for eBay Auto Parts Lister
# This script automatically pulls changes from Git and restarts the service

LOG_FILE="/var/log/auto-deploy.log"
APP_DIR="/opt/ebay-auto-parts-lister"
SERVICE_NAME="ebay-auto-parts-lister"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to deploy changes
deploy_changes() {
    log_message "Starting auto-deployment..."
    
    cd "$APP_DIR" || {
        log_message "ERROR: Cannot change to app directory"
        exit 1
    }
    
    # Get current commit hash
    OLD_COMMIT=$(git rev-parse HEAD)
    
    # Pull latest changes
    log_message "Pulling latest changes from Git..."
    if git pull origin main; then
        NEW_COMMIT=$(git rev-parse HEAD)
        
        if [ "$OLD_COMMIT" != "$NEW_COMMIT" ]; then
            log_message "New changes detected. Old: $OLD_COMMIT, New: $NEW_COMMIT"
            
            # Install/update dependencies
            log_message "Installing Python dependencies..."
            /opt/ebay-auto-parts-lister/venv/bin/pip install -r requirements.txt
            
            # Install Playwright browsers if needed
            log_message "Ensuring Playwright browsers are installed..."
            /opt/ebay-auto-parts-lister/venv/bin/playwright install chromium --with-deps
            
            # Restart the service
            log_message "Restarting service..."
            systemctl restart "$SERVICE_NAME"
            
            # Wait a moment for service to start
            sleep 3
            
            # Check service status
            if systemctl is-active --quiet "$SERVICE_NAME"; then
                log_message "✅ Service restarted successfully"
                log_message "✅ Auto-deployment completed successfully"
            else
                log_message "❌ Service failed to start after restart"
                systemctl status "$SERVICE_NAME" >> "$LOG_FILE"
            fi
        else
            log_message "No new changes detected"
        fi
    else
        log_message "❌ Git pull failed"
        exit 1
    fi
}

# Main execution
if [ "$1" = "webhook" ]; then
    # Called by webhook
    log_message "Auto-deployment triggered by webhook"
    deploy_changes
elif [ "$1" = "check" ]; then
    # Check for changes and deploy if found
    cd "$APP_DIR" || exit 1
    git fetch origin main
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        log_message "Remote changes detected, deploying..."
        deploy_changes
    else
        log_message "No remote changes detected"
    fi
else
    # Manual deployment
    log_message "Manual auto-deployment triggered"
    deploy_changes
fi
