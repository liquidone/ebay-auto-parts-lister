#!/bin/bash

# Setup script for auto-deployment system
# Run this on your VPS to enable automatic deployments

echo "🚀 Setting up auto-deployment system..."

APP_DIR="/opt/ebay-auto-parts-lister"
cd "$APP_DIR" || exit 1

# Make scripts executable
chmod +x auto-deploy.sh
chmod +x webhook-server.py

# Copy systemd service file
cp webhook-server.service /etc/systemd/system/
systemctl daemon-reload

# Create log directory
mkdir -p /var/log
touch /var/log/auto-deploy.log
touch /var/log/webhook-server.log

# Enable and start webhook server
systemctl enable webhook-server
systemctl start webhook-server

# Check status
echo "📊 Service Status:"
systemctl status webhook-server --no-pager -l

echo ""
echo "✅ Auto-deployment system installed!"
echo ""
echo "📝 Next steps:"
echo "1. Go to your GitHub repository settings"
echo "2. Add webhook: http://143.110.157.23:9000/webhook"
echo "3. Set content type to 'application/json'"
echo "4. Select 'Just the push event'"
echo "5. Make sure webhook is active"
echo ""
echo "🧪 Test the system:"
echo "- Push changes to main branch"
echo "- Watch logs: journalctl -u webhook-server -f"
echo "- Check deployment logs: tail -f /var/log/auto-deploy.log"
echo ""
echo "🔧 Manual deployment:"
echo "- Run: bash /opt/ebay-auto-parts-lister/auto-deploy.sh"
echo ""
echo "🌐 Health check:"
echo "- Visit: http://143.110.157.23:9000/health"
