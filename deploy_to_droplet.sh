#!/bin/bash

# eBay Auto Parts Lister - Clean Deployment Script
# Version: 1.0.0
# Date: 2025-08-09

set -e  # Exit on error

echo "========================================="
echo "eBay Auto Parts Lister Deployment"
echo "========================================="
echo ""

# Phase 1: System Update
echo "Phase 1: Updating System..."
apt update
apt upgrade -y

# Phase 2: Install Dependencies
echo ""
echo "Phase 2: Installing Dependencies..."
apt install -y python3 python3-pip python3-venv python3-dev git nginx curl wget
apt install -y libpng-dev libjpeg-dev libtiff-dev libwebp-dev
apt install -y certbot python3-certbot-nginx

# Phase 3: Create User and Directories
echo ""
echo "Phase 3: Setting up User and Directories..."
useradd -m -s /bin/bash ebayapp || echo "User already exists"
mkdir -p /opt/ebay-auto-parts-lister
chown ebayapp:ebayapp /opt/ebay-auto-parts-lister

# Phase 4: Clone Repository
echo ""
echo "Phase 4: Cloning Repository..."
cd /opt
rm -rf ebay-auto-parts-lister
git clone https://github.com/liquidone/ebay-auto-parts-lister.git
chown -R ebayapp:ebayapp /opt/ebay-auto-parts-lister

# Phase 5: Setup Python Environment
echo ""
echo "Phase 5: Setting up Python Environment..."
cd /opt/ebay-auto-parts-lister
sudo -u ebayapp python3 -m venv venv
sudo -u ebayapp ./venv/bin/pip install --upgrade pip
sudo -u ebayapp ./venv/bin/pip install -r requirements.txt

# Phase 6: Create Environment File
echo ""
echo "Phase 6: Creating Environment Configuration..."
cat > /opt/ebay-auto-parts-lister/.env << 'EOF'
# Google Gemini API Key
GEMINI_API_KEY=AIzaSyDgwlzV1rNvBUbqyKNvubeLuBxbHWmql1s

# Application Settings
APP_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Google Cloud Vision API
GOOGLE_APPLICATION_CREDENTIALS=/opt/ebay-auto-parts-lister/vision-credentials.json
EOF

chown ebayapp:ebayapp /opt/ebay-auto-parts-lister/.env
chmod 600 /opt/ebay-auto-parts-lister/.env

# Phase 7: Setup Systemd Service
echo ""
echo "Phase 7: Creating Systemd Service..."
cat > /etc/systemd/system/ebay-auto-parts-lister.service << 'EOF'
[Unit]
Description=eBay Auto Parts Lister FastAPI Application
After=network.target

[Service]
Type=simple
User=ebayapp
Group=ebayapp
WorkingDirectory=/opt/ebay-auto-parts-lister
Environment="PATH=/opt/ebay-auto-parts-lister/venv/bin"
Environment="PYTHONPATH=/opt/ebay-auto-parts-lister"
Environment="GEMINI_API_KEY=AIzaSyDgwlzV1rNvBUbqyKNvubeLuBxbHWmql1s"
ExecStart=/opt/ebay-auto-parts-lister/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/ebay-auto-parts-lister/app.log
StandardError=append:/var/log/ebay-auto-parts-lister/error.log

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
mkdir -p /var/log/ebay-auto-parts-lister
chown -R ebayapp:ebayapp /var/log/ebay-auto-parts-lister

# Phase 8: Configure Nginx
echo ""
echo "Phase 8: Configuring Nginx..."
cat > /etc/nginx/sites-available/ebay-auto-parts-lister << 'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    location /static {
        alias /opt/ebay-auto-parts-lister/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/ebay-auto-parts-lister /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# Phase 9: Configure Firewall
echo ""
echo "Phase 9: Configuring Firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
echo "y" | ufw enable

# Phase 10: Start Services
echo ""
echo "Phase 10: Starting Services..."
systemctl daemon-reload
systemctl enable ebay-auto-parts-lister
systemctl start ebay-auto-parts-lister
systemctl restart nginx

# Create auto-deploy script
echo ""
echo "Creating Auto-Deploy Script..."
cat > /opt/ebay-auto-parts-lister/deploy.sh << 'EOF'
#!/bin/bash
cd /opt/ebay-auto-parts-lister
git pull origin main
./venv/bin/pip install -r requirements.txt
systemctl restart ebay-auto-parts-lister
systemctl restart nginx
echo "Deployment complete at $(date)" >> /var/log/ebay-auto-parts-lister/deploy.log
EOF

chmod +x /opt/ebay-auto-parts-lister/deploy.sh
chown ebayapp:ebayapp /opt/ebay-auto-parts-lister/deploy.sh

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Service Status:"
systemctl status ebay-auto-parts-lister --no-pager
echo ""
echo "Nginx Status:"
systemctl status nginx --no-pager
echo ""
echo "Application URL: http://143.110.157.23"
echo ""
echo "Logs:"
echo "  App: /var/log/ebay-auto-parts-lister/app.log"
echo "  Error: /var/log/ebay-auto-parts-lister/error.log"
echo ""
echo "To deploy updates: /opt/ebay-auto-parts-lister/deploy.sh"
echo ""
