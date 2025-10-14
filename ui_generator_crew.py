import os
# The package is python-dotenv but the import is from dotenv
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import CodeInterpreterTool, SerperDevTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Annotated



# Define Pydantic Models for structured output
class AgentConfigOutput(BaseModel):
    agent_type: str = Field(..., description="The identified type of agent (e.g., travel, customer service, education)")
    key_capabilities: List[str] = Field(..., description="List of key capabilities identified from the agent description")
    user_interaction_patterns: List[str] = Field(..., description="Common user interaction patterns with this type of agent")
    recommended_design_system: str = Field(..., description="Recommended design system for this agent type")

class UIComponentsOutput(BaseModel):
    components: List[str] = Field(..., description="List of UI components to include in the interface")
    layout_structure: str = Field(..., description="Description of the layout structure")
    interaction_model: str = Field(..., description="Description of how users will interact with the interface")
    design_tokens: Dict[str, Any] = Field(..., description="Design tokens like colors, typography, spacing")

class UICodeOutput(BaseModel):
    filename: str = Field(..., description="The filename for the generated code, e.g., 'index.html', 'styles.css', or 'app.js'")
    code: str = Field(..., description="The generated code content")
    description: Optional[str] = Field(None, description="A brief description of what the code does")

# Load environment variables
load_dotenv()

# Initialize LLM
llm = LLM(
    model="gemini/gemini-2.5-pro",  # Using gemini-pro, adjust if needed
    api_key=os.getenv("GEMINI_API_KEY"),
    # You can add other llm configurations here, e.g., temperature
)
# llm = LLM(model=f'azure/{os.environ.get("AZURE_LLM_MODEL_NAME")}', temperature=0.7)


# Initialize Tools
code_interpreter = CodeInterpreterTool(llm=llm)
serper_tool = SerperDevTool()
# Note: FileWriterTool removed - agents must return structured Pydantic models only

