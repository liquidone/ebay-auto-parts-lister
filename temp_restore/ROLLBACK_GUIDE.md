# 🛡️ Enhanced Identification System - Rollback Guide

## Overview
This guide provides step-by-step instructions to safely rollback the enhanced identification system with browser fallback if needed.

## 🔄 Quick Rollback Options

### Option 1: Feature Flag Rollback (Recommended)
**Instantly disable features without code changes**

```bash
# SSH to your VPS
ssh root@143.198.55.193
cd /opt/ebay-auto-parts-lister

# Edit environment variables
nano .env
```

Add these lines to disable enhanced features:
```env
# Disable enhanced features
ENABLE_BROWSER_FALLBACK=false
ENABLE_ENHANCED_PROMPTS=false
ENABLE_FALLBACK_UI=false
ENABLE_CONFIDENCE_SCORING=false
```

Restart the application:
```bash
systemctl restart ebay-auto-parts-lister
```

### Option 2: Git Branch Rollback
**Complete rollback to previous stable version**

```bash
# Switch back to main branch
git checkout main

# Restart application
systemctl restart ebay-auto-parts-lister
```

### Option 3: Emergency Web Rollback
**Use the web interface for instant rollback**

1. Go to: `https://143.198.55.193/feature-flags`
2. Use the toggle endpoints to disable features
3. Or call the emergency rollback function in browser console:
   ```javascript
   enhancedUI.emergencyRollback()
   ```

## 🚨 Emergency Procedures

### If Application Won't Start
```bash
# Check service status
systemctl status ebay-auto-parts-lister

# View logs
journalctl -u ebay-auto-parts-lister -n 50

# If enhanced modules cause import errors:
# 1. Switch to main branch
git checkout main

# 2. Or temporarily rename problematic modules
mv modules/enhanced_part_identifier.py modules/enhanced_part_identifier.py.disabled
mv modules/gemini_browser_fallback.py modules/gemini_browser_fallback.py.disabled
mv modules/feature_flags.py modules/feature_flags.py.disabled

# 3. Restart service
systemctl restart ebay-auto-parts-lister
```

### If Browser Automation Causes Issues
```bash
# Disable browser fallback only
echo "ENABLE_BROWSER_FALLBACK=false" >> .env
systemctl restart ebay-auto-parts-lister

# Or uninstall playwright
pip uninstall playwright
```

## 📋 Rollback Checklist

### Before Rollback
- [ ] Document the issue causing rollback
- [ ] Check application logs for error details
- [ ] Verify current feature flag status
- [ ] Backup current configuration

### During Rollback
- [ ] Choose appropriate rollback method
- [ ] Test basic functionality after rollback
- [ ] Verify all core features work
- [ ] Check eBay compliance endpoints still work

### After Rollback
- [ ] Monitor application stability
- [ ] Document lessons learned
- [ ] Plan fixes for next iteration
- [ ] Update team on rollback status

## 🔧 Feature Flag Reference

| Feature Flag | Purpose | Safe to Disable |
|-------------|---------|-----------------|
| `ENABLE_BROWSER_FALLBACK` | Browser automation | ✅ Yes |
| `ENABLE_ENHANCED_PROMPTS` | Better AI prompts | ✅ Yes |
| `ENABLE_FALLBACK_UI` | Enhanced UI | ✅ Yes |
| `ENABLE_CONFIDENCE_SCORING` | Result scoring | ✅ Yes |
| `ENABLE_DEBUG_LOGGING` | Extra logging | ✅ Yes |

## 🧪 Testing After Rollback

### Basic Functionality Test
1. Upload an image: `https://143.198.55.193`
2. Verify part identification works
3. Check eBay compliance endpoints:
   - `https://143.198.55.193/ebay/compliance-status`
4. Test image processing pipeline

### API Endpoints Test
```bash
# Test basic identification
curl -X POST "https://143.198.55.193/process-images" \
  -F "files=@test_image.jpg"

# Test compliance endpoints
curl "https://143.198.55.193/ebay/compliance-status"
```

## 📊 Monitoring After Rollback

### Key Metrics to Watch
- Application startup time
- Image processing success rate
- API response times
- Error rates in logs

### Log Locations
```bash
# Application logs
journalctl -u ebay-auto-parts-lister -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Application error logs
tail -f /opt/ebay-auto-parts-lister/logs/app.log
```

## 🔄 Re-enabling Features

### Gradual Re-enablement Strategy
1. **Start with enhanced prompts only**
   ```env
   ENABLE_ENHANCED_PROMPTS=true
   ENABLE_CONFIDENCE_SCORING=true
   ```

2. **Add enhanced UI**
   ```env
   ENABLE_FALLBACK_UI=true
   ```

3. **Finally add browser fallback**
   ```env
   ENABLE_BROWSER_FALLBACK=true
   ```

### Testing Each Phase
- Test thoroughly between each enablement
- Monitor logs for 24 hours after each change
- Have rollback plan ready for each phase

## 🆘 Emergency Contacts

### If You Need Help
1. **Check this guide first**
2. **Review application logs**
3. **Try feature flag rollback**
4. **Use git branch rollback as last resort**

### Recovery Commands Quick Reference
```bash
# Emergency rollback to stable
git checkout main && systemctl restart ebay-auto-parts-lister

# Disable all enhanced features
echo -e "\nENABLE_BROWSER_FALLBACK=false\nENABLE_ENHANCED_PROMPTS=false\nENABLE_FALLBACK_UI=false" >> .env

# Restart application
systemctl restart ebay-auto-parts-lister

# Check status
systemctl status ebay-auto-parts-lister
```

## 📝 Rollback Log Template

```
Date: ___________
Issue: ___________
Rollback Method Used: ___________
Time to Rollback: ___________
Functionality Restored: ___________
Lessons Learned: ___________
Next Steps: ___________
```

---

**Remember: It's better to rollback quickly and investigate than to leave a broken system running!**
