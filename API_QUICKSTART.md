# API Server Quick Start Guide

## 🚀 Start the Server

```bash
cd /Users/satyamsinghal/Desktop/Products/AIA_Interface

# 1. Install API server dependencies
pip install -r requirements_api_server.txt

# 2. Start the server
python api_server.py
```

**Server will start on:** `http://localhost:5080`

## 📚 Interactive API Documentation (Swagger UI)

**Open in your browser:** `http://localhost:5080/api/docs`

The Swagger UI provides:
- ✅ **Interactive testing** - Try all endpoints directly from the browser
- ✅ **Request/Response examples** - See exactly what to send
- ✅ **Schema validation** - Understand required vs optional fields
- ✅ **Live execution** - Generate UIs and agents with one click

---

## ✅ Test the API

### 1. Health Check
```bash
curl http://localhost:5080/health
```

### 2. Generate UI (Full Example)
```bash
curl -X POST http://localhost:5080/api/v1/ui/generate \
  -H "Content-Type: application/json" \
  -d '{
    "agent_description": "Customer support chatbot that helps users resolve issues",
    "agent_capabilities": "answer questions, create tickets, escalate to humans",
    "theme": "dark",
    "color_scheme": "blue"
  }'
```

**Response:**
```json
{
  "job_id": "abc123...",
  "status": "pending",
  "output_name": "ui-abc12345"
}
```

### 3. Check Job Status
```bash
# Replace {job_id} with the ID from step 2
curl http://localhost:5080/api/v1/ui/job/abc123...
```

### 4. View Live Preview
Open in browser:
```
http://localhost:5080/api/v1/ui/preview/abc123...
```

### 5. Download Files
```bash
# Get all files as JSON
curl http://localhost:5080/api/v1/ui/bundle/abc123... > ui_bundle.json

# Download specific file
curl http://localhost:5080/api/v1/ui/file/abc123.../index.html > index.html
```

---

## 🎨 Frontend Integration

### Open the Demo App
```bash
# In a new terminal, start a simple HTTP server
python3 -m http.server 8080

# Open in browser:
# http://localhost:8080/frontend_example.html
```

This provides a complete web interface for testing the API.

---

## 🤖 Generate AI Agent

```bash
curl -X POST http://localhost:5080/api/v1/agent/generate \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A restaurant booking agent that finds tables and makes reservations",
    "name": "Restaurant Booker"
  }'
```

**Check status:**
```bash
curl http://localhost:5080/api/v1/agent/job/{job_id}
```

**Download agent bundle:**
```bash
curl http://localhost:5080/api/v1/agent/bundle/{job_id} > agent_bundle.json
```

---

## 📊 List All Jobs

```bash
# All jobs
curl http://localhost:5080/api/v1/jobs

# Only UI jobs
curl "http://localhost:5080/api/v1/jobs?type=ui"

# Only completed jobs
curl "http://localhost:5080/api/v1/jobs?status=completed"
```

---

## 🔧 Advanced: Python Client Example

```python
import requests
import time

API_BASE = 'http://localhost:5080'

# Generate UI
response = requests.post(f'{API_BASE}/api/v1/ui/generate', json={
    'agent_description': 'Travel planning assistant',
    'agent_capabilities': 'flight search, hotel booking',
    'theme': 'dark'
})

job_id = response.json()['job_id']
print(f"Job created: {job_id}")

# Poll until complete
while True:
    job = requests.get(f'{API_BASE}/api/v1/ui/job/{job_id}').json()
    
    if job['status'] == 'completed':
        print(f"✅ Done! Preview: {API_BASE}/api/v1/ui/preview/{job_id}")
        break
    elif job['status'] == 'failed':
        print(f"❌ Failed: {job['error']}")
        break
    
    print(f"Status: {job['status']}...")
    time.sleep(2)

# Download files
bundle = requests.get(f'{API_BASE}/api/v1/ui/bundle/{job_id}').json()

for filename, content in bundle['files'].items():
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Saved {filename}")
```

---

## 📚 Full Documentation

See `API_DOCUMENTATION.md` for complete endpoint reference.

---

## 🎯 Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app

# Or with increased timeout for long-running jobs
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 api_server:app
```

---

## ⚡ Quick Commands Summary

```bash
# Start server
python api_server.py

# Generate UI
curl -X POST http://localhost:5000/api/v1/ui/generate \
  -H "Content-Type: application/json" \
  -d '{"agent_description":"...", "agent_capabilities":"..."}'

# Check status
curl http://localhost:5000/api/v1/ui/job/{job_id}

# Preview in browser
open http://localhost:5000/api/v1/ui/preview/{job_id}

# List all jobs
curl http://localhost:5000/api/v1/jobs
```

**That's it!** You now have a full REST API for generating UIs and AI agents. 🎉
