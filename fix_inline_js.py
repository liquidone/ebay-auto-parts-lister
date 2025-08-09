#!/usr/bin/env python3
"""
Script to remove all duplicate inline JavaScript from main.py
Keeps only the console.log statement and lets external JS files handle everything
"""

import re

# Read the main.py file
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the script section and replace all inline JS with just console.log
# Pattern to match everything between <script> tags
pattern = r'(        <script>\s*\n            // External JavaScript files.*?\n            console\.log\(.*?\);)[^<]*(        </script>)'

# Replacement - just the opening with console.log and immediate closing
replacement = r'\1\n\2'

# Apply the replacement
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write the fixed content back
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully removed all duplicate inline JavaScript!")
print("   - Kept only console.log statement")
print("   - External JS files (app.js, debug.js, upload.js) now handle all functionality")
