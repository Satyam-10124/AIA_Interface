#!/usr/bin/env python3
import os
import json
import argparse
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
# The package is python-dotenv but the import is from dotenv
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Import crew setup for UI generation
from ui_generator_crew import ui_generator_crew, AgentConfigOutput, UIComponentsOutput, UICodeOutput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UI-Generator-CLI")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Agent UI/UX Generator CLI - Generate tailored UI/UX interfaces for AI agents"
    )
    
    parser.add_argument(
        "--agent-description", "-d",
        type=str,
        required=True,
        help="Description of the AI agent's purpose and functionality"
    )
    
    parser.add_argument(
        "--agent-capabilities", "-c",
        type=str,
        required=True,
        help="Comma-separated list of the agent's key capabilities"
    )
    
    parser.add_argument(
        "--agent-api", "-a",
        type=str,
        default="",
        help="APIs the agent will use (optional)"
    )
    
    # User design preference group
    design_group = parser.add_argument_group('Design Preferences')
    
    design_group.add_argument(
        "--custom-design", "-cd",
        type=str,
        default="",
        help="Custom design preferences in natural language (e.g., 'I prefer dark minimalist designs with subtle animations')"
    )
    
    design_group.add_argument(
        "--theme", "-t",
        type=str,
        choices=["light", "dark", "system"],
        default="light",
        help="UI theme preference"
    )
    
    parser.add_argument(
        "--layout", "-l",
        type=str,
        choices=["standard", "compact", "expanded"],
        default="standard",
        help="UI layout preference"
    )
    
    parser.add_argument(
        "--color-scheme", "-cs",
        type=str,
        choices=["blue", "green", "purple", "red", "orange", "teal"],
        default="blue",
        help="UI color scheme preference"
    )
    
    parser.add_argument(
        "--font-size", "-fs",
        type=str,
        choices=["small", "medium", "large"],
        default="medium",
        help="UI font size preference"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./generated_ui",
        help="Directory to save the generated UI files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()

def generate_ui(args):
    """Generate UI/UX based on the provided arguments."""
    # Prepare configuration for the crew
    config = {
        "agent_description": args.agent_description,
        "agent_capabilities": args.agent_capabilities,
        "agent_api": args.agent_api,
        "user_preferences": {
            "theme": args.theme,
            "layout": args.layout,
            "color_scheme": args.color_scheme,
            "font_size": args.font_size,
            "custom_design": args.custom_design
        }
    }
    
    ui_code_dict = {}
    logs = []
    
    def log(message):
        """Log a message and add it to the logs list."""
        logs.append(message)
        if args.verbose:
            logger.info(message)
    
    log(f"Processing UI generation request for agent: {config['agent_description'][:100]}...")
    
    # Log custom design preferences if provided
    if config['user_preferences']['custom_design']:
        log(f"Custom design preferences: {config['user_preferences']['custom_design']}")
    
    # Kickoff AI crew for UI generation
    log("Starting crewAI agents to analyze agent requirements and generate UI/UX...")
    try:
        crew_result = ui_generator_crew.kickoff(inputs=config)
        log("Crew kickoff completed successfully.")
    except Exception as e:
        error_msg = f"Error during crew execution: {str(e)}\n{traceback.format_exc()}"
        log(error_msg)
        logger.error(error_msg)
        return False, ui_code_dict, logs
    
    # Process task outputs
    if not ui_generator_crew.tasks:
        log("Warning: No tasks found in the crew definition.")
        return False, ui_code_dict, logs
    
    log(f"Processing outputs from {len(ui_generator_crew.tasks)} AI agent tasks.")
    log("Agent pipeline: Analysis → Design → HTML → CSS → JavaScript")
    
    for i, task_instance in enumerate(ui_generator_crew.tasks):
        task_output_item = task_instance.output
        if not task_output_item:
            log(f"Task {i+1} has no output object.")
            continue
        
        log(f"Processing output for task {i+1}: {task_instance.description[:50]}...")
        
        actual_output = None
        if hasattr(task_output_item, 'exported_output') and task_output_item.exported_output is not None:
            actual_output = task_output_item.exported_output
            log(f"Task {i+1} used exported_output (Pydantic model)")
        elif hasattr(task_output_item, 'raw_output') and task_output_item.raw_output is not None:
            actual_output = task_output_item.raw_output
            log(f"Task {i+1} used raw_output")
            
            # Try to parse as JSON if it's a string
            if isinstance(actual_output, str):
                try:
                    json_data = json.loads(actual_output)
                    if isinstance(json_data, dict) and 'filename' in json_data and 'code' in json_data:
                        log(f"Successfully parsed JSON from raw_output with filename: {json_data['filename']}")
                        ui_code_dict[json_data['filename']] = json_data['code']
                        continue
                except json.JSONDecodeError:
                    log("Could not parse raw_output as JSON, continuing with regular processing.")
        else:
            log(f"Task {i+1} had no recognizable output content.")
            continue
        
        if isinstance(actual_output, UICodeOutput):
            log(f"Task output is UICodeOutput: {actual_output.filename}")
            ui_code_dict[actual_output.filename] = actual_output.code
            if actual_output.description:
                log(f"Description: {actual_output.description}")
        elif isinstance(actual_output, AgentConfigOutput):
            log(f"Task output is AgentConfigOutput")
            log(f"Agent Type: {actual_output.agent_type}")
            log(f"Key Capabilities: {', '.join(actual_output.key_capabilities)}")
            log(f"Recommended Design System: {actual_output.recommended_design_system}")
        elif isinstance(actual_output, UIComponentsOutput):
            log(f"Task output is UIComponentsOutput")
            log(f"Components: {', '.join(actual_output.components)}")
            log(f"Layout Structure: {actual_output.layout_structure}")
            # Store design tokens for later use in CSS generation
            ui_code_dict['design_tokens.json'] = json.dumps(actual_output.design_tokens, indent=2)
        elif isinstance(actual_output, str):
            log(f"Task output {i+1} was a raw string. Attempting to parse as code.")
            # Try to determine file type based on content
            if "<html" in actual_output or "<!DOCTYPE" in actual_output:
                ui_code_dict["index.html"] = actual_output
                log("Detected HTML content and saved as index.html")
            elif "{" in actual_output and "}" in actual_output and ("color" in actual_output or "margin" in actual_output):
                ui_code_dict["styles.css"] = actual_output
                log("Detected CSS content and saved as styles.css")
            elif "function" in actual_output or "const" in actual_output or "let" in actual_output:
                ui_code_dict["app.js"] = actual_output
                log("Detected JavaScript content and saved as app.js")
            else:
                ui_code_dict[f"task_{i+1}_raw_output.txt"] = actual_output
                log("Could not determine file type, saved as raw output")
        else:
            log(f"Task output {i+1} was not a recognized Pydantic model nor a raw string.")
    
    # If no UI code was generated, try to extract from raw results
    if not ui_code_dict:
        log("No structured UI code was extracted. Attempting regex-based extraction...")
        
        for i, task_instance in enumerate(ui_generator_crew.tasks):
            if hasattr(task_instance, '_result') and task_instance._result:
                raw_result = str(task_instance._result)
                
                # Look for code blocks in markdown format (capture language)
                blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', raw_result, re.DOTALL)
                
                if blocks:
                    for j, (lang, code_block) in enumerate(blocks):
                        lang = (lang or '').lower()
                        # Handle JSON blocks that contain {"filename": ..., "code": ...}
                        if lang == 'json':
                            try:
                                parsed = json.loads(code_block)
                                if isinstance(parsed, dict) and 'filename' in parsed and 'code' in parsed:
                                    filename = parsed['filename']
                                    ui_code_dict[filename] = parsed['code']
                                    log(f"Extracted JSON block with filename: {filename}")
                                    continue
                            except Exception:
                                # Not a clean JSON payload, fall back to type inference
                                pass
                        
                        # Try to determine file type based on content
                        if "<html" in code_block or "<!DOCTYPE" in code_block:
                            filename = "index.html"
                        elif "{" in code_block and "}" in code_block and ("color" in code_block or "margin" in code_block):
                            filename = "styles.css"
                        elif "function" in code_block or "const" in code_block or "let" in code_block:
                            filename = "app.js"
                        else:
                            filename = f"code_block_{j+1}.txt"
                        
                        log(f"Extracted code block as {filename}")
                        ui_code_dict[filename] = code_block.strip()
    
    return True, ui_code_dict, logs

def save_files(ui_code_dict, output_dir):
    """Save the generated UI files to the specified directory."""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    # Save each file
    for filename, content in ui_code_dict.items():
        file_path = output_path / filename
        with open(file_path, 'w') as f:
            f.write(content)
        saved_files.append(str(file_path))
    
    # Create a simple preview HTML if index.html doesn't exist
    if "index.html" not in ui_code_dict:
        preview_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Generated UI Preview</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <h1>Generated UI Components</h1>
            <div id="app"></div>
            <script src="app.js"></script>
        </body>
        </html>
        """
        preview_path = output_path / "preview.html"
        with open(preview_path, 'w') as f:
            f.write(preview_html)
        saved_files.append(str(preview_path))
    
    return saved_files

def main():
    """Main entry point for the CLI application."""
    args = parse_arguments()
    
    print(f"\n{'=' * 60}")
    print(f"🤖 AI Agent UI/UX Generator CLI")
    print(f"{'=' * 60}\n")
    
    print("📋 Generation Parameters:")
    print(f"  • Agent Description: {args.agent_description[:50]}...")
    print(f"  • Agent Capabilities: {args.agent_capabilities[:50]}...")
    print(f"  • Theme: {args.theme}")
    print(f"  • Layout: {args.layout}")
    print(f"  • Color Scheme: {args.color_scheme}")
    print(f"  • Output Directory: {args.output_dir}\n")
    
    print("🚀 Starting UI/UX generation process...")
    success, ui_code_dict, logs = generate_ui(args)
    
    if not success:
        print("\n❌ UI/UX generation failed. See logs for details.")
        print("\n📝 Logs:")
        for log in logs:
            print(f"  • {log}")
        return 1
    
    if not ui_code_dict:
        print("\n⚠️ No UI code was generated.")
        return 1
    
    print("\n✅ UI/UX generation completed successfully!")
    print(f"\n📦 Generated {len(ui_code_dict)} files:")
    for filename in ui_code_dict.keys():
        print(f"  • {filename}")
    
    saved_files = save_files(ui_code_dict, args.output_dir)
    
    print(f"\n💾 Files saved to: {args.output_dir}")
    for file_path in saved_files:
        print(f"  • {file_path}")
    
    print("\n🎉 Done! You can now use the generated UI/UX files in your project.")
    
    return 0

if __name__ == "__main__":
    exit(main())
