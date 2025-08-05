#!/bin/bash
# Setup systemd service and nginx for eBay Auto Parts Lister

set -e

echo "🔧 Setting up systemd service and nginx..."

# Create systemd service file
echo "📝 Creating systemd service..."
sudo tee /etc/systemd/system/ebay-auto-parts-lister.service > /dev/null << 'EOF'
[Unit]
Description=eBay Auto Parts Lister FastAPI Application
After=network.target

[Service]
Type=simple
User=ebayapp
Group=ebayapp
WorkingDirectory=/opt/ebay-auto-parts-lister
Environment=PATH=/opt/ebay-auto-parts-lister/venv/bin
ExecStart=/opt/ebay-auto-parts-lister/venv/bin/uvicorn main_full:app --host 127.0.0.1 --port 8000 --workers 2
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
echo "🌐 Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/ebay-auto-parts-lister > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /opt/ebay-auto-parts-lister/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias /opt/ebay-auto-parts-lister/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
EOF

# Enable nginx site
echo "🔗 Enabling nginx site..."
sudo ln -sf /etc/nginx/sites-available/ebay-auto-parts-lister /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "✅ Testing nginx configuration..."
sudo nginx -t

# Reload systemd and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ebay-auto-parts-lister
sudo systemctl start ebay-auto-parts-lister
sudo systemctl reload nginx

# Check service status
echo "📊 Service status:"
sudo systemctl status ebay-auto-parts-lister --no-pager -l

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your eBay Auto Parts Lister is now running at:"
echo "   http://$(curl -s ifconfig.me)"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status ebay-auto-parts-lister    # Check status"
echo "   sudo systemctl restart ebay-auto-parts-lister   # Restart app"
echo "   sudo systemctl logs -f ebay-auto-parts-lister   # View logs"
echo "   sudo nginx -t && sudo systemctl reload nginx    # Reload nginx"
echo ""
echo "📝 Next steps:"
echo "1. Configure your API keys in /opt/ebay-auto-parts-lister/.env"
echo "2. Restart the service: sudo systemctl restart ebay-auto-parts-lister"
echo "3. Set up firewall: sudo ufw enable && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw allow 22"
echo "4. Optional: Set up SSL with certbot for HTTPS"
