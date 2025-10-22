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

# PHASE 1 ENHANCEMENT: Quality Assurance Models
class QAReportOutput(BaseModel):
    """Quality Assurance report for generated code."""
    passed: bool = Field(..., description="Whether the code passed all QA checks")
    issues_found: List[str] = Field(default_factory=list, description="List of issues discovered during testing")
    severity_levels: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues by severity: critical, high, medium, low"
    )
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    syntax_valid: bool = Field(default=True, description="Whether syntax is valid for all files")
    html_valid: bool = Field(default=True, description="Whether HTML structure is valid")
    css_valid: bool = Field(default=True, description="Whether CSS is valid")
    js_valid: bool = Field(default=True, description="Whether JavaScript is valid")

class AccessibilityReportOutput(BaseModel):
    """Accessibility audit report for WCAG compliance."""
    wcag_level: str = Field(..., description="WCAG compliance level achieved (A, AA, AAA, or None)")
    passed: bool = Field(..., description="Whether the UI meets WCAG 2.1 AA standards")
    violations: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of accessibility violations with details"
    )
    aria_score: int = Field(default=0, description="ARIA implementation score (0-100)")
    keyboard_navigable: bool = Field(default=False, description="Whether UI is fully keyboard navigable")
    screen_reader_compatible: bool = Field(default=False, description="Whether UI is screen reader compatible")
    contrast_ratio_passed: bool = Field(default=False, description="Whether color contrast meets 4.5:1 minimum")
    semantic_html_used: bool = Field(default=False, description="Whether semantic HTML5 elements are used")
    recommendations: List[str] = Field(default_factory=list, description="Accessibility improvement recommendations")

# PHASE 2 ENHANCEMENT: Code Revision & Performance Models
class RevisedCodeOutput(BaseModel):
    """Revised code after fixing QA and accessibility issues."""
    html_code: str = Field(..., description="Fixed HTML code")
    css_code: str = Field(..., description="Fixed CSS code")
    js_code: str = Field(..., description="Fixed JavaScript code")
    fixes_applied: List[str] = Field(default_factory=list, description="List of fixes that were applied")
    issues_remaining: List[str] = Field(default_factory=list, description="Issues that could not be auto-fixed")

class PerformanceReportOutput(BaseModel):
    """Performance optimization report."""
    optimized: bool = Field(..., description="Whether code was successfully optimized")
    optimizations_applied: List[str] = Field(default_factory=list, description="List of optimizations applied")
    bundle_size_reduction: str = Field(default="0%", description="Estimated bundle size reduction")
    lighthouse_score_estimate: int = Field(default=0, description="Estimated Lighthouse performance score (0-100)")
    recommendations: List[str] = Field(default_factory=list, description="Additional performance recommendations")

# PHASE 2.5 ENHANCEMENT: Web3 & Smart Contract Integration Models
class ContractInterfaceOutput(BaseModel):
    """Parsed smart contract interface details from ABI."""
    contract_name: str = Field(..., description="Name of the smart contract")
    contract_address: str = Field(..., description="Deployed contract address")
    network: str = Field(..., description="Network name (mainnet, sepolia, polygon, etc.)")
    read_functions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of view/pure functions with params and return types"
    )
    write_functions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of state-changing functions with params"
    )
    events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of contract events with parameters"
    )
    roles: List[str] = Field(
        default_factory=list,
        description="Access control roles (if using OpenZeppelin AccessControl)"
    )
    constructor_params: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Constructor parameters if needed"
    )

