"""
AIA Interface API Server
Provides REST API endpoints for UI/UX and AI Agent generation.
"""
import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from flasgger import Swagger, swag_from
from dotenv import load_dotenv
import threading
import queue
from dataclasses import dataclass, asdict

# Load environment
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ui_generator_crew import ui_generator_crew
from ai_agent_generator.agent_generator_crew import agent_generator_crew
from utils.environment_validator import EnvironmentValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "AIA Interface API",
        "description": "REST API for AI Agent and UI/UX Generation System. Generate complete UI interfaces and AI agent code bundles through simple API calls.",
        "version": "1.0.0",
        "contact": {
            "name": "AIA Interface",
            "url": "https://github.com/yourusername/aia-interface"
        }
    },
    "host": "localhost:5080",
    "basePath": "/",
    "schemes": ["http"],
    "tags": [
        {
            "name": "System",
            "description": "Health checks and system validation"
        },
        {
            "name": "UI Generator",
            "description": "Generate UI/UX interfaces for AI agents"
        },
        {
            "name": "Agent Generator",
            "description": "Generate AI agent code bundles"
        },
        {
            "name": "Job Management",
            "description": "Manage and track generation jobs"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Configuration
OUTPUT_DIR = Path("./generated_ui")
AGENT_OUTPUT_DIR = Path("./generated_agents")
OUTPUT_DIR.mkdir(exist_ok=True)
AGENT_OUTPUT_DIR.mkdir(exist_ok=True)

# In-memory job store (use Redis/database in production)
jobs: Dict[str, Dict[str, Any]] = {}

# In-memory log store for real-time streaming
job_logs: Dict[str, queue.Queue] = {}
job_log_history: Dict[str, List[str]] = {}


@dataclass
class GenerationJob:
    """Represents a generation job."""
    job_id: str
    job_type: str  # 'ui' or 'agent'
    status: str  # 'pending', 'processing', 'completed', 'failed'
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_path: Optional[str] = None
    files: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


def create_job(job_type: str, metadata: Dict[str, Any] = None) -> str:
    """Create a new generation job."""
    job_id = str(uuid.uuid4())
    job = GenerationJob(
        job_id=job_id,
        job_type=job_type,
        status='pending',
        created_at=datetime.now().isoformat(),
        metadata=metadata or {}
    )
    jobs[job_id] = asdict(job)
    job_logs[job_id] = queue.Queue()
    job_log_history[job_id] = []
    logger.info(f"Created job {job_id} of type {job_type}")
    return job_id


def update_job(job_id: str, **kwargs):
    """Update job status and data."""
    if job_id in jobs:
        jobs[job_id].update(kwargs)
        logger.info(f"Updated job {job_id}: {kwargs}")


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve job by ID."""
    return jobs.get(job_id)


def log_to_job(job_id: str, message: str, level: str = "INFO"):
    """Add a log message to a job's log queue."""
    if job_id in job_logs:
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        job_log_history[job_id].append(log_entry)
        try:
            job_logs[job_id].put_nowait(log_entry)
        except queue.Full:
            pass  # Queue is full, skip this message


# ============================================================================
# HEALTH & SYSTEM ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    tags:
      - System
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            timestamp:
              type: string
              example: "2025-10-13T16:00:00"
            version:
              type: string
              example: "1.0.0"
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/v1/validate', methods=['GET'])
def validate_environment():
    """
    Validate Environment Configuration
    ---
    tags:
      - System
    responses:
      200:
        description: Environment validation result
        schema:
          type: object
          properties:
            valid:
              type: boolean
            api_key:
              type: object
              properties:
                valid:
                  type: boolean
                message:
                  type: string
            dependencies:
              type: object
              properties:
                valid:
                  type: boolean
                message:
                  type: string
                missing:
                  type: array
                  items:
                    type: string
    """
    try:
        # Check API key
        api_key_ok, api_key_msg = EnvironmentValidator.validate_gemini_api_key()
        
        # Check dependencies
        deps_ok, deps_msg, missing = EnvironmentValidator.check_dependencies()
        
        return jsonify({
            'valid': api_key_ok and deps_ok,
            'api_key': {
                'valid': api_key_ok,
                'message': api_key_msg
            },
            'dependencies': {
                'valid': deps_ok,
                'message': deps_msg,
                'missing': missing if not deps_ok else []
            }
        })
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# UI GENERATOR ENDPOINTS
# ============================================================================

@app.route('/api/v1/ui/generate', methods=['POST'])
def generate_ui():
    """
    Generate UI/UX Interface
    ---
    tags:
      - UI Generator
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - agent_description
            - agent_capabilities
          properties:
            agent_description:
              type: string
              example: "A helpful travel planning assistant that helps users book flights and hotels"
              description: Description of the AI agent
            agent_capabilities:
              type: string
              example: "flight search, hotel booking, itinerary planning, price comparison"
              description: Comma-separated list of agent capabilities
            theme:
              type: string
              enum: [dark, light]
              default: dark
              description: UI theme
            layout:
              type: string
              enum: [compact, standard]
              default: compact
              description: Layout style
            color_scheme:
              type: string
              enum: [blue, green, red, purple, orange]
              default: blue
              description: Primary color scheme
            custom_design:
              type: string
              example: "Modern minimalist design with lots of white space"
              description: Additional design requirements
            output_name:
              type: string
              example: "travel-assistant-ui"
              description: Name for output directory (auto-generated if not provided)
    responses:
      202:
        description: UI generation job created successfully
        schema:
          type: object
          properties:
            job_id:
              type: string
              example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            status:
              type: string
              example: "pending"
            message:
              type: string
              example: "UI generation job created"
            output_name:
              type: string
              example: "travel-assistant-ui"
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            error:
              type: string
              example: "agent_description is required"
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('agent_description'):
            return jsonify({'error': 'agent_description is required'}), 400
        
        if not data.get('agent_capabilities'):
            return jsonify({'error': 'agent_capabilities is required'}), 400
        
        # Generate output name if not provided
        output_name = data.get('output_name') or f"ui-{uuid.uuid4().hex[:8]}"
        
        # Create job
        job_id = create_job('ui', metadata=data)
        
        # Start generation in background thread
        thread = threading.Thread(
            target=_run_ui_generation,
            args=(job_id, data, output_name)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'UI generation job created',
            'output_name': output_name
        }), 202
        
    except Exception as e:
        logger.error(f"UI generation error: {e}")
        return jsonify({'error': str(e)}), 500


def _run_ui_generation(job_id: str, params: Dict[str, Any], output_name: str):
    """Run UI generation in background."""
    try:
        update_job(job_id, status='processing')
        log_to_job(job_id, "Starting UI generation...")
        
        # Prepare inputs
        inputs = {
            "agent_description": params['agent_description'],
            "agent_capabilities": params['agent_capabilities'],
            "agent_api": params.get('agent_api', 'No specific API mentioned'),
            "user_preferences": f"Theme: {params.get('theme', 'dark')}, Layout: {params.get('layout', 'compact')}, Color Scheme: {params.get('color_scheme', 'blue')}, Custom Design: {params.get('custom_design', 'None')}",
            "theme": params.get('theme', 'dark'),
            "layout": params.get('layout', 'compact'),
            "color_scheme": params.get('color_scheme', 'blue'),
            "custom_design": params.get('custom_design', ''),
            "output_name": output_name,
            "output_dir": str(OUTPUT_DIR)
        }
        
        logger.info(f"Job {job_id}: Starting UI generation with inputs: {inputs}")
        log_to_job(job_id, f"Agent Description: {params['agent_description']}")
        log_to_job(job_id, f"Agent Capabilities: {params['agent_capabilities']}")
        log_to_job(job_id, f"Theme: {params.get('theme', 'dark')}, Color: {params.get('color_scheme', 'blue')}")
        log_to_job(job_id, "Initializing CrewAI agents...")
        
        # Run crew
        log_to_job(job_id, "Running UI generation crew...")
        result = ui_generator_crew.kickoff(inputs=inputs)
        log_to_job(job_id, "Crew execution completed")
        
        # Extract generated files
        output_path = OUTPUT_DIR / output_name
        files = []
        
        if output_path.exists():
            for file in output_path.iterdir():
                if file.is_file():
                    files.append(file.name)
                    log_to_job(job_id, f"Generated file: {file.name}")
        
        logger.info(f"Job {job_id}: Generated files: {files}")
        log_to_job(job_id, f"Total files generated: {len(files)}")
        log_to_job(job_id, "UI generation completed successfully!", "SUCCESS")
        
        # Update job
        update_job(
            job_id,
            status='completed',
            completed_at=datetime.now().isoformat(),
            output_path=str(output_path),
            files=files
        )
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        log_to_job(job_id, f"Error: {str(e)}", "ERROR")
        update_job(
            job_id,
            status='failed',
            completed_at=datetime.now().isoformat(),
            error=str(e)
        )


@app.route('/api/v1/ui/job/<job_id>', methods=['GET'])
def get_ui_job_status(job_id: str):
    """
    Get UI Generation Job Status
    ---
    tags:
      - UI Generator
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: Job ID returned from /api/v1/ui/generate
        example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    responses:
      200:
        description: Job status retrieved successfully
        schema:
          type: object
          properties:
            job_id:
              type: string
            job_type:
              type: string
              example: "ui"
            status:
              type: string
              enum: [pending, processing, completed, failed]
            created_at:
              type: string
            completed_at:
              type: string
            output_path:
              type: string
            files:
              type: array
              items:
                type: string
            error:
              type: string
      404:
        description: Job not found
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)


@app.route('/api/v1/ui/file/<job_id>/<filename>', methods=['GET'])
def get_ui_file(job_id: str, filename: str):
    """
    Download a specific generated UI file.
    
    Returns the file content with appropriate MIME type.
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    output_path = Path(job['output_path'])
    file_path = output_path / filename
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    # Determine MIME type
    mime_types = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json'
    }
    mime_type = mime_types.get(file_path.suffix, 'text/plain')
    
    return send_file(file_path, mimetype=mime_type)


@app.route('/api/v1/ui/bundle/<job_id>', methods=['GET'])
def get_ui_bundle(job_id: str):
    """
    Get all UI files as a JSON bundle.
    
    Response:
    {
        "job_id": "uuid",
        "files": {
            "index.html": "<html>...</html>",
            "styles.css": "body { ... }",
            "app.js": "document.addEventListener..."
        }
    }
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    output_path = Path(job['output_path'])
    files_content = {}
    
    for filename in job.get('files', []):
        file_path = output_path / filename
        if file_path.exists():
            files_content[filename] = file_path.read_text(encoding='utf-8')
    
    return jsonify({
        'job_id': job_id,
        'files': files_content,
        'metadata': job.get('metadata', {})
    })


@app.route('/api/v1/ui/preview/<job_id>', methods=['GET'])
def preview_ui(job_id: str):
    """
    Serve the generated UI for live preview.
    Serves index.html from the job's output directory.
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    output_path = Path(job['output_path'])
    return send_from_directory(output_path, 'index.html')


@app.route('/api/v1/ui/preview/<job_id>/<path:filepath>', methods=['GET'])
def preview_ui_asset(job_id: str, filepath: str):
    """
    Serve UI assets (CSS, JS) for live preview.
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'UI not ready yet'}), 400
    
    output_path = Path(job['output_path'])
    return send_from_directory(output_path, filepath)


