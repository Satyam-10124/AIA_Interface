import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import CodeInterpreterTool, SerperDevTool, FileWriterTool # Corrected import name
from pydantic import BaseModel, Field
from typing import Optional, List

# Define Pydantic Models for structured output
class CodeOutput(BaseModel):
    filename: str = Field(..., description="The suggested filename for the code, e.g., 'MyContract.sol' or 'app.js'")
    code: str = Field(..., description="The generated code content.")
    description: Optional[str] = Field(None, description="A brief description of what the code does.")

class DeploymentInstructionsOutput(BaseModel):
    instructions: str = Field(..., description="Step-by-step instructions for deployment.")
    required_tools: Optional[List[str]] = Field(None, description="List of tools or dependencies required for deployment.")
    notes: Optional[str] = Field(None, description="Any additional notes or common pitfalls.")

# Load environment variables
load_dotenv()

# Initialize LLM
# Ensure GEMINI_API_KEY is set in your .env file
llm = LLM(
    model="gemini/gemini-2.0-flash",  # Using gemini-pro, adjust if needed
    api_key=os.getenv("GEMINI_API_KEY"),
    # You can add other llm configurations here, e.g., temperature
)

# llm = LLM(model=f'azure/{os.environ.get("AZURE_LLM_MODEL_NAME")}', temperature=0.7)

# Initialize Tools
# The CodeInterpreterTool might need an LLM for more advanced operations like fixing code, 
# though 'fix_code' is not a standard method. We'll assume it's handled by your app.py logic for now.
code_interpreter = CodeInterpreterTool(llm=llm) 
serper_tool = SerperDevTool()
file_writer_tool = FileWriterTool() # Instantiate the tool

# AGENTS
smart_contract_agent = Agent(
    role='Senior Smart Contract Developer for dApps',
    goal='Generate secure, gas-efficient, and well-documented smart contract code for decentralized applications based on user requirements: {description} for the {blockchain} blockchain.',
    backstory=(
        "An expert in blockchain technology with profound knowledge of Solidity, Vyper, common smart contract patterns, security best practices, and gas optimization techniques. "
        "Specializes in creating robust smart contracts for various use cases including NFTs, DeFi protocols, and DAOs."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[code_interpreter, serper_tool, file_writer_tool], # Use instance
    llm=llm
)

frontend_agent = Agent(
    role='Lead Frontend Developer for Web3 Applications',
    goal='Develop intuitive, responsive, and interactive frontend interfaces for dApps using {frontend_framework}, ensuring seamless integration with smart contracts.',
    backstory=(
        "A creative and skilled frontend architect with extensive experience in building Web3 applications. Proficient in modern frontend frameworks like React, Vue, and Angular, "
        "and adept at using libraries such as Ethers.js or Web3.js for blockchain interaction. Prioritizes user experience and accessibility."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[serper_tool, file_writer_tool],
    llm=llm
)

deployment_agent = Agent(
    role='DevOps & Blockchain Deployment Specialist for dApps',
    goal='Generate comprehensive deployment scripts, configurations, and step-by-step instructions for deploying dApps using the {framework} framework on the {blockchain} network.',
    backstory=(
        "A seasoned DevOps engineer with specialized expertise in blockchain deployment tools and processes, including Hardhat, Truffle, and Brownie. "
        "Focuses on creating automated, reliable, and secure deployment pipelines for smart contracts and dApps."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[serper_tool, file_writer_tool],
    llm=llm
)

# TASKS
# Each task will output a JSON object: {"filename": "suggested_filename.ext", "code": "generated_code_string"}

task_generate_smart_contract = Task(
    description=(
        "1. Thoroughly analyze the dApp requirements provided: '{description}'.\n"
        "2. Identify the core logic and features for the smart contract for the '{blockchain}' blockchain.\n"
        "3. Generate the complete, secure, and gas-optimized smart contract code (e.g., in Solidity).\n"
        "4. YOU MUST RETURN YOUR OUTPUT IN THE FOLLOWING JSON SCHEMA FORMAT:\n"
        "   {\n"
        "     \"filename\": \"YourContractName.sol\",\n"
        "     \"code\": \"// Full solidity code here\",\n"
        "     \"description\": \"Brief description of the contract\"\n"
        "   }\n"
    ),
    expected_output="A CodeOutput Pydantic model object containing the filename, the generated smart contract code, and an optional description.",
    agent=smart_contract_agent,
    output_pydantic=CodeOutput
)

task_generate_frontend = Task(
    description=(
        "1. Review the dApp requirements: '{description}' and the generated smart contract (available in context).\n"
        "2. Design and develop the frontend code using the '{frontend_framework}' framework.\n"
        "3. Ensure the frontend includes necessary components for interacting with the smart contract functionalities (e.g., connecting wallet, calling contract methods, displaying data).\n"
        "4. YOU MUST RETURN YOUR OUTPUT IN THE FOLLOWING JSON SCHEMA FORMAT:\n"
        "   {\n"
        "     \"filename\": \"App.jsx\",\n"
        "     \"code\": \"// Full React component code here\",\n"
        "     \"description\": \"Brief description of the frontend\"\n"
        "   }\n"
    ),
    expected_output="A CodeOutput Pydantic model object containing the filename, the generated frontend code, and an optional description.",
    agent=frontend_agent,
    context=[task_generate_smart_contract], # Depends on smart contract details
    output_pydantic=CodeOutput
)

task_generate_deployment_script = Task(
    description=(
        "1. Examine the generated smart contract (available in context).\n"
        "2. Create a deployment script using the '{framework}' framework for the '{blockchain}' blockchain (e.g., a Hardhat deploy script).\n"
        "3. Ensure the script handles contract compilation and deployment correctly.\n"
        "4. YOU MUST RETURN YOUR OUTPUT IN THE FOLLOWING JSON SCHEMA FORMAT:\n"
        "   {\n"
        "     \"filename\": \"deploy.js\",\n"
        "     \"code\": \"// Full deployment script code here\",\n"
        "     \"description\": \"Brief description of the deployment script\"\n"
        "   }\n"
    ),
    expected_output="A CodeOutput Pydantic model object containing the filename, the generated deployment script, and an optional description.",
    agent=deployment_agent,
    context=[task_generate_smart_contract], # Depends on the smart contract
    output_pydantic=CodeOutput
)

# CREW DEFINITION
# This is the crew instance that will be imported and used in app.py
dapp_crew_definition = Crew(
    agents=[smart_contract_agent, frontend_agent, deployment_agent],
    tasks=[task_generate_smart_contract, task_generate_frontend, task_generate_deployment_script],
    process=Process.sequential,  # Tasks will run one after another
    verbose=True, # Enables detailed logging of the crew's execution
    # memory=True, # Set to True if you want the crew to remember past interactions in a session (can increase token usage)
    # share_crew=True # Advanced: allows agents to share a common state, useful for complex data passing
)
