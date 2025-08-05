#!/bin/bash
# DigitalOcean Ubuntu 22.04 Deployment Script for eBay Auto Parts Lister
# Run this script on a fresh Ubuntu 22.04 droplet

set -e  # Exit on any error

echo "🚀 Starting eBay Auto Parts Lister deployment on DigitalOcean..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and required system packages
echo "🐍 Installing Python 3.11 and dependencies..."
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev
sudo apt install -y git nginx supervisor
sudo apt install -y build-essential cmake pkg-config
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev libgtk-3-dev
sudo apt install -y libatlas-base-dev gfortran
sudo apt install -y python3-opencv

# Create application user
echo "👤 Creating application user..."
sudo useradd -m -s /bin/bash ebayapp || true
sudo usermod -aG sudo ebayapp

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/ebay-auto-parts-lister
sudo chown ebayapp:ebayapp /opt/ebay-auto-parts-lister

# Switch to application user for the rest
sudo -u ebayapp bash << 'EOF'
cd /opt/ebay-auto-parts-lister

# Clone the repository
echo "📥 Cloning repository..."
git clone https://github.com/liquidone/ebay-auto-parts-lister.git .

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies (use full requirements.txt for VPS)
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📂 Creating application directories..."
mkdir -p uploads processed static logs

# Create environment file template
echo "⚙️ Creating environment configuration..."
cp .env.template .env
echo "
# Update these with your actual API keys:
# GEMINI_API_KEY=your_actual_gemini_key
# OPENAI_API_KEY=your_actual_openai_key  
# EBAY_APP_ID=your_actual_ebay_app_id
# EBAY_DEV_ID=your_actual_ebay_dev_id
# EBAY_CERT_ID=your_actual_ebay_cert_id
# EBAY_USER_TOKEN=your_actual_ebay_user_token
" >> .env

EOF

echo "✅ Application setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit /opt/ebay-auto-parts-lister/.env with your API keys"
echo "2. Run: sudo bash /opt/ebay-auto-parts-lister/setup_services.sh"
echo "3. Your app will be running at http://your-droplet-ip"
echo ""
echo "📝 Don't forget to:"
echo "- Configure your firewall (ufw enable, ufw allow 80, ufw allow 443, ufw allow 22)"
echo "- Set up SSL certificate with certbot (optional)"
echo "- Configure domain name (optional)"
