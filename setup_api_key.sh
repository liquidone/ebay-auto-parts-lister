#!/bin/bash

# Setup script for Gemini API key on production server
# Run this on the production server (143.110.157.23)

echo "==================================="
echo "eBay Auto Parts Lister - API Setup"
echo "==================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root (use sudo)"
   exit 1
fi

# Navigate to application directory
cd /opt/ebay-auto-parts-lister

# Prompt for API key
echo ""
echo "Please enter your Gemini API key:"
read -s GEMINI_KEY
echo ""

# Create .env file with the API key
echo "Creating .env file..."
cat > .env << EOF
# Gemini API Configuration
GEMINI_API_KEY=$GEMINI_KEY

# Optional: Google Cloud Vision API (for OCR)
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
EOF

# Set proper permissions
chown ebayapp:ebayapp .env
chmod 600 .env

echo "✓ .env file created with API key"

# Also add to systemd service for reliability
echo "Updating systemd service..."
sed -i '/\[Service\]/a Environment="GEMINI_API_KEY='"$GEMINI_KEY"'"' /etc/systemd/system/ebayapp.service

# Reload systemd
systemctl daemon-reload

echo "✓ Systemd service updated"

# Restart the application
echo "Restarting application..."
systemctl restart ebayapp

# Wait for service to start
sleep 3

# Check status
if systemctl is-active --quiet ebayapp; then
    echo "✓ Service restarted successfully"
    echo ""
    echo "==================================="
    echo "✅ Setup Complete!"
    echo "==================================="
    echo ""
    echo "The Gemini API key has been configured."
    echo "You can now test the application at:"
    echo "http://143.110.157.23"
    echo ""
    echo "The debug panel should now show:"
    echo "- Gemini API: Configured ✓"
    echo "- API calls will work properly"
else
    echo "⚠️  Service may have issues starting. Check logs with:"
    echo "journalctl -u ebayapp -n 50"
fi
