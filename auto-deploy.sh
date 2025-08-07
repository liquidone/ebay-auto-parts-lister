#!/bin/bash

# Auto-deployment script for eBay Auto Parts Lister
# This script automatically pulls changes from Git and restarts the service
# Test change: Webhook deployment should not hang - 2025-08-06

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
    
    # Handle any local changes by stashing them
    log_message "Checking for local changes..."
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_message "Local changes detected, stashing them..."
        git stash push -m "Auto-stash before deployment $(date)"
    fi
    
    # Pull latest changes
    log_message "Pulling latest changes from Git..."
    if git pull origin main; then
        NEW_COMMIT=$(git rev-parse HEAD)
        
        if [ "$OLD_COMMIT" != "$NEW_COMMIT" ]; then
            log_message "New changes detected. Old: $OLD_COMMIT, New: $NEW_COMMIT"
            
            # Install/update dependencies
            log_message "Installing Python dependencies..."
            /opt/ebay-auto-parts-lister/venv/bin/pip install -r requirements.txt
            
            # Ensure Playwright browsers are installed for the service user
            log_message "Ensuring Playwright browsers are installed for ebayapp user..."
            sudo -u ebayapp /opt/ebay-auto-parts-lister/venv/bin/playwright install chromium --with-deps
            
            # Restart the service with timeout
            log_message "Restarting service..."
            timeout 15 systemctl restart "$SERVICE_NAME" || {
                log_message "⚠️ Service restart timed out after 15 seconds, continuing..."
            }
            
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

# Function to run deployment in background
run_deployment_background() {
    {
        deploy_changes
        log_message "Auto-deployment process completed"
    } &
    
    # Get the background process ID
    DEPLOY_PID=$!
    log_message "Deployment started in background (PID: $DEPLOY_PID)"
    
    # If called manually (not webhook), wait briefly then detach
    if [ "$1" != "webhook" ]; then
        echo "Deployment started in background. Check logs with: tail -f /var/log/auto-deploy.log"
        echo "Process ID: $DEPLOY_PID"
    fi
}

# Main execution
if [ "$1" = "webhook" ]; then
    # Called by webhook - run in background and exit immediately
    log_message "Auto-deployment triggered by webhook"
    run_deployment_background "webhook"
    exit 0
elif [ "$1" = "check" ]; then
    # Check for changes and deploy if found
    cd "$APP_DIR" || exit 1
    git fetch origin main
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        log_message "Remote changes detected, deploying..."
        run_deployment_background "check"
    else
        log_message "No remote changes detected"
    fi
    exit 0
else
    # Manual deployment - run in background
    log_message "Manual auto-deployment triggered"
    run_deployment_background "manual"
    exit 0
fi