# ============================================================================
# AI AGENT GENERATOR ENDPOINTS
# ============================================================================

@app.route('/api/v1/agent/generate', methods=['POST'])
def generate_agent():
    """
    Generate AI Agent Code Bundle
    ---
    tags:
      - Agent Generator
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - idea
          properties:
            idea:
              type: string
              example: "A customer support chatbot that handles inquiries, creates tickets, and escalates to humans"
              description: Description of the agent's purpose and capabilities
            name:
              type: string
              example: "Support Bot"
              description: Agent name (auto-generated if not provided)
            verify:
              type: boolean
              default: false
              description: Run verification after generation
    responses:
      202:
        description: Agent generation job created successfully
        schema:
          type: object
          properties:
            job_id:
              type: string
              example: "b2c3d4e5-f6a7-8901-bcde-f2345678901a"
            status:
              type: string
              example: "pending"
            message:
              type: string
            agent_name:
              type: string
      400:
        description: Invalid request
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('idea'):
            return jsonify({'error': 'idea is required'}), 400
        
        # Generate name if not provided
        agent_name = data.get('name') or f"agent-{uuid.uuid4().hex[:8]}"
        
        # Create job
        job_id = create_job('agent', metadata=data)
        
        # Start generation in background thread
        thread = threading.Thread(
            target=_run_agent_generation,
            args=(job_id, data, agent_name)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'Agent generation job created',
            'agent_name': agent_name
        }), 202
        
    except Exception as e:
        logger.error(f"Agent generation error: {e}")
        return jsonify({'error': str(e)}), 500


def _run_agent_generation(job_id: str, params: Dict[str, Any], agent_name: str):
    """Run agent generation in background."""
    try:
        update_job(job_id, status='processing')
        log_to_job(job_id, "Starting AI agent generation...")
        
        # Prepare inputs
        serper_available = bool(os.getenv("SERPER_API_KEY"))
        
        inputs = {
            "idea": params['idea'],
            "agent_name": agent_name,
            "output_dir": str(AGENT_OUTPUT_DIR),
            "output_root": str(AGENT_OUTPUT_DIR / agent_name.lower().replace(' ', '-')),
            "serper_available": str(serper_available).lower()
        }
        
        logger.info(f"Job {job_id}: Starting agent generation with inputs: {inputs}")
        log_to_job(job_id, f"Agent Idea: {params['idea']}")
        log_to_job(job_id, f"Agent Name: {agent_name}")
        log_to_job(job_id, f"Serper API {'Available' if serper_available else 'Not Available'}")
        log_to_job(job_id, "Initializing CrewAI agents...")
        
        # Run crew
        log_to_job(job_id, "Running agent generation crew...")
        result = agent_generator_crew.kickoff(inputs=inputs)
        log_to_job(job_id, "Crew execution completed")
        
        # Extract generated files
        output_path = AGENT_OUTPUT_DIR / agent_name.lower().replace(' ', '-')
        files = []
        
        if output_path.exists():
            for file in output_path.rglob('*'):
                if file.is_file():
                    files.append(str(file.relative_to(output_path)))
                    log_to_job(job_id, f"Generated file: {file.name}")
        
        logger.info(f"Job {job_id}: Generated files: {files}")
        log_to_job(job_id, f"Total files generated: {len(files)}")
        log_to_job(job_id, "Agent generation completed successfully!", "SUCCESS")
        
        # Update job
        update_job(
            job_id,
            status='completed',
            completed_at=datetime.now().isoformat(),
            output_path=str(output_path),
            files=files
        )
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        log_to_job(job_id, f"Error: {str(e)}", "ERROR")
        update_job(
            job_id,
            status='failed',
            completed_at=datetime.now().isoformat(),
            error=str(e)
        )


@app.route('/api/v1/agent/job/<job_id>', methods=['GET'])
def get_agent_job_status(job_id: str):
    """Get agent generation job status."""
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)


@app.route('/api/v1/agent/bundle/<job_id>', methods=['GET'])
def get_agent_bundle(job_id: str):
    """
    Get all agent files as a JSON bundle.
    
    Response:
    {
        "job_id": "uuid",
        "files": {
            "main.py": "...",
            "agents.py": "...",
            "tasks.py": "...",
            ...
        }
    }
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    output_path = Path(job['output_path'])
    files_content = {}
    
    for filename in job.get('files', []):
        file_path = output_path / filename
        if file_path.exists() and file_path.is_file():
            try:
                files_content[filename] = file_path.read_text(encoding='utf-8')
            except Exception as e:
                logger.warning(f"Could not read {filename}: {e}")
    
    return jsonify({
        'job_id': job_id,
        'files': files_content,
        'metadata': job.get('metadata', {})
    })


