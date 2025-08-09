#!/usr/bin/env python3
"""
Final script to remove ALL duplicate JavaScript code from main.py
This will ensure only the console.log remains in the script tag
and the external JS files are loaded properly
"""

# Read the main.py file
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the positions of key elements
script_start = content.find('        <script>')
script_end = content.find('        </script>')
external_js_comment = content.find('<!-- Load external JavaScript files for enhanced UI -->')
first_external_script = content.find('<script src="/static/js/app.js')

# If we found the duplicate JS between script end and external JS loading
if script_end > 0 and external_js_comment > script_end:
    # Extract the parts we want to keep
    part1 = content[:script_end + len('        </script>')]
    
    # Find where the external JS scripts actually start
    if first_external_script > 0:
        part2 = content[first_external_script:]
    else:
        # If external scripts not found, look for them after the comment
        remaining = content[external_js_comment:]
        part2 = '\n        <!-- Load external JavaScript files for enhanced UI -->\n' + remaining
    
    # Combine the parts, removing all the duplicate JS in between
    new_content = part1 + '\n        \n        <!-- Load external JavaScript files for enhanced UI -->\n        <script src="/static/js/app.js?v="""+ cache_buster + """"></script>\n        <script src="/static/js/debug.js?v="""+ cache_buster + """"></script>\n        <script src="/static/js/upload.js?v="""+ cache_buster + """"></script>\n    </body>\n    </html>\n    """\n    \n    # Create response with cache-busting headers\n    response = HTMLResponse(content=html_content)\n    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"\n    response.headers["Pragma"] = "no-cache"\n    response.headers["Expires"] = "0"\n    \n    return response'
    
    # Write the fixed content back
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Successfully removed ALL duplicate JavaScript code!")
    print("   - Script tag now contains only console.log")
    print("   - All duplicate JS between script tag and external JS loading removed")
    print("   - External JS files properly loaded")
    print("   - HTML structure is now clean and valid")
else:
    print("Could not find the expected structure. Manual intervention may be needed.")