# AGENTS
agent_analyzer = Agent(
    role='AI Agent Analyst',
    goal='Analyze and understand the purpose, capabilities, and requirements of the AI agent to determine the optimal UI/UX approach',
    backstory=(
        "An expert in AI agent design with deep knowledge of various agent types and their interaction patterns. "
        "Specializes in analyzing agent descriptions and capabilities to identify the most effective UI/UX strategies."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[serper_tool],
    llm=llm
)

ui_designer = Agent(
    role='UI/UX Designer for AI Interfaces',
    goal='Design intuitive, effective, and aesthetically pleasing UI/UX for AI agents that enhances user interaction and agent capabilities',
    backstory=(
        "A creative and skilled UI/UX designer with expertise in designing interfaces for AI systems. "
        "Proficient in modern design systems, interaction patterns, and accessibility standards. "
        "Focuses on creating interfaces that make complex AI capabilities accessible and enjoyable to use."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[serper_tool],  # Only research tools, no file writing
    llm=llm
)

frontend_developer = Agent(
    role='Frontend Developer for AI Interfaces',
    goal='Implement the designed UI/UX as clean, maintainable, and responsive HTML, CSS, and JavaScript code',
    backstory=(
        "A talented frontend developer with experience in building interfaces for AI applications. "
        "Skilled in HTML, CSS, JavaScript, and modern frontend frameworks. "
        "Focuses on creating performant, accessible, and visually appealing implementations of UI/UX designs. "
        "IMPORTANT: You must ALWAYS return your output as a properly formatted UICodeOutput Pydantic model. "
        "Never use file writing tools - only return structured JSON data."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter],  # Only analysis tools, no file writing
    llm=llm
)

# TASKS
task_analyze_agent = Task(
    description=(
        "1. Analyze the AI agent description: '{agent_description}'\n"
        "2. Identify the agent's key capabilities: '{agent_capabilities}'\n"
        "3. Consider any API integrations mentioned: '{agent_api}'\n"
        "4. Determine the agent type, key interaction patterns, and recommended design approach\n"
        "5. YOU MUST RETURN YOUR OUTPUT IN THE FOLLOWING JSON SCHEMA FORMAT:\n"
        "   {\n"
        "     \"agent_type\": \"type of agent (e.g., travel, customer service)\",\n"
        "     \"key_capabilities\": [\"capability1\", \"capability2\", ...],\n"
        "     \"user_interaction_patterns\": [\"pattern1\", \"pattern2\", ...],\n"
        "     \"recommended_design_system\": \"recommended design system\"\n"
        "   }\n"
    ),
    expected_output="An AgentConfigOutput Pydantic model containing the agent type, key capabilities, interaction patterns, and recommended design system",
    agent=agent_analyzer,
    output_pydantic=AgentConfigOutput
)

task_design_ui_components = Task(
    description=(
        "1. Review the agent analysis from the previous task\n"
        "2. Consider any user preferences provided: '{user_preferences}'\n"
        "3. IMPORTANT: If a custom_design preference is provided, prioritize these design instructions\n"
        "   over the standard theme/layout/color_scheme options. The custom_design contains\n"
        "   natural language preferences like 'I prefer dark minimalist designs with subtle animations'\n"
        "4. Design the UI components, layout structure, interaction model, and design tokens\n"
        "5. Ensure the design aligns with the agent's purpose, capabilities, and user's design preferences\n"
        "6. YOU MUST RETURN YOUR OUTPUT IN THE FOLLOWING JSON SCHEMA FORMAT:\n"
        "   {\n"
        "     \"components\": [\"component1\", \"component2\", ...],\n"
        "     \"layout_structure\": \"description of layout\",\n"
        "     \"interaction_model\": \"description of interaction model\",\n"
        "     \"design_tokens\": {\"colors\": {}, \"typography\": {}, \"spacing\": {}}\n"
        "   }\n"
    ),
    expected_output="A UIComponentsOutput Pydantic model containing the UI components, layout structure, interaction model, and design tokens",
    agent=ui_designer,
    context=[task_analyze_agent],
    output_pydantic=UIComponentsOutput
)

task_generate_html = Task(
    description=(
        "1. Review the agent analysis and UI design from previous tasks\n"
        "2. Create the HTML structure for the AI agent interface\n"
        "3. Ensure the HTML is semantic, accessible, and follows best practices\n"
        "4. Include appropriate containers for all the required components\n"
        "\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- DO NOT use any file writing tools\n"
        "- ONLY return a UICodeOutput Pydantic model with this exact structure:\n"
        "  {\"filename\": \"index.html\", \"code\": \"...\", \"description\": \"...\"}\n"
        "- The 'code' field must contain the complete HTML as a string\n"
        "- Ensure the JSON is valid and properly escaped\n"
        "\n"
        "LINKING REQUIREMENTS (VERY IMPORTANT):\n"
        "- In the <head> section, include: <link rel=\"stylesheet\" href=\"styles.css\">\n"
        "- Before the closing </body> tag, include: <script src=\"app.js\"></script>\n"
        "- These links are REQUIRED for the CSS and JavaScript to work\n"
        "- DO NOT comment out these tags - they must be active\n"
    ),
    expected_output="A UICodeOutput Pydantic model containing the filename, HTML code, and description",
    agent=frontend_developer,
    context=[task_analyze_agent, task_design_ui_components],
    output_pydantic=UICodeOutput
)

task_generate_css = Task(
    description=(
        "1. Review the agent analysis, UI design, and HTML structure from previous tasks\n"
        "2. Create the CSS styles for the AI agent interface\n"
        "3. Implement the design tokens (colors, typography, spacing) from the UI design\n"
        "4. Ensure the styles are responsive and accessible\n"
        "5. If custom design preferences were specified, make sure your CSS implementation\n"
        "   faithfully reflects these preferences (e.g., 'minimalist', 'colorful', etc.)\n"
        "\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- DO NOT use any file writing tools\n"
        "- ONLY return a UICodeOutput Pydantic model with this exact structure:\n"
        "  {\"filename\": \"styles.css\", \"code\": \"...\", \"description\": \"...\"}\n"
        "- The 'code' field must contain the complete CSS as a string\n"
        "- Ensure the JSON is valid and properly escaped\n"
    ),
    expected_output="A UICodeOutput Pydantic model containing the filename, CSS code, and description",
    agent=frontend_developer,
    context=[task_analyze_agent, task_design_ui_components, task_generate_html],
    output_pydantic=UICodeOutput
)

task_generate_javascript = Task(
    description=(
        "1. Review the agent analysis, UI design, and HTML/CSS from previous tasks\n"
        "2. Create the JavaScript code for the AI agent interface\n"
        "3. Implement the interaction model from the UI design\n"
        "4. Include functionality for handling user input and displaying agent responses\n"
        "\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- DO NOT use any file writing tools\n"
        "- ONLY return a UICodeOutput Pydantic model with this exact structure:\n"
        "  {\"filename\": \"app.js\", \"code\": \"...\", \"description\": \"...\"}\n"
        "- The 'code' field must contain the complete JavaScript as a string\n"
        "- Ensure the JSON is valid and properly escaped\n"
    ),
    expected_output="A UICodeOutput Pydantic model containing the filename, JavaScript code, and description",
    agent=frontend_developer,
    context=[task_analyze_agent, task_design_ui_components, task_generate_html, task_generate_css],
    output_pydantic=UICodeOutput
)

# CREW DEFINITION
ui_generator_crew = Crew(
    agents=[agent_analyzer, ui_designer, frontend_developer],
    tasks=[task_analyze_agent, task_design_ui_components, task_generate_html, task_generate_css, task_generate_javascript],
    process=Process.sequential,
    verbose=True,
)