# ============================================================================
# LIST & MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/v1/jobs', methods=['GET'])
def list_jobs():
    """
    List All Jobs
    ---
    tags:
      - Job Management
    parameters:
      - name: type
        in: query
        type: string
        enum: [ui, agent]
        description: Filter by job type
      - name: status
        in: query
        type: string
        enum: [pending, processing, completed, failed]
        description: Filter by job status
      - name: limit
        in: query
        type: integer
        default: 50
        description: Maximum number of results
    responses:
      200:
        description: List of jobs
        schema:
          type: object
          properties:
            total:
              type: integer
            jobs:
              type: array
              items:
                type: object
    """
    job_type = request.args.get('type')
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    
    filtered_jobs = list(jobs.values())
    
    if job_type:
        filtered_jobs = [j for j in filtered_jobs if j['job_type'] == job_type]
    
    if status:
        filtered_jobs = [j for j in filtered_jobs if j['status'] == status]
    
    # Sort by created_at descending
    filtered_jobs.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'total': len(filtered_jobs),
        'jobs': filtered_jobs[:limit]
    })


@app.route('/api/v1/job/<job_id>', methods=['DELETE'])
def delete_job(job_id: str):
    """Delete a job and its outputs."""
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Delete output files if they exist
    if job.get('output_path'):
        output_path = Path(job['output_path'])
        if output_path.exists():
            import shutil
            shutil.rmtree(output_path)
            logger.info(f"Deleted output directory: {output_path}")
    
    # Remove job from store
    del jobs[job_id]
    
    return jsonify({'message': 'Job deleted successfully'})


