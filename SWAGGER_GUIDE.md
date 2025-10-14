# 📚 Swagger UI Guide - AIA Interface API

## 🎯 What is Swagger UI?

Swagger UI is an **interactive API documentation** interface that lets you:
- 🧪 Test all API endpoints directly from your browser
- 📖 View detailed request/response schemas
- ✅ Validate your API calls before coding
- 🚀 Generate code snippets for different languages

---

## 🌐 Access Swagger UI

### 1. Start the API Server

```bash
cd /Users/satyamsinghal/Desktop/Products/AIA_Interface
python api_server.py
```

### 2. Open Swagger UI in Browser

```
http://localhost:5080/api/docs
```

You'll see a beautiful, interactive documentation page!

---

## 🎨 Swagger UI Features

### **Main Sections**

1. **System Endpoints** (Green)
   - Health checks
   - Environment validation

2. **UI Generator** (Blue)
   - Generate UI interfaces
   - Check job status
   - Download generated files
   - Preview live UIs

3. **Agent Generator** (Purple)
   - Generate AI agent code
   - Check agent generation status
   - Download agent bundles

4. **Job Management** (Orange)
   - List all jobs
   - Filter by type and status
   - Delete jobs

---

## 🚀 How to Test an Endpoint

### Example: Generate a UI

1. **Expand the endpoint** - Click on `POST /api/v1/ui/generate`

2. **Click "Try it out"** - This makes the form editable

3. **Fill in the request body**:
   ```json
   {
     "agent_description": "A travel planning assistant that helps users book flights and hotels",
     "agent_capabilities": "flight search, hotel booking, itinerary planning",
     "theme": "dark",
     "color_scheme": "blue"
   }
   ```

4. **Click "Execute"** - Sends the actual API request

5. **View the Response**:
   - **Status Code**: `202 Accepted`
   - **Response Body**:
     ```json
     {
       "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
       "status": "pending",
       "message": "UI generation job created",
       "output_name": "ui-abc12345"
     }
     ```

6. **Copy the job_id** - You'll need it for the next step!

---

## 📊 Complete Workflow in Swagger

### Step 1: Generate UI

1. `POST /api/v1/ui/generate`
2. Click "Try it out"
3. Enter your agent description
4. Execute
5. **Copy the `job_id` from response**

### Step 2: Check Status

1. `GET /api/v1/ui/job/{job_id}`
2. Click "Try it out"
3. Paste your `job_id` in the path parameter
4. Execute
5. Wait until `status` is `"completed"`

### Step 3: View Live Preview

1. Copy the `job_id`
2. Open in browser: `http://localhost:5080/api/v1/ui/preview/{job_id}`
3. See your generated UI live!

### Step 4: Download Files (Optional)

1. `GET /api/v1/ui/bundle/{job_id}`
2. Click "Try it out"
3. Paste your `job_id`
4. Execute
5. Get all HTML/CSS/JS files in JSON format

---

## 🤖 Generate an AI Agent via Swagger

### Step 1: Create Agent

1. `POST /api/v1/agent/generate`
2. Click "Try it out"
3. Enter request body:
   ```json
   {
     "idea": "A restaurant booking agent that finds tables and makes reservations",
     "name": "Restaurant Booker"
   }
   ```
4. Execute
5. Copy the `job_id`

### Step 2: Check Status

1. `GET /api/v1/agent/job/{job_id}`
2. Paste your `job_id`
3. Execute
4. Wait for `status: "completed"`

### Step 3: Download Agent Code

1. `GET /api/v1/agent/bundle/{job_id}`
2. Paste your `job_id`
3. Execute
4. Get complete agent code bundle (main.py, agents.py, tasks.py, etc.)

---

## 💡 Pro Tips

### 1. **Use Example Values**
Swagger shows example values for all fields. Click "Example Value" to auto-fill!

### 2. **View Schemas**
Click on "Model" to see the full JSON schema with all properties.

### 3. **Response Codes**
- `200 OK` - Request successful
- `202 Accepted` - Job created (async operation)
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found

### 4. **Copy curl Commands**
After executing, Swagger shows the equivalent curl command:
```bash
curl -X POST "http://localhost:5080/api/v1/ui/generate" \
  -H "Content-Type: application/json" \
  -d '{"agent_description":"..."}'
```

### 5. **Test Different Themes**
Try generating UIs with different combinations:
- **Themes**: `dark`, `light`
- **Layouts**: `compact`, `standard`
- **Color Schemes**: `blue`, `green`, `red`, `purple`, `orange`

---

## 🔍 Common Workflows

### Workflow 1: Quick UI Test

```
1. POST /api/v1/ui/generate
   → Get job_id

2. GET /api/v1/ui/job/{job_id}
   → Poll until completed

3. Open browser: /api/v1/ui/preview/{job_id}
   → See live UI!
```

### Workflow 2: Compare Multiple UIs

```
1. Generate 3 different UIs with different themes
2. Use GET /api/v1/jobs?type=ui to list all
3. Preview each one to compare designs
```

### Workflow 3: Full Agent + UI Package

```
1. POST /api/v1/agent/generate
   → Generate agent code

2. POST /api/v1/ui/generate
   → Generate matching UI

3. Download both bundles
4. Deploy together!
```

---

## 🎯 Example Test Cases

### Test Case 1: E-commerce UI

```json
{
  "agent_description": "E-commerce shopping assistant with product recommendations",
  "agent_capabilities": "product search, cart management, checkout, personalized recommendations",
  "theme": "light",
  "color_scheme": "blue"
}
```

### Test Case 2: Healthcare Chatbot

```json
{
  "agent_description": "Healthcare assistant that helps users understand symptoms and find doctors",
  "agent_capabilities": "symptom analysis, doctor search, appointment booking, medication reminders",
  "theme": "light",
  "color_scheme": "green",
  "custom_design": "Clean medical interface with calm colors and trust-building design"
}
```

### Test Case 3: Crypto Trading Dashboard

```json
{
  "agent_description": "Cryptocurrency trading assistant with real-time analysis",
  "agent_capabilities": "price alerts, portfolio tracking, market analysis, trading signals",
  "theme": "dark",
  "color_scheme": "green",
  "custom_design": "Cyberpunk aesthetic with neon green accents, dark backgrounds, and animated price tickers"
}
```

---

## 🐛 Troubleshooting

### Issue: "Failed to fetch"
**Solution**: Make sure the API server is running on port 5080

### Issue: Job status stuck on "pending"
**Solution**: 
- Check server logs for errors
- Verify GEMINI_API_KEY is set in .env
- Generation can take 1-3 minutes

### Issue: Can't see preview
**Solution**:
- Ensure job status is "completed"
- Open preview URL in new tab
- Check that files were actually generated

---

## 📚 Additional Resources

- **Full API Documentation**: `/API_DOCUMENTATION.md`
- **Quick Start Guide**: `/API_QUICKSTART.md`
- **Frontend Example**: Open `/frontend_example.html` in browser

---

## 🎉 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements_api_server.txt

# 2. Start server
python api_server.py

# 3. Open Swagger UI
open http://localhost:5080/api/docs

# 4. Test health endpoint
curl http://localhost:5080/health
```

---

**Pro Tip**: Keep Swagger UI open in one tab and the live preview in another tab for instant feedback!

**Happy Testing!** 🚀
