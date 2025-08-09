#!/usr/bin/env python3
"""
Script to remove ALL duplicate inline JavaScript from main.py
Keeps only the console.log statement and lets external JS files handle everything
"""

# Read the main.py file
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the script section and replace it
new_lines = []
in_script = False
script_done = False

for i, line in enumerate(lines):
    if '        <script>' in line and not script_done:
        # Start of script tag - add it
        new_lines.append(line)
        in_script = True
    elif in_script and not script_done:
        if "console.log('eBay Auto Parts Lister - External JS modules loaded');" in line:
            # Keep the console.log line
            new_lines.append(line)
            # Add the closing script tag on next line
            new_lines.append('        </script>\n')
            in_script = False
            script_done = True
        elif '        </script>' in line:
            # If we hit the closing tag without finding console.log, just close it
            new_lines.append(line)
            in_script = False
            script_done = True
        elif "// External JavaScript files" in line:
            # Keep the comment line
            new_lines.append(line)
        # Skip all other lines inside script tag
    elif not in_script:
        # Keep all lines outside of script tag
        new_lines.append(line)

# Write the fixed content back
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully removed ALL duplicate inline JavaScript!")
print("   - Kept only console.log statement")
print("   - External JS files (app.js, debug.js, upload.js) now handle all functionality")
print("   - Script tag properly closed")
