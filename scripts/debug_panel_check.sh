#!/bin/bash

# Debug Panel Diagnostic Script
echo "=== Starting Debug Panel Diagnostic ==="
echo "Timestamp: $(date)"
echo ""

# 1. Environment check
echo "1. Environment:"
echo "   - Hostname: $(hostname)"
echo "   - Python: $(python3 --version 2>&1 || echo "Not found")"
echo "   - pip: $(pip3 --version 2>&1 || echo "Not found")"
echo "   - Node.js: $(node --version 2>&1 || echo "Not found")"
echo "   - npm: $(npm --version 2>&1 || echo "Not found")"
echo ""

# 2. Service status
echo "2. Service Status:"
SERVICE="ebay-auto-parts-lister"
SYSTEMCTL="systemctl --no-pager"
$SYSTEMCTL status $SERVICE --no-pager | head -n 7
echo ""

# 3. Check API endpoint
echo "3. API Endpoint Check:"
echo "   Testing /health endpoint..."
curl -s -o /dev/null -w "   Status: %{http_code}\n" http://localhost:8000/health
echo ""

# 4. Check debug endpoint
echo "4. Debug Endpoint Check:"
echo "   Testing /debug endpoint (if exists)..."
curl -s -o /dev/null -w "   Status: %{http_code}\n" http://localhost:8000/debug
echo ""

# 5. Check logs for errors
echo "5. Recent Logs (errors only):"
journalctl -u $SERVICE --since "5 minutes ago" -n 20 | grep -i "error\|exception\|traceback" | tail -n 10 || echo "   No recent errors found"
echo ""

# 6. Check debug panel HTML
echo "6. Debug Panel HTML Check:"
if [ -f "/opt/ebay-auto-parts-lister/templates/index.html" ]; then
    echo "   Found index.html"
    grep -A5 "debug-panel" /opt/ebay-auto-parts-lister/templates/index.html || echo "   Could not find debug panel in HTML"
else
    echo "   index.html not found in expected location"
fi
echo ""

# 7. Check JavaScript files
echo "7. JavaScript Files Check:"
find /opt/ebay-auto-parts-lister/static/js -name "*.js" -type f -exec ls -la {} \;
echo ""

# 8. Check backend debug output
echo "8. Backend Debug Output Check:"
if [ -f "/opt/ebay-auto-parts-lister/modules/part_identifier.py" ]; then
    echo "   Checking for debug_output in part_identifier.py..."
    grep -A10 "debug_output" /opt/ebay-auto-parts-lister/modules/part_identifier.py | head -n 20
else
    echo "   part_identifier.py not found"
fi
echo ""

# 9. Run a test API call
echo "9. Running Test API Call:"
TEST_FILE="/opt/ebay-auto-parts-lister/static/test_image.jpg"
if [ -f "$TEST_FILE" ]; then
    echo "   Using test image: $TEST_FILE"
    curl -X POST -F "image=@$TEST_FILE" http://localhost:8000/process | jq '{
        success: .success,
        has_debug_output: (.debug_output != null),
        debug_keys: (.debug_output | keys_unsorted),
        error: .error
    }'
else
    echo "   Test image not found at $TEST_FILE"
    echo "   Testing with empty file..."
    curl -X POST -F "image=@/dev/null" http://localhost:8000/process | jq '{
        success: .success,
        has_debug_output: (.debug_output != null),
        error: .error
    }'
fi
echo ""

echo "=== Diagnostic Complete ==="
echo "View full logs: journalctl -u $SERVICE -n 100"
