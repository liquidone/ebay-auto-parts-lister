# Quick Setup Instructions for Gemini API Key

## Option 1: Quick One-Line Setup (Easiest)

SSH into your server and run this single command (replace YOUR_API_KEY with your actual key):

```bash
echo "GEMINI_API_KEY=YOUR_API_KEY" > /opt/ebay-auto-parts-lister/.env && chown ebayapp:ebayapp /opt/ebay-auto-parts-lister/.env && chmod 600 /opt/ebay-auto-parts-lister/.env && systemctl restart ebayapp
```

## Option 2: Step by Step

1. SSH into the server:
```bash
ssh root@143.110.157.23
```

2. Create the .env file:
```bash
cd /opt/ebay-auto-parts-lister
nano .env
```

3. Add this line (replace with your actual API key):
```
GEMINI_API_KEY=your_actual_api_key_here
```

4. Save and exit (Ctrl+X, then Y, then Enter)

5. Set permissions:
```bash
chown ebayapp:ebayapp .env
chmod 600 .env
```

6. Restart the service:
```bash
systemctl restart ebayapp
```

## Option 3: Using the Setup Script

1. Copy the setup_api_key.sh script to the server:
```bash
scp setup_api_key.sh root@143.110.157.23:/tmp/
```

2. SSH into the server and run it:
```bash
ssh root@143.110.157.23
chmod +x /tmp/setup_api_key.sh
/tmp/setup_api_key.sh
```

## Verification

After setting up, check that it's working:

1. Open http://143.110.157.23 in your browser
2. Upload some test images
3. Click "Process Images"
4. The debug panel should now show:
   - **Gemini API: Configured** ✓
   - Actual API responses
   - Proper part identification results

## Troubleshooting

If it's still not working, check the logs:
```bash
journalctl -u ebayapp -n 50
```

Or check if the environment variable is set:
```bash
cat /opt/ebay-auto-parts-lister/.env
```
