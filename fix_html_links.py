#!/usr/bin/env python3
"""
Quick fix script to add CSS and JS links to generated HTML files.
Run this on already-generated UI files that are missing proper linking.
"""
import sys
from pathlib import Path
import re


def fix_html_links(html_path: Path):
    """Add CSS and JS links to HTML file if missing."""
    if not html_path.exists():
        print(f"❌ File not found: {html_path}")
        return False
    
    html_content = html_path.read_text(encoding='utf-8')
    modified = False
    
    # Check if CSS link exists
    if 'href="styles.css"' not in html_content and '<link rel="stylesheet"' not in html_content:
        # Add CSS link before </head>
        if '</head>' in html_content:
            css_link = '    <link rel="stylesheet" href="styles.css">\n</head>'
            html_content = html_content.replace('</head>', css_link)
            modified = True
            print("✅ Added CSS link: <link rel=\"stylesheet\" href=\"styles.css\">")
        else:
            print("⚠️  No </head> tag found to insert CSS link")
    else:
        print("✓ CSS link already present")
    
    # Check if JS script exists
    if 'src="app.js"' not in html_content and '<script src=' not in html_content:
        # Add JS script before </body>
        if '</body>' in html_content:
            js_script = '    <script src="app.js"></script>\n</body>'
            html_content = html_content.replace('</body>', js_script)
            modified = True
            print("✅ Added JS script: <script src=\"app.js\"></script>")
        else:
            print("⚠️  No </body> tag found to insert JS script")
    else:
        print("✓ JS script already present")
    
    # Remove commented out links/scripts
    if '<!-- <link rel="stylesheet"' in html_content:
        html_content = re.sub(r'<!-- <link rel="stylesheet"[^>]*> -->', '<link rel="stylesheet" href="styles.css">', html_content)
        modified = True
        print("✅ Uncommented CSS link")
    
    if '<!-- <script src=' in html_content:
        html_content = re.sub(r'<!-- <script src="[^"]*"></script> -->', '<script src="app.js"></script>', html_content)
        modified = True
        print("✅ Uncommented JS script")
    
    if modified:
        html_path.write_text(html_content, encoding='utf-8')
        print(f"\n💾 Updated: {html_path}")
        return True
    else:
        print(f"\n✓ No changes needed: {html_path}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_html_links.py <path-to-index.html>")
        print("\nExample:")
        print("  python fix_html_links.py generated_ui/travel-assistant-ui/index.html")
        print("\nOr fix all HTML files in a directory:")
        print("  python fix_html_links.py generated_ui/travel-assistant-ui/")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_file():
        # Fix single file
        print(f"🔧 Fixing: {path}\n")
        fix_html_links(path)
    elif path.is_dir():
        # Fix all index.html files in directory
        html_files = list(path.glob("**/index.html"))
        if not html_files:
            print(f"❌ No index.html files found in: {path}")
            sys.exit(1)
        
        print(f"🔧 Found {len(html_files)} HTML file(s) to fix\n")
        for html_file in html_files:
            print(f"Processing: {html_file}")
            fix_html_links(html_file)
            print()
    else:
        print(f"❌ Invalid path: {path}")
        sys.exit(1)
    
    print("✅ Done!")


if __name__ == "__main__":
    main()
