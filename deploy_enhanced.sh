#!/bin/bash
# Safe deployment script for enhanced identification system
# Includes automatic rollback on failure

set -e  # Exit on any error

VPS_IP="143.198.55.193"
APP_DIR="/opt/ebay-auto-parts-lister"
SERVICE_NAME="ebay-auto-parts-lister"

echo "🚀 Starting safe deployment of enhanced identification system..."

# Function to rollback on failure
rollback() {
    echo "❌ Deployment failed! Rolling back..."
    ssh root@$VPS_IP "cd $APP_DIR && git checkout main && systemctl restart $SERVICE_NAME"
    echo "✅ Rollback completed - system restored to stable state"
    exit 1
}

# Set trap for rollback on error
trap rollback ERR

echo "📡 Connecting to VPS: $VPS_IP"

# Step 1: Backup current state
echo "💾 Creating backup of current state..."
ssh root@$VPS_IP "cd $APP_DIR && git stash push -m 'Pre-enhanced-deployment-backup-$(date +%Y%m%d_%H%M%S)'"

# Step 2: Fetch and checkout enhanced branch
echo "📥 Fetching enhanced system code..."
ssh root@$VPS_IP "cd $APP_DIR && git fetch origin feature/browser-fallback"
ssh root@$VPS_IP "cd $APP_DIR && git checkout feature/browser-fallback"

# Step 3: Install new dependencies
echo "📦 Installing new dependencies (Playwright)..."
ssh root@$VPS_IP "cd $APP_DIR && pip install -r requirements.txt"

# Step 4: Install Playwright browsers (with error handling)
echo "🎭 Installing Playwright browsers..."
ssh root@$VPS_IP "cd $APP_DIR && python -m playwright install chromium || echo 'Playwright install failed - browser fallback will be disabled'"

# Step 5: Configure environment with safe defaults
echo "⚙️ Configuring environment with safe defaults..."
ssh root@$VPS_IP "cd $APP_DIR && cat >> .env << 'EOF'

# Enhanced Identification System (Safe Defaults)
ENABLE_BROWSER_FALLBACK=false
ENABLE_ENHANCED_PROMPTS=true
ENABLE_FALLBACK_UI=true
ENABLE_CONFIDENCE_SCORING=true
BROWSER_FALLBACK_MAX_DAILY=10
BROWSER_FALLBACK_DELAY=30
MAX_API_RETRIES=3
ENABLE_DEBUG_LOGGING=false
EOF"

# Step 6: Test application startup
echo "🧪 Testing application startup..."
ssh root@$VPS_IP "cd $APP_DIR && timeout 30 python -c 'from main_full import app; print(\"✅ Application imports successfully\")'"

# Step 7: Restart service
echo "🔄 Restarting application service..."
ssh root@$VPS_IP "systemctl restart $SERVICE_NAME"

# Step 8: Wait and verify service is running
echo "⏳ Waiting for service to start..."
sleep 10

# Step 9: Health check
echo "🏥 Performing health check..."
ssh root@$VPS_IP "systemctl is-active $SERVICE_NAME || (echo 'Service failed to start' && exit 1)"

# Step 10: Test basic endpoints
echo "🔍 Testing basic endpoints..."
curl -f -s "https://$VPS_IP/ebay/compliance-status" > /dev/null || (echo "Basic endpoint test failed" && exit 1)

# Step 11: Test enhanced endpoints
echo "🚀 Testing enhanced endpoints..."
curl -f -s "https://$VPS_IP/feature-flags" > /dev/null || (echo "Enhanced endpoint test failed" && exit 1)

echo "✅ Enhanced identification system deployed successfully!"
echo ""
echo "🎯 Deployment Summary:"
echo "   - Enhanced prompts: ENABLED"
echo "   - Enhanced UI: ENABLED"
echo "   - Confidence scoring: ENABLED"
echo "   - Browser fallback: DISABLED (for safety)"
echo ""
echo "🔧 To enable browser fallback later:"
echo "   ssh root@$VPS_IP"
echo "   cd $APP_DIR"
echo "   echo 'ENABLE_BROWSER_FALLBACK=true' >> .env"
echo "   systemctl restart $SERVICE_NAME"
echo ""
echo "🛡️ To rollback if needed:"
echo "   ssh root@$VPS_IP"
echo "   cd $APP_DIR"
echo "   git checkout main"
echo "   systemctl restart $SERVICE_NAME"
echo ""
echo "🌐 Application URL: https://$VPS_IP"
echo "📊 Feature flags: https://$VPS_IP/feature-flags"

# Remove trap since we succeeded
trap - ERR

echo "🎉 Deployment completed successfully!"