class Web3IntegrationOutput(BaseModel):
    """Generated Web3 integration code and configuration."""
    wallet_connection_code: str = Field(..., description="Complete wallet connection logic (MetaMask, WalletConnect)")
    contract_wrapper_code: str = Field(..., description="Type-safe contract wrapper class")
    network_config: Dict[str, Any] = Field(..., description="Network configuration (RPC URLs, chain IDs, explorers)")
    required_libraries: List[str] = Field(
        default_factory=lambda: ["ethers@6.0.0", "web3modal@3.0.0"],
        description="Required npm packages or CDN scripts"
    )
    event_listeners: List[str] = Field(
        default_factory=list,
        description="Generated event listener code for contract events"
    )
    transaction_handlers: Dict[str, str] = Field(
        default_factory=dict,
        description="Transaction handling code for each write function"
    )
    read_function_calls: Dict[str, str] = Field(
        default_factory=dict,
        description="Generated code for calling read/view functions"
    )
    role_checks: Dict[str, str] = Field(
        default_factory=dict,
        description="Code for checking user roles (if AccessControl is used)"
    )
    gas_estimation_code: str = Field(
        default="",
        description="Gas estimation logic for transactions"
    )

# Load environment variables
load_dotenv()

# Initialize LLM
llm = LLM(
    model="gemini/gemini-2.5-flash",  # Using gemini-pro, adjust if needed
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

# PHASE 1 ENHANCEMENT: Quality Assurance Agents
qa_tester = Agent(
    role='Frontend QA Engineer',
    goal='Test generated code for bugs, syntax errors, edge cases, and user experience issues using static analysis',
    backstory=(
        "An expert in frontend testing with deep knowledge of unit tests, integration tests, and static code analysis. "
        "Uses Python's AST module and pattern matching to catch bugs before runtime. "
        "Validates HTML structure, CSS properties, JavaScript syntax, and common coding mistakes. "
        "Checks for missing error handlers, hardcoded values, console.log statements, and undefined variables. "
        "Ensures user flows are logical and interaction patterns are intuitive."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter],  # Uses code interpreter for static analysis
    llm=llm
)

accessibility_auditor = Agent(
    role='Web Accessibility Specialist (WCAG 2.1)',
    goal='Ensure WCAG 2.1 AA compliance, screen reader compatibility, and inclusive design for all users',
    backstory=(
        "A certified accessibility expert (CPACC) with expertise in ARIA, semantic HTML, keyboard navigation, "
        "and assistive technologies. Deeply familiar with WCAG 2.1 guidelines and Section 508 requirements. "
        "Checks for proper heading hierarchy, alt text on images, ARIA labels on interactive elements, "
        "color contrast ratios (minimum 4.5:1), focus indicators, and form labels. "
        "Ensures interfaces are usable by people of all abilities, including those using screen readers, "
        "keyboard-only navigation, or high contrast modes. "
        "Uses static analysis to validate HTML structure and provide specific, actionable fixes."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter],  # Uses code interpreter for HTML analysis
    llm=llm
)

# PHASE 2 ENHANCEMENT: Code Revision & Performance Agents
code_reviser = Agent(
    role='Code Reviser & Bug Fixer',
    goal='Automatically fix all QA issues and accessibility violations in the generated code',
    backstory=(
        "An expert code refactoring specialist with deep knowledge of best practices, security, and accessibility. "
        "Takes QA and accessibility reports and systematically fixes every issue found. "
        "Applies fixes like: wrapping async functions in try/catch, replacing .innerHTML with safe DOM methods, "
        "adding null checks, increasing touch target sizes, fixing color contrast, adding ARIA attributes, "
        "removing console.log statements, converting hardcoded values to CSS variables, and more. "
        "Returns fully revised HTML, CSS, and JavaScript code that passes all tests. "
        "Uses Python code interpreter to perform systematic code transformations."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter],
    llm=llm
)

performance_optimizer = Agent(
    role='Frontend Performance Engineer',
    goal='Optimize code for production with minification, lazy loading, and performance best practices',
    backstory=(
        "A performance optimization specialist focused on achieving Lighthouse scores of 90+. "
        "Applies production-ready optimizations: minifies HTML/CSS/JS, adds async/defer to scripts, "
        "implements lazy loading for images, removes unused CSS, adds resource hints (preload, prefetch), "
        "optimizes Critical Rendering Path, and ensures fast Time to Interactive (TTI). "
        "Provides detailed performance metrics and estimates bundle size reductions. "
        "Uses code analysis to identify optimization opportunities."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter],
    llm=llm
)

# PHASE 2.5 ENHANCEMENT: Web3 & Smart Contract Agents
smart_contract_parser = Agent(
    role='Smart Contract ABI Parser & Analyzer',
    goal='Parse smart contract ABIs and extract function signatures, events, and access control patterns',
    backstory=(
        "An expert in Ethereum smart contracts and Solidity with deep knowledge of ERC standards, "
        "OpenZeppelin libraries, and DeFi protocols. Specializes in analyzing contract ABIs to identify: "
        "- Read functions (view/pure) vs Write functions (state-changing) "
        "- Function parameters and return types "
        "- Events and their indexed parameters "
        "- Access control roles (OpenZeppelin AccessControl pattern) "
        "- Common patterns: ERC-20, ERC-721, ERC-1155, Governor, Timelock "
        "Uses Python's JSON parsing and pattern matching to extract type-safe contract interfaces. "
        "Identifies constructor parameters, fallback functions, and special functions like receive(). "
        "IMPORTANT: You must return ContractInterfaceOutput with complete function signatures."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter],  # Uses code interpreter for ABI parsing
    llm=llm
)

web3_integrator = Agent(
    role='Web3 Integration Specialist',
    goal='Generate production-ready Web3 code for wallet connections, contract interactions, and blockchain event handling',
    backstory=(
        "A senior blockchain frontend developer with expertise in ethers.js v6, web3.js, wagmi, and Web3Modal. "
        "Specializes in creating type-safe, error-resistant dApp frontends with: "
        "- Multi-wallet support (MetaMask, WalletConnect, Coinbase Wallet, Rainbow) "
        "- Multi-chain configurations (Ethereum, Polygon, Arbitrum, Optimism, BSC) "
        "- Transaction management (gas estimation, error handling, confirmation tracking) "
        "- Real-time event listeners for contract events "
        "- Role-based UI (show/hide features based on user's on-chain permissions) "
        "- Proper error messages for user-rejected transactions, insufficient funds, network mismatches "
        "Generates clean, maintainable JavaScript classes that wrap contract interactions. "
        "Follows best practices: checks for window.ethereum, handles network switching, validates addresses. "
        "IMPORTANT: You must return Web3IntegrationOutput with complete working code."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter, serper_tool],  # Code gen + research for best practices
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

# PHASE 1 ENHANCEMENT: Quality Assurance Tasks
task_qa_test = Task(
    description=(
        "Perform comprehensive quality assurance testing on the generated HTML, CSS, and JavaScript code.\n"
        "\n"
        "TESTING CHECKLIST:\n"
        "\n"
        "1. SYNTAX VALIDATION:\n"
        "   - Parse HTML: Check for unclosed tags, invalid attributes, missing required attributes\n"
        "   - Parse CSS: Validate property names, check for syntax errors, verify selectors\n"
        "   - Parse JavaScript: Use AST to check syntax, look for common errors\n"
        "\n"
        "2. CODE QUALITY CHECKS:\n"
        "   - JavaScript: Look for undefined variables, unused code, console.log statements\n"
        "   - CSS: Check for duplicate selectors, unused styles, !important overuse\n"
        "   - HTML: Validate IDs are unique, check for inline styles (should be in CSS)\n"
        "\n"
        "3. COMMON BUG PATTERNS:\n"
        "   - Missing error handlers in JavaScript\n"
        "   - Hardcoded values that should be configurable\n"
        "   - Event listeners not properly bound\n"
        "   - Missing null/undefined checks\n"
        "   - Unescaped user input (XSS vulnerabilities)\n"
        "\n"
        "4. USER FLOW VALIDATION:\n"
        "   - Verify all interactive elements have event handlers\n"
        "   - Check that form submissions are handled\n"
        "   - Ensure error messages are displayed appropriately\n"
        "   - Validate loading states are shown during async operations\n"
        "\n"
        "5. SEVERITY CLASSIFICATION:\n"
        "   - Critical: Syntax errors, broken functionality, security issues\n"
        "   - High: Missing error handlers, poor UX, accessibility blockers\n"
        "   - Medium: Code quality issues, minor bugs, performance concerns\n"
        "   - Low: Style inconsistencies, missing comments, minor improvements\n"
        "\n"
        "IMPORTANT: Use static analysis only - do NOT execute the code. Use Python's ast module, \n"
        "regex patterns, and HTML/CSS parsing to identify issues.\n"
        "\n"
        "Return a QAReportOutput with:\n"
        "- passed: true if no critical/high issues found\n"
        "- issues_found: detailed list of all issues\n"
        "- severity_levels: count by severity (critical, high, medium, low)\n"
        "- recommendations: actionable fixes for each issue\n"
        "- validity flags for each file type\n"
    ),
    expected_output="A QAReportOutput Pydantic model with comprehensive test results and recommendations",
    agent=qa_tester,
    context=[task_generate_html, task_generate_css, task_generate_javascript],
    output_pydantic=QAReportOutput
)

task_accessibility_audit = Task(
    description=(
        "Perform a comprehensive accessibility audit on the generated HTML and CSS to ensure WCAG 2.1 AA compliance.\n"
        "\n"
        "ACCESSIBILITY CHECKLIST:\n"
        "\n"
        "1. SEMANTIC HTML (Required for AA):\n"
        "   - Check for proper use of <header>, <nav>, <main>, <footer>, <section>, <article>\n"
        "   - Verify heading hierarchy (h1 > h2 > h3, no skipped levels)\n"
        "   - Ensure lists use <ul>/<ol>/<li> appropriately\n"
        "   - Check that <button> is used for buttons, not <div> or <a>\n"
        "   - Validate form elements use <label> with for attribute\n"
        "\n"
        "2. ARIA LABELS AND ROLES (Required for AA):\n"
        "   - All interactive elements must have accessible names\n"
        "   - Images must have alt text (alt=\"\" for decorative images)\n"
        "   - Buttons/links must have aria-label if text is not descriptive\n"
        "   - Form inputs must have associated labels or aria-label\n"
        "   - Icon-only buttons must have aria-label\n"
        "   - Landmarks should have aria-label if multiple of same type exist\n"
        "\n"
        "3. KEYBOARD NAVIGATION (Required for AA):\n"
        "   - All interactive elements must be keyboard accessible\n"
        "   - Check for tabindex (avoid positive values, use 0 or -1)\n"
        "   - Ensure focus is visible (outline or custom focus styles)\n"
        "   - Verify logical tab order follows visual layout\n"
        "   - Check that modals trap focus properly\n"
        "\n"
        "4. COLOR CONTRAST (Required for AA):\n"
        "   - Text must have 4.5:1 contrast ratio with background (normal text)\n"
        "   - Large text (18pt+) must have 3:1 contrast ratio\n"
        "   - UI components must have 3:1 contrast ratio\n"
        "   - Check that information is not conveyed by color alone\n"
        "\n"
        "5. SCREEN READER COMPATIBILITY:\n"
        "   - Check for proper ARIA live regions for dynamic content\n"
        "   - Verify error messages are announced\n"
        "   - Ensure loading states are announced\n"
        "   - Check that hidden content uses aria-hidden=\"true\"\n"
        "\n"
        "6. FORM ACCESSIBILITY:\n"
        "   - All inputs have associated labels\n"
        "   - Required fields are marked with aria-required=\"true\"\n"
        "   - Error messages use aria-describedby\n"
        "   - Fieldsets group related inputs\n"
        "\n"
        "7. RESPONSIVE & MOBILE:\n"
        "   - Check for viewport meta tag\n"
        "   - Verify touch targets are at least 44x44 pixels\n"
        "   - Ensure text is resizable up to 200%\n"
        "\n"
        "SCORING:\n"
        "- ARIA Score: 0-100 based on proper ARIA implementation\n"
        "- WCAG Level: 'AAA' if exceeds AA, 'AA' if meets AA, 'A' if only meets A, 'None' if fails\n"
        "\n"
        "For each violation, provide:\n"
        "1. Element/line where issue occurs\n"
        "2. WCAG guideline violated (e.g., 1.3.1, 2.4.6)\n"
        "3. Severity (critical, high, medium, low)\n"
        "4. Specific fix with code example\n"
        "\n"
        "Return AccessibilityReportOutput with:\n"
        "- wcag_level: highest level achieved\n"
        "- passed: true if meets WCAG 2.1 AA\n"
        "- violations: detailed list with fixes\n"
        "- all boolean flags set appropriately\n"
        "- recommendations for improvements\n"
    ),
    expected_output="An AccessibilityReportOutput Pydantic model with WCAG compliance assessment and specific fixes",
    agent=accessibility_auditor,
    context=[task_generate_html, task_generate_css],
    output_pydantic=AccessibilityReportOutput
)

# PHASE 2 ENHANCEMENT: Code Revision & Performance Tasks
task_revise_code = Task(
    description=(
        "Review the QA and Accessibility reports from previous tasks and systematically fix ALL issues found.\n"
        "\n"
        "MANDATORY FIXES TO APPLY:\n"
        "\n"
        "1. QA ISSUES - Apply these fixes based on the QA report:\n"
        "   - ASYNC ERROR HANDLING: Wrap all async/await functions in try/catch blocks\n"
        "   - XSS PREVENTION: Replace ALL .innerHTML with safe alternatives (textContent or createElement)\n"
        "   - NULL CHECKS: Add 'if (element)' checks after all DOM queries\n"
        "   - REMOVE DEBUG: Delete all console.log and alert() statements\n"
        "   - CSS VARIABLES: Convert hardcoded colors to CSS variables in :root\n"
        "   - CSS CLASSES: Replace inline style manipulations with CSS classes\n"
        "   - CLEAN UP: Remove redundant CSS properties and unused variables\n"
        "\n"
        "2. ACCESSIBILITY FIXES - Apply these fixes based on the Accessibility report:\n"
        "   - TOUCH TARGETS: Increase all interactive elements to minimum 44x44px\n"
        "   - COLOR CONTRAST: Fix any colors below 4.5:1 contrast ratio\n"
        "   - ARIA ATTRIBUTES: Add missing aria-label, aria-describedby, role attributes\n"
        "   - SEMANTIC HTML: Wrap interactive non-button elements in <button> tags\n"
        "   - KEYBOARD NAV: Ensure all interactive elements are focusable\n"
        "   - SCREEN READER: Add aria-hidden for decorative elements, aria-live for dynamic content\n"
        "\n"
        "3. CODE TRANSFORMATION STRATEGY:\n"
        "   - Use Python's code interpreter to parse and transform the code\n"
        "   - Apply fixes systematically (don't miss any issue from the reports)\n"
        "   - Maintain code structure and functionality while fixing issues\n"
        "   - Test that fixes don't break existing functionality\n"
        "\n"
        "CRITICAL: You MUST fix EVERY issue listed in the QA and Accessibility reports.\n"
        "Return RevisedCodeOutput with:\n"
        "- html_code: fully fixed HTML\n"
        "- css_code: fully fixed CSS\n"
        "- js_code: fully fixed JavaScript\n"
        "- fixes_applied: detailed list of all fixes made\n"
        "- issues_remaining: list of any issues that couldn't be auto-fixed (should be empty)\n"
    ),
    expected_output="A RevisedCodeOutput Pydantic model with all code fixed and zero remaining issues",
    agent=code_reviser,
    context=[task_generate_html, task_generate_css, task_generate_javascript, task_qa_test, task_accessibility_audit],
    output_pydantic=RevisedCodeOutput
)

task_optimize_performance = Task(
    description=(
        "Optimize the revised code for production deployment with performance best practices.\n"
        "\n"
        "OPTIMIZATION CHECKLIST:\n"
        "\n"
        "1. HTML OPTIMIZATIONS:\n"
        "   - Add viewport meta tag if missing\n"
        "   - Add charset meta tag\n"
        "   - Use async/defer on non-critical <script> tags\n"
        "   - Add preload/prefetch for critical resources\n"
        "   - Minify HTML (remove comments, extra whitespace)\n"
        "\n"
        "2. CSS OPTIMIZATIONS:\n"
        "   - Remove unused CSS rules\n"
        "   - Minify CSS (remove comments, whitespace, optimize selectors)\n"
        "   - Combine similar media queries\n"
        "   - Add will-change hints for animated elements\n"
        "   - Use CSS containment where appropriate\n"
        "\n"
        "3. JAVASCRIPT OPTIMIZATIONS:\n"
        "   - Minify JavaScript (remove comments, whitespace, shorten variable names)\n"
        "   - Use event delegation where possible\n"
        "   - Debounce/throttle scroll/resize handlers if present\n"
        "   - Mark expensive operations with performance hints\n"
        "   - Add passive event listeners for scroll/touch events\n"
        "\n"
        "4. PERFORMANCE METRICS:\n"
        "   - Estimate bundle size reduction (bytes saved)\n"
        "   - Estimate Lighthouse performance score (0-100)\n"
        "   - List all optimizations applied\n"
        "   - Provide recommendations for further improvements\n"
        "\n"
        "IMPORTANT: Focus on production-ready optimizations. Don't break functionality.\n"
        "Use Python code interpreter to apply minification and transformations.\n"
        "\n"
        "Return PerformanceReportOutput with:\n"
        "- optimized: true if successful\n"
        "- optimizations_applied: detailed list of all optimizations\n"
        "- bundle_size_reduction: estimated percentage (e.g., '23%')\n"
        "- lighthouse_score_estimate: 0-100 score estimate\n"
        "- recommendations: additional performance tips\n"
    ),
    expected_output="A PerformanceReportOutput Pydantic model with optimization details and performance metrics",
    agent=performance_optimizer,
    context=[task_revise_code],
    output_pydantic=PerformanceReportOutput
)

# PHASE 2.5 ENHANCEMENT: Web3 & Smart Contract Tasks
task_parse_contract = Task(
    description=(
        "Parse the provided smart contract ABI and extract all interface details.\n"
        "\n"
        "CONTRACT INFORMATION PROVIDED:\n"
        "- Contract Address: '{contract_address}'\n"
        "- Contract ABI: '{contract_abi}'\n"
        "- Network: '{network}'\n"
        "\n"
        "PARSING CHECKLIST:\n"
        "\n"
        "1. LOAD AND VALIDATE ABI:\n"
        "   - Parse the JSON ABI file or string\n"
        "   - Validate it's a proper Solidity ABI structure\n"
        "   - Extract contract name (if available in metadata)\n"
        "\n"
        "2. CATEGORIZE FUNCTIONS:\n"
        "   - Identify READ functions (view, pure)\n"
        "   - Identify WRITE functions (state-changing, payable)\n"
        "   - For each function, extract:\n"
        "     * Function name\n"
        "     * Input parameters (name, type, indexed for events)\n"
        "     * Output/return types\n"
        "     * State mutability (view, pure, payable, nonpayable)\n"
        "\n"
        "3. EXTRACT EVENTS:\n"
        "   - List all event definitions\n"
        "   - For each event, extract:\n"
        "     * Event name\n"
        "     * Parameters (name, type, indexed status)\n"
        "\n"
        "4. DETECT ACCESS CONTROL:\n"
        "   - Look for OpenZeppelin AccessControl patterns:\n"
        "     * hasRole(bytes32,address) function\n"
        "     * getRoleAdmin(bytes32) function\n"
        "     * Role-based modifiers\n"
        "   - Extract role constants (e.g., DEFAULT_ADMIN_ROLE, MINTER_ROLE)\n"
        "   - Identify which functions require which roles\n"
        "\n"
        "5. IDENTIFY ERC STANDARDS:\n"
        "   - Check if implements ERC-20 (transfer, balanceOf, approve, etc.)\n"
        "   - Check if implements ERC-721 (mint, ownerOf, tokenURI, etc.)\n"
        "   - Check if implements ERC-1155 (batch operations)\n"
        "   - Check if implements Governor pattern (propose, castVote, execute)\n"
        "\n"
        "IMPORTANT: Return ContractInterfaceOutput with complete, type-safe function signatures.\n"
        "This output will be used to generate Web3 integration code.\n"
    ),
    expected_output="A ContractInterfaceOutput Pydantic model with parsed contract interface",
    agent=smart_contract_parser,
    context=[],  # Standalone task, doesn't depend on others
    output_pydantic=ContractInterfaceOutput
)

task_generate_web3_integration = Task(
    description=(
        "Generate production-ready Web3 integration code based on the parsed contract interface.\n"
        "\n"
        "CONTRACT INTERFACE:\n"
        "- Use the parsed contract interface from the previous task\n"
        "- Contract Address: '{contract_address}'\n"
        "- Network: '{network}'\n"
        "\n"
        "CODE GENERATION CHECKLIST:\n"
        "\n"
        "1. WALLET CONNECTION CODE:\n"
        "   - Generate complete wallet connection logic:\n"
        "     * Check for window.ethereum\n"
        "     * Handle MetaMask, WalletConnect, Coinbase Wallet\n"
        "     * Request account access (eth_requestAccounts)\n"
        "     * Get signer and provider\n"
        "     * Display connected address in UI\n"
        "   - Handle wallet events:\n"
        "     * accountsChanged → reload or update UI\n"
        "     * chainChanged → reload or prompt network switch\n"
        "     * disconnect → clear state\n"
        "\n"
        "2. NETWORK CONFIGURATION:\n"
        "   - Generate network config object with:\n"
        "     * Chain ID (hex and decimal)\n"
        "     * RPC URL (Infura, Alchemy, or public)\n"
        "     * Block explorer URL\n"
        "     * Currency symbol (ETH, MATIC, etc.)\n"
        "   - Add network switching logic\n"
        "   - Handle wrong network errors\n"
        "\n"
        "3. CONTRACT WRAPPER CLASS:\n"
        "   - Generate a JavaScript class that wraps the contract:\n"
        "     ```javascript\n"
        "     class ContractWrapper {\n"
        "       constructor(address, abi, provider) { ... }\n"
        "       // Read functions\n"
        "       async functionName(params) { ... }\n"
        "       // Write functions with gas estimation\n"
        "       async writeFunctionName(params) { ... }\n"
        "     }\n"
        "     ```\n"
        "   - For each READ function, generate:\n"
        "     * Async function that calls contract\n"
        "     * Error handling\n"
        "     * Return type formatting (e.g., format BigNumber to string)\n"
        "   - For each WRITE function, generate:\n"
        "     * Gas estimation\n"
        "     * Transaction building\n"
        "     * Confirmation waiting\n"
        "     * Error handling (user rejected, insufficient funds, etc.)\n"
        "\n"
        "4. EVENT LISTENERS:\n"
        "   - For each contract event, generate:\n"
        "     * Event listener setup code\n"
        "     * Callback function template\n"
        "     * UI update logic\n"
        "   - Example:\n"
        "     ```javascript\n"
        "     contract.on('Transfer', (from, to, value) => {{\n"
        "       console.log('Transfer: ' + from + ' → ' + to + ': ' + value);\n"
        "       updateBalanceDisplay();\n"
        "     }});\n"
        "     ```\n"
        "\n"
        "5. TRANSACTION HANDLERS:\n"
        "   - Generate complete transaction flow for each write function:\n"
        "     * Validate inputs\n"
        "     * Show 'Confirming...' status\n"
        "     * Estimate gas\n"
        "     * Send transaction\n"
        "     * Show 'Waiting for confirmation...' status\n"
        "     * Wait for receipt\n"
        "     * Show success with transaction hash\n"
        "     * Update UI\n"
        "   - Handle all error cases:\n"
        "     * User rejected transaction\n"
        "     * Insufficient funds\n"
        "     * Gas estimation failed\n"
        "     * Transaction reverted\n"
        "\n"
        "6. ROLE-BASED UI (if AccessControl detected):\n"
        "   - Generate role checking functions:\n"
        "     ```javascript\n"
        "     async function checkUserRole(address) {\n"
        "       const isAdmin = await contract.hasRole(ADMIN_ROLE, address);\n"
        "       return { isAdmin, ... };\n"
        "     }\n"
        "     ```\n"
        "   - Generate UI visibility logic:\n"
        "     * Show admin panel only if user has admin role\n"
        "     * Disable buttons if user lacks permission\n"
        "\n"
        "7. REQUIRED LIBRARIES:\n"
        "   - Specify ethers.js v6 CDN or npm package\n"
        "   - Specify web3modal v3 if using multi-wallet\n"
        "\n"
        "IMPORTANT: Generate complete, copy-paste ready code.\n"
        "The generated code should work immediately with the contract address and ABI.\n"
        "Return Web3IntegrationOutput with all code and configurations.\n"
    ),
    expected_output="A Web3IntegrationOutput Pydantic model with complete Web3 integration code",
    agent=web3_integrator,
    context=[task_parse_contract],  # Depends on parsed contract interface
    output_pydantic=Web3IntegrationOutput
)

# CREW DEFINITION (PHASE 2: Enhanced with Code Revision & Performance)
ui_generator_crew = Crew(
    agents=[
        agent_analyzer,
        ui_designer,
        frontend_developer,
        qa_tester,               # PHASE 1: QA Testing
        accessibility_auditor,   # PHASE 1: Accessibility Auditing
        code_reviser,            # PHASE 2: Code Revision
        performance_optimizer    # PHASE 2: Performance Optimization
    ],
    tasks=[
        task_analyze_agent,
        task_design_ui_components,
        task_generate_html,
        task_generate_css,
        task_generate_javascript,
        task_qa_test,              # PHASE 1: Quality Assurance
        task_accessibility_audit,  # PHASE 1: Accessibility Check
        task_revise_code,          # PHASE 2: Auto-fix all issues
        task_optimize_performance  # PHASE 2: Production optimization
    ],
    process=Process.sequential,
    verbose=True,
)

# CREW DEFINITION (PHASE 2.5: Web3-Enhanced with Smart Contract Integration)
web3_ui_generator_crew = Crew(
    agents=[
        agent_analyzer,
        ui_designer,
        frontend_developer,
        smart_contract_parser,     # PHASE 2.5: Parse contract ABI
        web3_integrator,           # PHASE 2.5: Generate Web3 code
        qa_tester,                 # PHASE 1: QA Testing
        accessibility_auditor,     # PHASE 1: Accessibility Auditing
        code_reviser,              # PHASE 2: Code Revision
        performance_optimizer      # PHASE 2: Performance Optimization
    ],
    tasks=[
        task_analyze_agent,
        task_design_ui_components,
        task_parse_contract,         # PHASE 2.5: Parse contract first
        task_generate_web3_integration,  # PHASE 2.5: Generate Web3 code
        task_generate_html,
        task_generate_css,
        task_generate_javascript,
        task_qa_test,
        task_accessibility_audit,
        task_revise_code,
        task_optimize_performance
    ],
    process=Process.sequential,
    verbose=True,
)
