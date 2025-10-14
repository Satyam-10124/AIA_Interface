# Testing Guide - UI Generator with Linked Files

## ✅ What Was Fixed

The UI generator now automatically links HTML, CSS, and JavaScript files together:
- `<link rel="stylesheet" href="styles.css">` in `<head>`
- `<script src="app.js"></script>` before `</body>`

---

## 🧪 Test New Generation (With Auto-Linking)

This will create a fully linked UI with all fixes applied:

```bash
cd /Users/satyamsinghal/Desktop/Products/AIA_Interface

python ui_generator_cli.py \
  --agent-description "E-commerce shopping assistant with product recommendations" \
  --agent-capabilities "product search, cart management, checkout, recommendations" \
  --theme dark \
  --layout compact \
  --color-scheme blue \
  --output-name "shopping-assistant-ui" \
  --verbose
```

**Expected output:**
```
🔍 Pre-Flight Environment Validation
✅ GEMINI_API_KEY found
✅ Output directory created
...
📝 Saved index.html (XXXX characters)
📝 Saved styles.css (XXXX characters)
📝 Saved app.js (XXXX characters)
💾 Files saved to: ./generated_ui/shopping-assistant-ui
```

---

## 🔧 Fix Already-Generated Files

If you have existing UI files without proper linking, use the fix script:

### Fix Single UI Project
```bash
python fix_html_links.py generated_ui/travel-assistant-ui/index.html
```

### Fix All UI Projects
```bash
python fix_html_links.py generated_ui/
```

**Output:**
```
🔧 Fixing: generated_ui/travel-assistant-ui/index.html

✅ Added CSS link: <link rel="stylesheet" href="styles.css">
✅ Added JS script: <script src="app.js"></script>

💾 Updated: generated_ui/travel-assistant-ui/index.html
✅ Done!
```

---

## 🌐 View Generated UI in Browser

### Option 1: Simple HTTP Server (Recommended)
```bash
cd generated_ui/travel-assistant-ui

# Python 3
python3 -m http.server 8000

# Then open: http://localhost:8000
```

### Option 2: Open Directly
```bash
open generated_ui/travel-assistant-ui/index.html
```

⚠️ Note: Some features may not work when opened directly due to browser security restrictions. Use HTTP server for best results.

---

## 🔍 Verify Linking

Check that the generated HTML has proper tags:

```bash
# Check CSS link
grep -n "styles.css" generated_ui/travel-assistant-ui/index.html

# Check JS script
grep -n "app.js" generated_ui/travel-assistant-ui/index.html

# View head section
head -20 generated_ui/shopping-assistant-ui/index.html
```

**You should see:**
```html
<head>
    ...
    <link rel="stylesheet" href="styles.css">
</head>
```

**And before closing body:**
```html
    <script src="app.js"></script>
</body>
```

---

## 🎨 Verify Files Work Together

### 1. Check Files Exist
```bash
ls -lh generated_ui/shopping-assistant-ui/
```

Expected:
```
-rw-r--r--  index.html   (HTML structure)
-rw-r--r--  styles.css   (Styling)
-rw-r--r--  app.js       (Interactivity)
```

### 2. Test in Browser
After starting HTTP server, open browser console (F12) and check:
- **Console tab:** No 404 errors for styles.css or app.js
- **Elements tab:** Styles are applied (check computed styles)
- **Network tab:** Both files loaded successfully (200 status)

### 3. Interactive Test
- Type a message in the chat input
- Click "Send" button
- Verify:
  - ✅ Message appears in chat
  - ✅ Loading indicator shows
  - ✅ Agent responds after delay
  - ✅ Styles are applied (colors, spacing)

---

## 📊 Compare Before/After

### Before Fix (Broken Linking)
```html
<head>
    ...
    <!-- <link rel="stylesheet" href="style.css"> -->
</head>
<body>
    ...
    <!-- No script tag -->
</body>
```

❌ Result: Unstyled HTML, no interactivity

### After Fix (Proper Linking)
```html
<head>
    ...
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    ...
    <script src="app.js"></script>
</body>
```

✅ Result: Fully styled and interactive UI

---

## 🐛 Troubleshooting

### CSS Not Applied
```bash
# Check if CSS file exists
ls -lh generated_ui/*/styles.css

# Check HTML has CSS link
grep "styles.css" generated_ui/*/index.html

# Fix if missing
python fix_html_links.py generated_ui/your-ui-name/index.html
```

### JavaScript Not Working
```bash
# Check if JS file exists
ls -lh generated_ui/*/app.js

# Check HTML has JS script
grep "app.js" generated_ui/*/index.html

# Check browser console for errors (F12 → Console tab)
```

### 404 Errors
- Make sure you're using HTTP server, not `file://` protocol
- Verify CSS/JS files are in same directory as index.html
- Check file names match exactly (case-sensitive)

---

## ✅ Success Checklist

- [ ] Generated 3 files: index.html, styles.css, app.js
- [ ] HTML contains `<link rel="stylesheet" href="styles.css">`
- [ ] HTML contains `<script src="app.js"></script>`
- [ ] HTTP server running on localhost
- [ ] No 404 errors in browser console
- [ ] Styles are applied (dark theme, colors, spacing)
- [ ] Chat is interactive (send messages, get responses)
- [ ] Buttons and forms work

---

## 🚀 Quick Full Test

Run this to generate, fix, and test:

```bash
#!/bin/bash
cd /Users/satyamsinghal/Desktop/Products/AIA_Interface

# 1. Generate new UI
echo "1️⃣ Generating UI..."
python ui_generator_cli.py \
  --agent-description "Weather forecast assistant" \
  --agent-capabilities "current weather, forecast, alerts" \
  --output-name "test-weather-ui"

# 2. Verify files
echo -e "\n2️⃣ Verifying files..."
ls -lh generated_ui/test-weather-ui/

# 3. Check linking
echo -e "\n3️⃣ Checking CSS link..."
grep "styles.css" generated_ui/test-weather-ui/index.html

echo -e "\n4️⃣ Checking JS script..."
grep "app.js" generated_ui/test-weather-ui/index.html

# 4. Start server
echo -e "\n5️⃣ Starting HTTP server..."
echo "Open http://localhost:8000 in your browser"
cd generated_ui/test-weather-ui
python3 -m http.server 8000
```

---

## 📝 Notes

1. **New generations** after the fix will have proper linking automatically
2. **Old generations** need to run `fix_html_links.py` once
3. Always use **HTTP server** for testing, not direct file opening
4. Check **browser console** for any errors

---

**Status:** ✅ Linking fix implemented and tested
**Next Test:** Generate a new UI and verify all files work together
