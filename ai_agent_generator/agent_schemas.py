from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class AgentIdeaInput(BaseModel):
    """User-provided idea for the agent you want to generate."""
    idea: str = Field(..., description="Plain-language idea describing the agent to build")
    agent_name: Optional[str] = Field(None, description="Optional human-friendly name for the agent")
    goals: Optional[List[str]] = Field(default_factory=list, description="Optional list of concrete goals")
    inputs: Optional[List[str]] = Field(default_factory=list, description="Expected inputs for the agent")
    outputs: Optional[List[str]] = Field(default_factory=list, description="Expected outputs from the agent")
    apis: Optional[List[str]] = Field(default_factory=list, description="APIs the agent should use, if any")
    tools: Optional[List[str]] = Field(default_factory=list, description="Tools the agent should leverage")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Constraints or guardrails")
    non_functional: Optional[List[str]] = Field(default_factory=list, description="NFRs such as performance or UX")


class AgentSpecOutput(BaseModel):
    """Structured specification for the agent based on the user's idea."""
    name: str = Field(..., description="Canonical name for the agent")
    purpose: str = Field(..., description="What the agent does and why")
    capabilities: List[str] = Field(..., description="Key capabilities and behaviors")
    inputs: List[str] = Field(..., description="Expected inputs or parameters")
    outputs: List[str] = Field(..., description="Expected outputs/results")
    tools: List[str] = Field(default_factory=list, description="Recommended tools")
    apis: List[str] = Field(default_factory=list, description="Recommended APIs")
    modules: List[str] = Field(
        default_factory=lambda: ["agents.py", "tasks.py", "crew.py", "main.py"],
        description="Files to generate for the agent",
    )
    recommended_evaluation: List[str] = Field(
        default_factory=list, description="Suggested evaluation ideas/tests",
    )
    design_notes: Optional[str] = Field(None, description="Important design considerations")


class AgentFileOutput(BaseModel):
    filename: str = Field(..., description="The filename for the generated code")
    code: str = Field(..., description="The file contents (code or other text)")
    description: Optional[str] = Field(None, description="Short description of the file")


class AgentFilesBundle(BaseModel):
    files: List[AgentFileOutput] = Field(..., description="All files to write for this agent")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="Python packages to install")
    entrypoint: Optional[str] = Field(None, description="Relative path to the primary script to run")
    tests: Optional[Dict[str, str]] = Field(
        default=None, description="Mapping of test file path -> test file content"
    )


class VerificationReport(BaseModel):
    passed: bool = Field(..., description="Overall pass/fail")
    syntax_ok: bool = Field(..., description="True if all .py files compile (AST parse)")
    import_ok: bool = Field(..., description="True if entrypoint module imports successfully")
    tests_ok: bool = Field(..., description="True if optional tests executed successfully")
    errors: List[str] = Field(default_factory=list, description="Blocking errors")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking warnings")
    suggestions: List[str] = Field(default_factory=list, description="Actionable next steps")