# ============================================================================
# LOG STREAMING ENDPOINTS (SSE)
# ============================================================================

@app.route('/api/v1/job/<job_id>/logs/stream', methods=['GET'])
def stream_job_logs(job_id: str):
    """
    Stream Job Logs (Server-Sent Events)
    ---
    tags:
      - Job Management
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: Job ID to stream logs for
    responses:
      200:
        description: SSE stream of job logs
        content:
          text/event-stream:
            schema:
              type: string
      404:
        description: Job not found
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    def generate():
        """Generate SSE events from job logs."""
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'job_id': job_id, 'status': job['status']})}\n\n"
        
        # Send log history first
        if job_id in job_log_history:
            for log_entry in job_log_history[job_id]:
                yield f"data: {json.dumps({'type': 'log', 'message': log_entry})}\n\n"
        
        # Stream new logs as they arrive
        if job_id in job_logs:
            log_queue = job_logs[job_id]
            
            while True:
                # Check if job is complete
                current_job = get_job(job_id)
                if current_job and current_job['status'] in ['completed', 'failed']:
                    # Send final status
                    yield f"data: {json.dumps({'type': 'status', 'status': current_job['status'], 'final': True})}\n\n"
                    break
                
                try:
                    # Wait for new log with timeout
                    log_entry = log_queue.get(timeout=1)
                    yield f"data: {json.dumps({'type': 'log', 'message': log_entry})}\n\n"
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@app.route('/api/v1/job/<job_id>/logs', methods=['GET'])
def get_job_logs(job_id: str):
    """
    Get Job Logs (Full History)
    ---
    tags:
      - Job Management
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: Job ID to get logs for
    responses:
      200:
        description: Complete log history
        schema:
          type: object
          properties:
            job_id:
              type: string
            status:
              type: string
            logs:
              type: array
              items:
                type: string
      404:
        description: Job not found
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    logs = job_log_history.get(job_id, [])
    
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'logs': logs,
        'total_logs': len(logs)
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Validate environment on startup
    print("\n🔍 Validating environment...")
    try:
        EnvironmentValidator.run_full_validation()
        print("✅ Environment validation passed\n")
    except Exception as e:
        print(f"⚠️  Warning: {e}\n")
    
    # Start server
    port = int(os.getenv('API_PORT', 5080))
    debug = os.getenv('API_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting AIA Interface API Server")
    print(f"📍 Host: 0.0.0.0")
    print(f"🔌 Port: {port}")
    print(f"🌐 Base URL: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/api/docs")
    print(f"\n{'='*60}\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
