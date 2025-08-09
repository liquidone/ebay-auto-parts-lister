#!/bin/bash
# Optional SSL setup with Let's Encrypt for eBay Auto Parts Lister
# Run this after you have a domain name pointing to your droplet

set -e

# Check if domain is provided
if [ -z "$1" ]; then
    echo "Usage: bash setup_ssl.sh your-domain.com"
    echo "Example: bash setup_ssl.sh ebay-lister.yourdomain.com"
    exit 1
fi

DOMAIN=$1

echo "🔒 Setting up SSL certificate for $DOMAIN..."

# Install certbot
echo "📦 Installing certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
echo "🔐 Obtaining SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Update nginx configuration for SSL
echo "🌐 Updating nginx configuration..."
sudo tee /etc/nginx/sites-available/ebay-auto-parts-lister > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    client_max_body_size 50M;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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

# Test and reload nginx
echo "✅ Testing nginx configuration..."
sudo nginx -t
sudo systemctl reload nginx

# Set up automatic renewal
echo "🔄 Setting up automatic SSL renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo ""
echo "✅ SSL setup complete!"
echo ""
echo "🌐 Your eBay Auto Parts Lister is now running securely at:"
echo "   https://$DOMAIN"
echo ""
echo "🔒 SSL certificate will auto-renew every 90 days"
echo "📊 Check renewal status: sudo certbot certificates"
