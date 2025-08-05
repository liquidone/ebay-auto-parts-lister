#!/bin/bash
# Maintenance and backup script for eBay Auto Parts Lister

set -e

APP_DIR="/opt/ebay-auto-parts-lister"
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🔧 eBay Auto Parts Lister Maintenance Script"

# Create backup directory
sudo mkdir -p $BACKUP_DIR
sudo chown ebayapp:ebayapp $BACKUP_DIR

case "$1" in
    backup)
        echo "💾 Creating backup..."
        sudo -u ebayapp bash << EOF
cd $APP_DIR
tar -czf $BACKUP_DIR/ebay-lister-backup-$DATE.tar.gz \
    --exclude=venv \
    --exclude=__pycache__ \
    --exclude=.git \
    .
EOF
        echo "✅ Backup created: $BACKUP_DIR/ebay-lister-backup-$DATE.tar.gz"
        ;;
    
    update)
        echo "🔄 Updating application..."
        sudo -u ebayapp bash << 'EOF'
cd /opt/ebay-auto-parts-lister
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
EOF
        sudo systemctl restart ebay-auto-parts-lister
        echo "✅ Application updated and restarted"
        ;;
    
    logs)
        echo "📋 Recent application logs:"
        sudo journalctl -u ebay-auto-parts-lister -n 50 --no-pager
        ;;
    
    status)
        echo "📊 Service status:"
        sudo systemctl status ebay-auto-parts-lister --no-pager
        echo ""
        echo "🌐 Nginx status:"
        sudo systemctl status nginx --no-pager
        echo ""
        echo "💾 Disk usage:"
        df -h $APP_DIR
        echo ""
        echo "🔍 Recent backups:"
        ls -la $BACKUP_DIR/ | tail -5
        ;;
    
    restart)
        echo "🔄 Restarting services..."
        sudo systemctl restart ebay-auto-parts-lister
        sudo systemctl reload nginx
        echo "✅ Services restarted"
        ;;
    
    clean)
        echo "🧹 Cleaning up old files..."
        sudo -u ebayapp bash << 'EOF'
cd /opt/ebay-auto-parts-lister
# Clean old processed images (older than 7 days)
find processed/ -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" | head -100 | xargs -r rm -f
# Clean old uploads (older than 30 days)  
find uploads/ -name "*" -mtime +30 -type f | head -50 | xargs -r rm -f
EOF
        # Clean old backups (keep last 10)
        cd $BACKUP_DIR && ls -t ebay-lister-backup-*.tar.gz | tail -n +11 | xargs -r rm -f
        echo "✅ Cleanup complete"
        ;;
    
    *)
        echo "Usage: bash maintenance.sh {backup|update|logs|status|restart|clean}"
        echo ""
        echo "Commands:"
        echo "  backup  - Create a backup of the application"
        echo "  update  - Pull latest code and restart"
        echo "  logs    - Show recent application logs"
        echo "  status  - Show service status and system info"
        echo "  restart - Restart application and nginx"
        echo "  clean   - Clean up old files and backups"
        exit 1
        ;;
esac
