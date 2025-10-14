# AIA Interface API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:5000`

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [UI Generator Endpoints](#ui-generator-endpoints)
4. [Agent Generator Endpoints](#agent-generator-endpoints)
5. [Job Management](#job-management)
6. [Error Handling](#error-handling)
7. [Frontend Integration Examples](#frontend-integration-examples)

---

## 🚀 Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements_api_server.txt

# Set up environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Start server
python api_server.py
```

Server will start on `http://localhost:5000`

### Environment Variables

```bash
# Required
GEMINI_API_KEY=AIzaSy...

# Optional
SERPER_API_KEY=...  # For web search capabilities
API_PORT=5000       # Server port (default: 5000)
API_DEBUG=false     # Debug mode (default: false)
```

---

## 🔐 Authentication

Currently, the API is open (no authentication required for v1.0).

For production, consider adding API keys or OAuth2.

---

## 🎨 UI Generator Endpoints

### POST `/api/v1/ui/generate`

Generate UI/UX files based on agent description.

**Request Body:**
```json
{
  "agent_description": "A helpful travel planning assistant that helps users book flights and hotels",
  "agent_capabilities": "flight search, hotel booking, itinerary planning, price comparison",
  "theme": "dark",
  "layout": "compact",
  "color_scheme": "blue",
  "custom_design": "Modern minimalist design with lots of white space",
  "output_name": "travel-assistant-ui"
}
```

**Required Fields:**
- `agent_description` (string): Description of the AI agent
- `agent_capabilities` (string): Comma-separated capabilities

**Optional Fields:**
- `theme` (string): `"light"` or `"dark"` (default: `"dark"`)
- `layout` (string): `"compact"` or `"standard"` (default: `"compact"`)
- `color_scheme` (string): `"blue"`, `"green"`, `"red"`, `"purple"`, `"orange"` (default: `"blue"`)
- `custom_design` (string): Additional design requirements
- `output_name` (string): Name for output directory (auto-generated if not provided)

**Response (202 Accepted):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "UI generation job created",
  "output_name": "travel-assistant-ui"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/ui/generate \
  -H "Content-Type: application/json" \
  -d '{
    "agent_description": "Customer support chatbot",
    "agent_capabilities": "answer questions, create tickets",
    "theme": "dark"
  }'
```

---

### GET `/api/v1/ui/job/{job_id}`

Check UI generation job status.

**Response (200 OK):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "job_type": "ui",
  "status": "completed",
  "created_at": "2025-10-13T15:30:00",
  "completed_at": "2025-10-13T15:32:30",
  "output_path": "/path/to/generated_ui/travel-assistant-ui",
  "files": ["index.html", "styles.css", "app.js"],
  "metadata": {
    "agent_description": "...",
    "theme": "dark"
  }
}
```

**Status Values:**
- `pending`: Job created, waiting to start
- `processing`: Currently generating
- `completed`: Successfully completed
- `failed`: Generation failed (check `error` field)

**Example:**
```bash
curl http://localhost:5000/api/v1/ui/job/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

### GET `/api/v1/ui/file/{job_id}/{filename}`

Download a specific generated file.

**Parameters:**
- `job_id`: Job identifier
- `filename`: `index.html`, `styles.css`, or `app.js`

**Response (200 OK):**
Returns file content with appropriate MIME type.

**Example:**
```bash
curl http://localhost:5000/api/v1/ui/file/a1b2c3d4/index.html > index.html
```

---

### GET `/api/v1/ui/bundle/{job_id}`

Get all UI files in a single JSON response.

**Response (200 OK):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "files": {
    "index.html": "<!DOCTYPE html>...",
    "styles.css": "body { ... }",
    "app.js": "document.addEventListener..."
  },
  "metadata": {
    "agent_description": "...",
    "theme": "dark"
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/v1/ui/bundle/a1b2c3d4
```

---

### GET `/api/v1/ui/preview/{job_id}`

Live preview of generated UI in browser.

**Response (200 OK):**
Serves the `index.html` file with proper asset references.

**Usage:**
Open `http://localhost:5000/api/v1/ui/preview/{job_id}` in your browser to see the live UI.

**Example:**
```
http://localhost:5000/api/v1/ui/preview/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 🤖 Agent Generator Endpoints

### POST `/api/v1/agent/generate`

Generate AI Agent code bundle.

**Request Body:**
```json
{
  "idea": "A customer support chatbot that handles inquiries, creates tickets, and escalates to humans",
  "name": "Support Bot",
  "verify": true
}
```

**Required Fields:**
- `idea` (string): Description of the agent's purpose

**Optional Fields:**
- `name` (string): Agent name (auto-generated if not provided)
- `verify` (boolean): Run verification after generation (default: false)

**Response (202 Accepted):**
```json
{
  "job_id": "b2c3d4e5-f6a7-8901-bcde-f2345678901a",
  "status": "pending",
  "message": "Agent generation job created",
  "agent_name": "Support Bot"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/agent/generate \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A restaurant booking agent",
    "name": "Restaurant Booker"
  }'
```

---

### GET `/api/v1/agent/job/{job_id}`

Check agent generation job status.

**Response (200 OK):**
```json
{
  "job_id": "b2c3d4e5-f6a7-8901-bcde-f2345678901a",
  "job_type": "agent",
  "status": "completed",
  "created_at": "2025-10-13T15:30:00",
  "completed_at": "2025-10-13T15:35:45",
  "output_path": "/path/to/generated_agents/support-bot",
  "files": [
    "main.py",
    "agents.py",
    "tasks.py",
    "crew.py",
    "README.md",
    "requirements.txt"
  ]
}
```

---

### GET `/api/v1/agent/bundle/{job_id}`

Get all agent files in a single JSON response.

**Response (200 OK):**
```json
{
  "job_id": "b2c3d4e5-f6a7-8901-bcde-f2345678901a",
  "files": {
    "main.py": "#!/usr/bin/env python...",
    "agents.py": "from crewai import Agent...",
    "tasks.py": "from crewai import Task...",
    "crew.py": "from crewai import Crew...",
    "README.md": "# Support Bot...",
    "requirements.txt": "crewai==0.193.2..."
  },
  "metadata": {
    "idea": "A customer support chatbot...",
    "name": "Support Bot"
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/v1/agent/bundle/b2c3d4e5 > agent_bundle.json
```

---

## 📊 Job Management

### GET `/api/v1/jobs`

List all jobs with optional filtering.

**Query Parameters:**
- `type` (optional): Filter by `"ui"` or `"agent"`
- `status` (optional): Filter by `"pending"`, `"processing"`, `"completed"`, `"failed"`
- `limit` (optional): Max results (default: 50)

**Response (200 OK):**
```json
{
  "total": 15,
  "jobs": [
    {
      "job_id": "...",
      "job_type": "ui",
      "status": "completed",
      "created_at": "2025-10-13T15:30:00"
    }
  ]
}
```

**Examples:**
```bash
# All jobs
curl http://localhost:5000/api/v1/jobs

# Only UI jobs
curl http://localhost:5000/api/v1/jobs?type=ui

# Only completed jobs
curl http://localhost:5000/api/v1/jobs?status=completed

# UI jobs that are completed
curl http://localhost:5000/api/v1/jobs?type=ui&status=completed&limit=10
```

---

### DELETE `/api/v1/job/{job_id}`

Delete a job and its generated files.

**Response (200 OK):**
```json
{
  "message": "Job deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/v1/job/a1b2c3d4
```

---

## 🏥 System Endpoints

### GET `/health`

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-13T15:30:00",
  "version": "1.0.0"
}
```

---

### GET `/api/v1/validate`

Validate environment configuration.

**Response (200 OK):**
```json
{
  "valid": true,
  "api_key": {
    "valid": true,
    "message": "✅ GEMINI_API_KEY found"
  },
  "dependencies": {
    "valid": true,
    "message": "✅ All dependencies installed",
    "missing": []
  }
}
```

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `202 Accepted`: Job created, processing asynchronously
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Errors

**Missing Required Field:**
```json
{
  "error": "agent_description is required"
}
```

**Job Not Found:**
```json
{
  "error": "Job not found"
}
```

**Job Not Completed:**
```json
{
  "error": "Job not completed yet"
}
```

---

## 💻 Frontend Integration Examples

### React Example

```javascript
import React, { useState, useEffect } from 'react';

const UIGenerator = () => {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [previewUrl, setPreviewUrl] = useState(null);

  const generateUI = async () => {
    const response = await fetch('http://localhost:5000/api/v1/ui/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_description: 'Travel planning assistant',
        agent_capabilities: 'flight search, hotel booking',
        theme: 'dark'
      })
    });
    
    const data = await response.json();
    setJobId(data.job_id);
    setStatus('pending');
  };

  useEffect(() => {
    if (!jobId) return;

    const checkStatus = async () => {
      const response = await fetch(`http://localhost:5000/api/v1/ui/job/${jobId}`);
      const data = await response.json();
      
      setStatus(data.status);
      
      if (data.status === 'completed') {
        setPreviewUrl(`http://localhost:5000/api/v1/ui/preview/${jobId}`);
      }
    };

    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div>
      <button onClick={generateUI}>Generate UI</button>
      <p>Status: {status}</p>
      {previewUrl && (
        <iframe src={previewUrl} width="100%" height="600px" />
      )}
    </div>
  );
};
```

### Plain JavaScript / Fetch API

```javascript
// Generate UI
async function generateUI() {
  const response = await fetch('http://localhost:5000/api/v1/ui/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_description: 'Customer support chatbot',
      agent_capabilities: 'answer questions, create tickets',
      theme: 'dark',
      color_scheme: 'blue'
    })
  });
  
  const { job_id } = await response.json();
  return job_id;
}

// Poll for completion
async function pollJobStatus(jobId) {
  const checkStatus = async () => {
    const response = await fetch(`http://localhost:5000/api/v1/ui/job/${jobId}`);
    const job = await response.json();
    
    if (job.status === 'completed') {
      console.log('✅ Generation complete!');
      console.log('Preview:', `http://localhost:5000/api/v1/ui/preview/${jobId}`);
      return job;
    } else if (job.status === 'failed') {
      console.error('❌ Generation failed:', job.error);
      return null;
    } else {
      console.log(`⏳ Status: ${job.status}...`);
      setTimeout(() => checkStatus(), 2000);
    }
  };
  
  return checkStatus();
}

// Usage
const jobId = await generateUI();
const result = await pollJobStatus(jobId);
```

### Python Client

```python
import requests
import time

API_BASE = 'http://localhost:5000'

def generate_ui(description, capabilities, theme='dark'):
    """Generate UI and return job ID."""
    response = requests.post(
        f'{API_BASE}/api/v1/ui/generate',
        json={
            'agent_description': description,
            'agent_capabilities': capabilities,
            'theme': theme
        }
    )
    return response.json()['job_id']

def wait_for_completion(job_id, max_wait=300):
    """Poll job status until completion."""
    start = time.time()
    
    while time.time() - start < max_wait:
        response = requests.get(f'{API_BASE}/api/v1/ui/job/{job_id}')
        job = response.json()
        
        if job['status'] == 'completed':
            return job
        elif job['status'] == 'failed':
            raise Exception(f"Generation failed: {job.get('error')}")
        
        print(f"Status: {job['status']}...")
        time.sleep(2)
    
    raise TimeoutError('Job did not complete in time')

def download_bundle(job_id):
    """Download all generated files."""
    response = requests.get(f'{API_BASE}/api/v1/ui/bundle/{job_id}')
    return response.json()['files']

# Usage
job_id = generate_ui(
    'Travel planning assistant',
    'flight search, hotel booking, itinerary planning'
)

job = wait_for_completion(job_id)
files = download_bundle(job_id)

# Save files locally
for filename, content in files.items():
    with open(filename, 'w') as f:
        f.write(content)
```

---

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (production-ready)
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements_api_server.txt .
RUN pip install -r requirements_api_server.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

---

## 📝 Notes

1. **Async Jobs**: UI and Agent generation run asynchronously. Poll the job endpoint to check status.

2. **File Storage**: Generated files are stored locally in `generated_ui/` and `generated_agents/`. Consider cloud storage for production.

3. **Rate Limiting**: Not implemented in v1.0. Add rate limiting for production.

4. **CORS**: Enabled for all origins. Restrict in production.

5. **Persistence**: Jobs are stored in memory. Use Redis or a database for production.

---

**API Version:** 1.0.0  
**Last Updated:** 2025-10-13  
**Support:** See project README
