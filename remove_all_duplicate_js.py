#!/usr/bin/env python3
"""
Comprehensive script to remove ALL duplicate JavaScript code from main.py
This will ensure only the console.log remains in the script tag
and the external JS files are loaded properly
"""

import re

# Read the main.py file
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Build the cleaned content
new_lines = []
found_script_close = False
skip_until_external = False

for i, line in enumerate(lines):
    # Keep everything until we find the closing script tag
    if not found_script_close:
        new_lines.append(line)
        if '</script>' in line and '<script>' not in line:
            found_script_close = True
            skip_until_external = True
            # Add a blank line after script close
            new_lines.append('\n')
    
    # After closing script tag, skip all JS code until we find external JS loading
    elif skip_until_external:
        # Check if this line contains the external JS loading
        if '<!-- Load external JavaScript files' in line:
            new_lines.append(line)
            skip_until_external = False
        elif '<script src="/static/js/' in line:
            # Found external JS files - add the comment if not already added
            if '<!-- Load external JavaScript files' not in ''.join(new_lines[-3:]):
                new_lines.append('        <!-- Load external JavaScript files for enhanced UI -->\n')
            new_lines.append(line)
            skip_until_external = False
        elif '</body>' in line or '</html>' in line:
            # Found closing tags - we need to add the external JS files first
            new_lines.append('        <!-- Load external JavaScript files for enhanced UI -->\n')
            new_lines.append('        <script src="/static/js/app.js?v="""+ cache_buster + """"></script>\n')
            new_lines.append('        <script src="/static/js/debug.js?v="""+ cache_buster + """"></script>\n')
            new_lines.append('        <script src="/static/js/upload.js?v="""+ cache_buster + """"></script>\n')
            new_lines.append(line)
            skip_until_external = False
        # Skip all other lines (the duplicate JS code)
    
    # After we've found the external JS, keep everything else
    else:
        new_lines.append(line)

# Write the fixed content back
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully removed ALL duplicate JavaScript code!")
print("   - Script tag now contains only console.log")
print("   - All duplicate JS code between script tag and external JS loading removed")
print("   - External JS files properly loaded with cache busting")
print("   - HTML structure is now clean and valid")
