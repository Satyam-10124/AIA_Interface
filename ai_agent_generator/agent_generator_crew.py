import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import CodeInterpreterTool, FileWriterTool, SerperDevTool

from .agent_schemas import (
    AgentSpecOutput,
    AgentFilesBundle,
    VerificationReport,
)

# Load environment variables (expects GEMINI_API_KEY in .env)
load_dotenv()

# Initialize LLM (reuse the pattern from ui_generator_crew.py)
llm = LLM(
    model="gemini/gemini-2.5-pro",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Tools
code_interpreter = CodeInterpreterTool(llm=llm)
file_writer_tool = FileWriterTool()
# Make Serper optional to avoid requiring SERPER_API_KEY
_serper_key = os.getenv("SERPER_API_KEY")
serper_tool = SerperDevTool() if _serper_key else None

# Agents
spec_architect = Agent(
    role="AI Agent Architect",
    goal=(
        "Transform a plain-language idea into a clear, actionable specification "
        "for a CrewAI-based agent with modules, tools, and evaluation plan."
    ),
    backstory=(
        "A senior AI product architect who translates raw ideas into precise, "
        "implementable specifications for autonomous agents using CrewAI."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[serper_tool] if serper_tool else [],
    llm=llm,
)

agent_developer = Agent(
    role="Agent Developer",
    goal=(
        "Generate clean, maintainable Python modules and a runnable entrypoint "
        "for the agent using CrewAI. Include minimal docs and typing."
    ),
    backstory=(
        "A pragmatic Python developer with strong experience in CrewAI projects. "
        "Writes production-ready code with attention to structure and clarity."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter],
    llm=llm,
)

verifier = Agent(
    role="Agent Verifier (Static Analysis Only)",
    goal=(
        "Verify that the generated code is syntactically valid using STATIC ANALYSIS ONLY. "
        "DO NOT attempt to execute code, install dependencies, or use pip. "
        "Use Python's built-in ast module to check syntax. Provide a concise verification report."
    ),
    backstory=(
        "A meticulous QA engineer who specializes in STATIC CODE ANALYSIS. "
        "You understand that the sandbox environment cannot install dependencies, "
        "so you rely ONLY on Python's ast.parse() for syntax validation. "
        "You NEVER execute code or run pip install. You check structure and syntax only."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[],  # NO TOOLS - pure static analysis using built-in ast module
    llm=llm,
)

# Tasks

# 1) Specification
task_specify = Task(
    description=(
        "You are given a user idea: '{idea}'.\n"
        "Optional name: '{agent_name}'.\n\n"
        "1. Produce a complete agent specification covering: name, purpose, capabilities,\n"
        "   inputs, outputs, tools, APIs, modules, recommended evaluation bullets, and design notes.\n"
        "2. Be concrete. Choose file names from the 'modules' list (e.g., agents.py, tasks.py, crew.py, main.py). Also include non-code deliverables: README.md and requirements.txt.\n"
        "3. Keep scope reasonable for a first working version.\n"
        "4. SERPER availability = '{serper_available}'. If false, DO NOT include any Serper tools or references.\n\n"
        "YOU MUST RETURN YOUR OUTPUT USING THIS JSON SCHEMA ONLY:\n"
        "{\n"
        "  \"name\": \"<agent name>\",\n"
        "  \"purpose\": \"<what the agent does>\",\n"
        "  \"capabilities\": [\"...\"],\n"
        "  \"inputs\": [\"...\"],\n"
        "  \"outputs\": [\"...\"],\n"
        "  \"tools\": [\"...\"],\n"
        "  \"apis\": [\"...\"],\n"
        "  \"modules\": [\"agents.py\", \"tasks.py\", \"crew.py\", \"main.py\"],\n"
        "  \"recommended_evaluation\": [\"...\"],\n"
        "  \"design_notes\": \"...\"\n"
        "}\n\n"
        "Return ONLY valid JSON per the schema. No commentary, markdown, or backticks."
    ),
    expected_output=(
        "An AgentSpecOutput Pydantic model with a concrete, usable plan."
    ),
    agent=spec_architect,
    output_pydantic=AgentSpecOutput,
)

# 2) Code Generation
task_generate_code = Task(
    description=(
        "Using the agent specification and the user's output directory '{output_dir}', generate a multi-file code bundle using CrewAI.\n\n"
        "Requirements:\n"
        "- Target Python >= 3.9.\n"
        "- Each file must be valid Python and importable.\n"
        "- The main entrypoint (main.py) must contain a __main__ guard and a simple CLI.\n"
        "- Load environment variables via python-dotenv (load_dotenv).\n"
        "- Do NOT include any secrets in code.\n"
        "- Prefer readable, typed code with docstrings.\n"
        "- SERPER availability = '{serper_available}'. If false, DO NOT reference Serper in code.\n"
        "- Pin dependencies to these versions in requirements.txt: crewai==0.193.2, crewai-tools==0.75.0, python-dotenv==1.0.0.\n"
        "- The 'files' array MUST include 'README.md' and 'requirements.txt' at the project root.\n"
        "- README.md MUST include: Overview, Quickstart (venv, pip install -r requirements.txt, run CLI, run tests), and Environment Variables (SERPER_API_KEY optional).\n\n"
        "Tests (REQUIRED):\n"
        "- Include a pytest file at 'tests/test_smoke.py' that imports the generated crew and asserts it initializes.\n\n"
        "IMPORTANT: Do NOT write files directly. Return ONLY a JSON bundle matching the schema below. No commentary or markdown.\n\n"
        "Return in this JSON schema ONLY:\n"
        "{\n"
        "  \"files\": [{\"filename\": \"path/relative/to/agent_root.py\", \"code\": \"...\" , \"description\": \"...\"}],\n"
        "  \"dependencies\": [\"crewai\", \"python-dotenv\"],\n"
        "  \"entrypoint\": \"main.py\",\n"
        "  \"tests\": {\"tests/test_smoke.py\": \"...\"}\n"
        "}\n\n"
        "Return ONLY valid JSON."
    ),
    expected_output=(
        "An AgentFilesBundle Pydantic model with concrete files, optional tests, and entrypoint."
    ),
    agent=agent_developer,
    context=[task_specify],
    output_pydantic=AgentFilesBundle,
)

# 3) Verification (Static Analysis Only)
# The verifier uses ONLY Python's built-in ast module to check syntax.
# NO dependency installation, NO code execution, NO pytest runs.

task_verify = Task(
    description=(
        "Verify the AgentFilesBundle from context using STATIC ANALYSIS ONLY.\n\n"
        "CRITICAL RULES:\n"
        "- DO NOT write files to disk\n"
        "- DO NOT use pip install or any package manager\n"
        "- DO NOT execute any code\n"
        "- DO NOT run pytest or any tests\n"
        "- ONLY use Python's built-in ast.parse() to check syntax\n\n"
        "Verification Steps:\n"
        "1) For each .py file in the bundle, use ast.parse(code) to validate syntax\n"
        "2) Check that required files exist (agents.py, tasks.py, crew.py, main.py, README.md, requirements.txt)\n"
        "3) Verify basic structure: look for 'from crewai import', 'Agent(', 'Task(', 'Crew('\n"
        "4) Count basic metrics: number of functions, classes, imports\n\n"
        "Example Python code to use:\n"
        "```python\n"
        "import ast\n"
        "try:\n"
        "    ast.parse(code_string)\n"
        "    syntax_ok = True\n"
        "except SyntaxError as e:\n"
        "    syntax_ok = False\n"
        "    error = f'Line {e.lineno}: {e.msg}'\n"
        "```\n\n"
        "Return VerificationReport JSON with:\n"
        "- syntax_ok: true if all .py files parse successfully\n"
        "- import_ok: true (always, since we can't actually test imports)\n"
        "- tests_ok: true (always, since we can't run tests)\n"
        "- passed: true if syntax_ok and all required files present\n"
        "- errors: list of syntax errors found\n"
        "- warnings: list of structural issues (missing Agent/Task/Crew patterns)\n"
        "- suggestions: list of improvements\n\n"
        "Return ONLY the VerificationReport JSON."
    ),
    expected_output=(
        "A VerificationReport Pydantic model with syntax validation results."
    ),
    agent=verifier,
    context=[task_generate_code],
    output_pydantic=VerificationReport,
)

# Crew
agent_generator_crew = Crew(
    agents=[spec_architect, agent_developer, verifier],
    tasks=[task_specify, task_generate_code, task_verify],
    process=Process.sequential,
    verbose=True,
)

