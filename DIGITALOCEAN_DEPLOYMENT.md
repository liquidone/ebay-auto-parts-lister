# 🚀 DigitalOcean VPS Deployment Guide - eBay Auto Parts Lister

## 🎯 Why DigitalOcean VPS?

✅ **Full control** - No build restrictions, install anything  
✅ **Better performance** - Dedicated resources, no cold starts  
✅ **Cost effective** - $6/month for reliable hosting  
✅ **Complete OpenCV support** - No dependency issues  
✅ **Always running** - 24/7 availability  
✅ **Easy scaling** - Upgrade resources anytime  

## 💰 **Recommended Droplet Configuration**

**Basic Droplet ($6/month):**
- **1 GB RAM** - Sufficient for your app
- **1 vCPU** - Handles concurrent users well
- **25 GB SSD** - Plenty of storage
- **1000 GB transfer** - More than enough bandwidth
- **Ubuntu 22.04 LTS** - Stable, long-term support

## 🚀 **Quick Deployment (15 minutes total)**

### Step 1: Create DigitalOcean Droplet (3 minutes)

1. **Sign up at [digitalocean.com](https://digitalocean.com)**
2. **Create new Droplet:**
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic $6/month (1GB RAM, 1 vCPU)
   - **Region:** Choose closest to your users
   - **Authentication:** SSH Key (recommended) or Password
   - **Hostname:** `ebay-auto-parts-lister`

3. **Note your droplet's IP address** (you'll need this)

### Step 2: Connect to Your Droplet (1 minute)

**Windows (using PowerShell):**
```powershell
ssh root@YOUR_DROPLET_IP
```

**Or use PuTTY if you prefer a GUI**

### Step 3: Run Deployment Script (10 minutes)

```bash
# Download and run the deployment script
curl -sSL https://raw.githubusercontent.com/liquidone/ebay-auto-parts-lister/main/deploy_digitalocean.sh | bash
```

### Step 4: Configure API Keys (1 minute)

```bash
# Edit the environment file
nano /opt/ebay-auto-parts-lister/.env

# Add your actual API keys:
GEMINI_API_KEY=your_actual_gemini_key_here
OPENAI_API_KEY=your_actual_openai_key_here
EBAY_APP_ID=your_actual_ebay_app_id
EBAY_DEV_ID=your_actual_ebay_dev_id
EBAY_CERT_ID=your_actual_ebay_cert_id
EBAY_USER_TOKEN=your_actual_ebay_user_token
```

### Step 5: Start Services (1 minute)

```bash
# Setup and start all services
bash /opt/ebay-auto-parts-lister/setup_services.sh
```

## 🎉 **You're Live!**

Your eBay Auto Parts Lister is now running at: `http://YOUR_DROPLET_IP`

## 🔧 **Post-Deployment Setup**

### Security (Recommended)

```bash
# Enable firewall
ufw enable
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
```

### Optional: Custom Domain + SSL

If you have a domain name:

```bash
# Point your domain to your droplet IP, then:
bash /opt/ebay-auto-parts-lister/setup_ssl.sh yourdomain.com
```

## 🛠️ **Management Commands**

```bash
# Check status
bash /opt/ebay-auto-parts-lister/maintenance.sh status

# View logs
bash /opt/ebay-auto-parts-lister/maintenance.sh logs

# Restart services
bash /opt/ebay-auto-parts-lister/maintenance.sh restart

# Create backup
bash /opt/ebay-auto-parts-lister/maintenance.sh backup

# Update application
bash /opt/ebay-auto-parts-lister/maintenance.sh update

# Clean old files
bash /opt/ebay-auto-parts-lister/maintenance.sh clean
```

## 🎯 **What You Get**

- **🤖 Full Gemini AI** part identification (no restrictions!)
- **🖼️ Complete OpenCV** image processing (crop, rotate, enhance)
- **🛒 eBay API integration** for automated listings
- **💰 Market pricing** suggestions
- **📊 Database tracking** with SQLite
- **🌐 Production web server** with nginx reverse proxy
- **🔄 Auto-restart** on crashes with systemd
- **💾 Easy backups** and maintenance scripts

## 🚨 **Troubleshooting**

**Service won't start:**
```bash
sudo systemctl status ebay-auto-parts-lister
sudo journalctl -u ebay-auto-parts-lister -f
```

**Nginx issues:**
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Permission issues:**
```bash
sudo chown -R ebayapp:ebayapp /opt/ebay-auto-parts-lister
```

**Update application:**
```bash
cd /opt/ebay-auto-parts-lister
sudo -u ebayapp git pull origin main
sudo systemctl restart ebay-auto-parts-lister
```

## 💡 **Scaling Up**

**Need more power?**
- **Resize droplet** in DigitalOcean dashboard (takes 2 minutes)
- **Add more workers** in systemd service file
- **Enable database backups** to DigitalOcean Spaces
- **Add load balancer** for multiple droplets

## 📊 **Cost Breakdown**

- **Droplet:** $6/month
- **Domain (optional):** $10-15/year
- **SSL Certificate:** Free (Let's Encrypt)
- **Backups (optional):** $1.20/month (20% of droplet cost)

**Total: ~$6-8/month for production-ready hosting**

## 🆘 **Support**

**DigitalOcean has excellent documentation:**
- [Initial Server Setup](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-22-04)
- [Nginx Configuration](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-22-04)
- [SSL with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-22-04)

**Need help?** DigitalOcean has 24/7 support and an active community forum.

---

**🎉 Enjoy your fully-featured eBay Auto Parts Lister running on a reliable VPS!**
