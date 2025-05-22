import os
import uvicorn
import logging
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
load_dotenv()

# Import your crewAI setup and Pydantic models from crew.py
from crew import dapp_crew_definition, CodeOutput, DeploymentInstructionsOutput, llm as crew_llm # Assuming crew_llm is defined in crew.py
from crewai_tools import CodeInterpreterTool

app = FastAPI(title="AI dApp Developer Assistant")

logging.basicConfig(level=logging.INFO)

class DappRequest(BaseModel):
    description: str = Field(..., example="Build a NFT marketplace on Ethereum with bidding and royalties")
    blockchain: str = Field(..., example="Ethereum")
    framework: Optional[str] = Field("hardhat", example="hardhat")
    frontend_framework: Optional[str] = Field("react", example="react")
    tests_required: Optional[bool] = Field(True, example=True) # This can be used to conditionally add a testing task or guide agents

class DappResponse(BaseModel):
    success: bool
    message: str
    generated_code: Optional[Dict[str, str]] = None  # E.g. {"SmartContract.sol": "...", "FrontendApp.jsx": "..."}
    logs: Optional[str] = None
    deployment_instructions: Optional[str] = None

@app.post("/build-and-deploy-dapp", response_model=DappResponse)
async def build_and_deploy_dapp(request: DappRequest):
    config = {
        "description": request.description,
        "blockchain": request.blockchain,
        "framework": request.framework,
        "frontend_framework": request.frontend_framework,
        "tests_required": str(request.tests_required), # Pass as string if agents expect it this way or for interpolation
    }

    logs = ""
    generated_code_dict: Dict[str, str] = {}
    deployment_instructions_str: str = "No deployment instructions generated."

    try:
        logging.info(f"Received dApp build request: {config}")
    except Exception as e:
        logs += f"Error logging request: {str(e)}\n"
        
    try:

        # Kickoff AI crew
        # The result of kickoff() when process is sequential is typically the result of the last task.
        # To get all task outputs, we often access them via crew.tasks_output after kickoff.
        crew_result = dapp_crew_definition.kickoff(inputs=config)
        logs += f"Crew kickoff completed. Raw crew_result: {str(crew_result)[:500]}\n"
        
        # Direct extraction from crew_result if available
        if crew_result and isinstance(crew_result, dict):
            logs += "Attempting to extract code directly from crew_result dictionary...\n"
            if 'filename' in crew_result and 'code' in crew_result:
                logs += f"Found code in crew_result! Filename: {crew_result['filename']}\n"
                generated_code_dict[crew_result['filename']] = crew_result['code']
                
        # Try another method to directly get the final task result
        try:
            final_task = dapp_crew_definition.tasks[-1]  # Last task
            if hasattr(final_task, 'result') and final_task.result:
                logs += f"Direct access to final_task.result: {str(final_task.result)[:200]}...\n"
                if isinstance(final_task.result, dict) and 'filename' in final_task.result and 'code' in final_task.result:
                    generated_code_dict[final_task.result['filename']] = final_task.result['code']
        except Exception as e:
            logs += f"Error accessing final task result: {str(e)}\n"

        # Process task outputs
        if not dapp_crew_definition.tasks:
            logs += "Warning: No tasks found in the crew definition to process outputs from.\n"
        else:
            logs += f"Processing outputs for {len(dapp_crew_definition.tasks)} tasks.\n"
            for i, task_instance in enumerate(dapp_crew_definition.tasks):
                task_output_item = task_instance.output
                if not task_output_item:
                    logs += f"Task {i+1} ('{task_instance.description[:50]}...') has no output object.\n"
                    # Try another way to get the result directly
                    if hasattr(task_instance, 'result') and task_instance.result:
                        logs += f"Found task_instance.result: {str(task_instance.result)[:200]}\n"
                        # If it's a dict with code
                        if isinstance(task_instance.result, dict) and 'filename' in task_instance.result and 'code' in task_instance.result:
                            generated_code_dict[task_instance.result['filename']] = task_instance.result['code']
                            logs += f"Extracted code from task_instance.result for {task_instance.result['filename']}\n"
                            continue
                        # If it's the raw string and could be parsed
                        elif isinstance(task_instance.result, str):
                            logs += "Found raw string result. Treating as raw output.\n"
                            generated_code_dict[f"task_{i+1}_raw_output.txt"] = task_instance.result
                            continue
                    continue

                logs += f"Processing output for task {i+1} ('{task_instance.description[:50]}...'): {str(task_output_item)[:200]}\n"
                
                actual_output = None
                # Access exported_output for Pydantic model or raw_output for string
                if hasattr(task_output_item, 'exported_output') and task_output_item.exported_output is not None:
                    actual_output = task_output_item.exported_output
                    logs += f"Task {i+1} used exported_output (Pydantic model): {str(actual_output)[:200]}\n"
                elif hasattr(task_output_item, 'raw_output') and task_output_item.raw_output is not None:
                    actual_output = task_output_item.raw_output
                    logs += f"Task {i+1} used raw_output. Raw output: {str(actual_output)[:200]}\n"
                    # Try to parse as JSON if it's a string
                    if isinstance(actual_output, str):
                        try:
                            import json
                            json_data = json.loads(actual_output)
                            if isinstance(json_data, dict) and 'filename' in json_data and 'code' in json_data:
                                logs += f"Successfully parsed JSON from raw_output with filename: {json_data['filename']}\n"
                                generated_code_dict[json_data['filename']] = json_data['code']
                                continue
                        except json.JSONDecodeError:
                            logs += "Could not parse raw_output as JSON, continuing with regular processing.\n"
                else:
                    logs += f"Task {i+1} ('{task_instance.description[:50]}...') had no recognizable output content (exported_output or raw_output was None or missing).\n"
                    # Try to get result directly
                    if hasattr(task_instance, 'result') and task_instance.result:
                        logs += f"Trying task_instance.result as fallback: {str(task_instance.result)[:100]}\n"
                        if isinstance(task_instance.result, dict) and 'filename' in task_instance.result and 'code' in task_instance.result:
                            generated_code_dict[task_instance.result['filename']] = task_instance.result['code']
                            logs += f"Extracted code from task_instance.result for {task_instance.result['filename']}\n"
                            continue
                    continue

                if isinstance(actual_output, CodeOutput):
                    logs += f"Task output is CodeOutput: {actual_output.filename}\n"
                    generated_code_dict[actual_output.filename] = actual_output.code
                    if actual_output.description:
                        logs += f"Code Description: {actual_output.description}\n"
                elif isinstance(actual_output, DeploymentInstructionsOutput):
                    logs += f"Task output is DeploymentInstructionsOutput.\n"
                    deployment_instructions_str = actual_output.instructions
                    if actual_output.required_tools:
                        deployment_instructions_str += "\n\nRequired Tools: " + ", ".join(actual_output.required_tools)
                    if actual_output.notes:
                        deployment_instructions_str += "\n\nAdditional Notes:\n" + actual_output.notes
                elif isinstance(actual_output, str):
                    # This case handles if raw_output was a string and not parsed into a Pydantic model by some chance.
                    # Or if a task was not expected to return a Pydantic model.
                    # You might need to decide how to handle raw string outputs from tasks not using output_pydantic.
                    logs += f"Task output {i+1} was a raw string. Attempting to infer structure or add to general logs.\n"
                    # For now, just log it. If tasks are supposed to return Pydantic models,
                    # this path indicates a potential issue in task definition or LLM's adherence to output format.
                    generated_code_dict[f"task_{i+1}_raw_output.txt"] = actual_output
                else:
                    logs += f"Task output {i+1} ('{task_instance.description[:50]}...') was not a recognized Pydantic model (CodeOutput, DeploymentInstructionsOutput) nor a raw string. Type: {type(actual_output)}, Data: {str(actual_output)[:200]}\n"

        if not generated_code_dict:
            logs += "Critical: No structured code was extracted from AI agent outputs. Check task definitions and agent goals.\n"
            logs += "Attempting regex-based extraction from task outputs...\n"
            
            # Try regex-based extraction from raw task outputs
            import re
            import json
            
            # Process each task again but with regex extraction
            for i, task_instance in enumerate(dapp_crew_definition.tasks):
                if hasattr(task_instance, '_result') and task_instance._result:
                    raw_result = str(task_instance._result)
                    logs += f"Found task._result for regex extraction. Length: {len(raw_result)}\n"
                    
                    # Common file extensions we might encounter
                    file_extensions = [".sol", ".js", ".jsx", ".ts", ".tsx", ".html", ".css"]
                    possible_files = []
                    
                    # Look for filename patterns in the LLM output
                    for ext in file_extensions:
                        filename_matches = re.findall(r'["\'](\w+-*\w*' + ext + ')["\']', raw_result)
                        possible_files.extend(filename_matches)
                    
                    if possible_files:
                        logs += f"Found possible filenames via regex: {possible_files}\n"
                        
                        # For each potential filename, try to extract code blocks following it
                        for filename in possible_files:
                            # Look for code blocks after the filename is mentioned
                            code_pattern = filename + r'[^`]*```[^`]*```'
                            code_matches = re.findall(code_pattern, raw_result, re.DOTALL)
                            
                            if code_matches:
                                # Extract code from markdown code blocks
                                for match in code_matches:
                                    code_block = re.search(r'```[\w]*\n([\s\S]*?)```', match)
                                    if code_block and code_block.group(1):
                                        logs += f"Extracted code for {filename} using regex code block pattern\n"
                                        generated_code_dict[filename] = code_block.group(1).strip()
                            else:
                                # If no code blocks, look for the filename followed by content
                                name_content_pattern = f"{filename}\s*:\s*['\"]([^'\"]+)['\"]" 
                                content_matches = re.findall(name_content_pattern, raw_result)
                                if content_matches:
                                    logs += f"Extracted code for {filename} using name:content pattern\n"
                                    generated_code_dict[filename] = content_matches[0]
            
            # Final attempt: extract all code blocks even without filenames
            if not generated_code_dict:
                all_code_blocks = re.findall(r'```[\w]*\n([\s\S]*?)```', str(crew_result), re.DOTALL)
                for i, code_block in enumerate(all_code_blocks):
                    # Try to infer file type from content
                    if "contract " in code_block and "function " in code_block:
                        filename = f"Contract_{i+1}.sol"
                    elif "import React" in code_block:
                        filename = f"Component_{i+1}.jsx"
                    elif "const " in code_block and "function" in code_block and "main()" in code_block:
                        filename = f"Script_{i+1}.js"
                    else:
                        filename = f"CodeBlock_{i+1}.txt"
                    
                    logs += f"Extracted generic code block as {filename}\n"
                    generated_code_dict[filename] = code_block.strip()
                    
            # Check the filesystem directly for generated files
            if not generated_code_dict:
                logs += "Direct extraction failed. Checking filesystem for generated files...\n"
                import os
                
                # List of common filenames that might have been generated
                potential_files = [
                    "Ecommerce.sol", "App.jsx", "deploy.js", "hardhat.config.js",
                    "NFT.sol", "MyToken.sol", "index.jsx", "EcommerceApp.jsx",
                    "ERC20Token.sol", "ERC721Token.sol", "Token.sol"
                ]
                
                # Check current directory for these files
                current_dir = os.getcwd()
                for filename in potential_files:
                    filepath = os.path.join(current_dir, filename)
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        try:
                            with open(filepath, 'r') as f:
                                file_content = f.read()
                                if file_content.strip():  # Only add non-empty files
                                    logs += f"Found and read file from disk: {filename}\n"
                                    generated_code_dict[filename] = file_content
                        except Exception as e:
                            logs += f"Error reading file {filename}: {str(e)}\n"
            
            # Last resort fallback - try to parse crew_result directly
            if not generated_code_dict and isinstance(crew_result, str):
                try:
                    potential_dict = json.loads(crew_result)
                    if isinstance(potential_dict, dict) and 'filename' in potential_dict and 'code' in potential_dict:
                        logs += f"Last resort: Extracted code from JSON parsing of crew_result: {potential_dict['filename']}\n"
                        generated_code_dict[potential_dict['filename']] = potential_dict['code']
                except json.JSONDecodeError:
                    logs += "Could not parse crew_result as JSON in last resort attempt.\n"
                    
                # Fallback of fallbacks - just save the raw output
                if not generated_code_dict and crew_result:
                    logs += "Emergency fallback: Using raw crew_result as output.\n"
                    generated_code_dict["raw_output.txt"] = str(crew_result)
            
            if not generated_code_dict:        
                raise HTTPException(status_code=500, detail="No code or deployment instructions generated by AI agents. Review logs.")

        # Initialize CodeInterpreterTool - potentially with the same LLM as the crew for consistency if tool uses LLM for analysis
        code_interpreter = CodeInterpreterTool(llm=crew_llm) # Use the LLM from crew.py

        for filename, code_content in list(generated_code_dict.items()): # Iterate over a copy
            logs += f"\n--- Processing/Checking {filename} ---\n"
            if not code_content or not isinstance(code_content, str) or len(code_content.strip()) == 0:
                logs += f"Skipping {filename} as its content is empty or invalid.\n"
                del generated_code_dict[filename]
                continue

            # Standard CodeInterpreterTool.run() method
            # This tool typically executes Python code. For Solidity, JS, etc., 'running' might mean linting or simple syntax checks.
            # The tool's capabilities for non-Python code depend on its underlying implementation.
            try:
                run_result = code_interpreter.run(code=code_content)
                logs += f"Execution/check result for {filename}: {run_result}\n" # run_result is a string
                # The standard .run() method returns a string, not a dict with 'error' and 'output' keys.
                # You'd need to parse this string to determine if an error occurred.
                # For simplicity, we'll assume if the string contains 'Error' or 'Exception', it's an error.
                # This is a basic check and might need refinement.
                if "error" in run_result.lower() or "exception" in run_result.lower():
                    error_detail = run_result
                    logs += f"Error detected in {filename}: {error_detail}\n"
                    
                    # Placeholder for error fixing loop:
                    # A real fix loop would re-engage an agent with the code and error_detail.
                    # e.g., fix_task_description = f"Fix the following error in {filename} given the code:\nCODE:\n{code_content}\nERROR:\n{error_detail}"
                    # (This would require a specialized fixing agent/task)
                    logs += f"Error fixing for {filename} is not implemented in this version. Manual review required.\n"
                    # Optionally, remove the file from generated_code_dict or mark it as erroneous
                    # For now, we'll keep it and let the user see the error in logs.

            except Exception as e_interpret:
                logs += f"Exception during code interpretation for {filename}: {str(e_interpret)}\n{traceback.format_exc()}\n"
                # This file is problematic

        return DappResponse(
            success=True, # Or False if critical errors occurred that weren't 'fixed'
            message="dApp code generation process completed. Review logs and generated files.",
            generated_code=generated_code_dict if generated_code_dict else None,
            logs=logs,
            deployment_instructions=deployment_instructions_str,
        )

    except Exception as e_main:
        error_info = f"Exception in dApp builder: {str(e_main)}\n{traceback.format_exc()}"
        logging.error(error_info)
        logs += "\nCRITICAL ERROR: " + error_info
        return DappResponse(
            success=False,
            message=f"Internal Server Error: {str(e_main)}",
            logs=logs
        )
        # Or: raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e_main)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

