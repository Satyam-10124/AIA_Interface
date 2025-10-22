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
from ui_generator_crew import (
    ui_generator_crew,
    web3_ui_generator_crew,       # PHASE 2.5: Web3-enabled crew
    AgentConfigOutput,
    UIComponentsOutput,
    UICodeOutput,
    QAReportOutput,               # PHASE 1: QA Report
    AccessibilityReportOutput,    # PHASE 1: Accessibility Report
    RevisedCodeOutput,            # PHASE 2: Revised Code
    PerformanceReportOutput,      # PHASE 2: Performance Report
    ContractInterfaceOutput,      # PHASE 2.5: Parsed contract interface
    Web3IntegrationOutput         # PHASE 2.5: Web3 integration code
)

# Import utilities
from utils.environment_validator import validate_or_exit
from utils.output_extractor import OutputExtractor

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
    
    # PHASE 2.5: Web3 & Smart Contract integration group
    web3_group = parser.add_argument_group('Web3 & Smart Contract Integration (Phase 2.5)')
    
    web3_group.add_argument(
        "--contract-address",
        type=str,
        default="",
        help="Smart contract address (e.g., 0x742d35...)"
    )
    
    web3_group.add_argument(
        "--contract-abi",
        type=str,
        default="",
        help="Path to contract ABI JSON file or JSON string"
    )
    
    web3_group.add_argument(
        "--network",
        type=str,
        choices=["mainnet", "sepolia", "goerli", "polygon", "mumbai", "arbitrum", "optimism", "bsc"],
        default="sepolia",
        help="Blockchain network for contract deployment"
    )
    
    parser.add_argument(
        "--output-name", "-on",
        type=str,
        default="default_ui",
        help="Name for the generated UI project (creates subdirectory)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./generated_ui",
        help="Base directory to save generated UI files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output and diagnostics"
    )
    
    return parser.parse_args()

def generate_ui(args):
    """Generate UI/UX based on the provided arguments."""
    # PHASE 2.5: Check if Web3 mode is enabled
    web3_mode = bool(args.contract_address and args.contract_abi)
    
    # Load contract ABI if provided
    contract_abi_data = ""
    if web3_mode:
        # Check if contract_abi is a file path or JSON string
        if os.path.isfile(args.contract_abi):
            with open(args.contract_abi, 'r') as f:
                contract_abi_data = f.read()
        else:
            contract_abi_data = args.contract_abi
    
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
    
    # PHASE 2.5: Add Web3 config if in Web3 mode
    if web3_mode:
        config["contract_address"] = args.contract_address
        config["contract_abi"] = contract_abi_data
        config["network"] = args.network
    
    ui_code_dict = {}
    logs = []
    
    def log(message):
        """Log a message and add it to the logs list."""
        logs.append(message)
        if args.verbose:
            logger.info(message)
    
    log(f"Processing UI generation request for agent: {config['agent_description'][:100]}...")
    
    # PHASE 2.5: Log Web3 mode status
    if web3_mode:
        log(f"🔗 Web3 Mode ENABLED")
        log(f"   Contract: {args.contract_address}")
        log(f"   Network: {args.network}")
        log(f"   Using Web3-enhanced agent pipeline")
    
    # Log custom design preferences if provided
    if config['user_preferences']['custom_design']:
        log(f"Custom design preferences: {config['user_preferences']['custom_design']}")
    
    # PHASE 2.5: Select appropriate crew based on mode
    selected_crew = web3_ui_generator_crew if web3_mode else ui_generator_crew
    pipeline_desc = "Analysis → Design → Contract Parsing → Web3 Integration → HTML → CSS → JavaScript" if web3_mode else "Analysis → Design → HTML → CSS → JavaScript"
    
    # Kickoff AI crew for UI generation
    log(f"Starting crewAI agents to analyze agent requirements and generate UI/UX...")
    log(f"Agent pipeline: {pipeline_desc}")
    try:
        crew_result = selected_crew.kickoff(inputs=config)
        log("Crew kickoff completed successfully.")
    except Exception as e:
        error_msg = f"Error during crew execution: {str(e)}\n{traceback.format_exc()}"
        log(error_msg)
        logger.error(error_msg)
        return False, ui_code_dict, logs
    
    # Process task outputs
    if not selected_crew.tasks:
        log("Warning: No tasks found in the crew definition.")
        return False, ui_code_dict, logs
    
    log(f"Processing outputs from {len(selected_crew.tasks)} AI agent tasks.")
    
    # Show diagnostic info if verbose
    if args.verbose:
        OutputExtractor.diagnostic_dump(selected_crew, log)
    
    # Extract outputs using the new robust extractor
    qa_report = None
    accessibility_report = None
    revised_code = None
    performance_report = None
    contract_interface = None  # PHASE 2.5
    web3_integration = None    # PHASE 2.5
    
    for i, task_instance in enumerate(selected_crew.tasks):
        task_output_item = task_instance.output
        
        if not task_output_item:
            log(f"Task {i+1} has no output object.")
            continue
        
        log(f"Processing output for task {i+1}: {task_instance.description[:50]}...")
        
        # Get actual output for analysis
        actual_output = None
        if hasattr(task_output_item, 'pydantic') and task_output_item.pydantic:
            actual_output = task_output_item.pydantic
        elif hasattr(task_output_item, 'exported_output') and task_output_item.exported_output:
            actual_output = task_output_item.exported_output
        elif hasattr(task_output_item, 'raw_output') and task_output_item.raw_output:
            actual_output = task_output_item.raw_output
        
        # Debug: Log output type
        if args.verbose and actual_output:
            log(f"Task {i+1} output type: {type(actual_output).__name__}")
        
        # Check output type
        if isinstance(actual_output, ContractInterfaceOutput):  # PHASE 2.5
            contract_interface = actual_output
            log(f"✅ Contract Interface parsed - Contract: {contract_interface.contract_name}")
            log(f"   Read functions: {len(contract_interface.read_functions)}, Write functions: {len(contract_interface.write_functions)}")
            log(f"   Events: {len(contract_interface.events)}, Roles: {len(contract_interface.roles)}")
        elif isinstance(actual_output, Web3IntegrationOutput):  # PHASE 2.5
            web3_integration = actual_output
            log(f"✅ Web3 Integration code generated")
            log(f"   Wallet connection: ✓, Contract wrapper: ✓")
            log(f"   Event listeners: {len(web3_integration.event_listeners)}")
            log(f"   Required libraries: {', '.join(web3_integration.required_libraries)}")
        elif isinstance(actual_output, QAReportOutput):
            qa_report = actual_output
            log(f"✅ QA Report received - Passed: {qa_report.passed}")
        elif isinstance(actual_output, AccessibilityReportOutput):
            accessibility_report = actual_output
            log(f"✅ Accessibility Report received - WCAG Level: {accessibility_report.wcag_level}")
        elif isinstance(actual_output, RevisedCodeOutput):
            revised_code = actual_output
            log(f"✅ Revised Code received - Fixes applied: {len(revised_code.fixes_applied)}")
            # Replace original code with revised code
            ui_code_dict['index.html'] = revised_code.html_code
            ui_code_dict['styles.css'] = revised_code.css_code
            ui_code_dict['app.js'] = revised_code.js_code
        elif isinstance(actual_output, PerformanceReportOutput):
            performance_report = actual_output
            log(f"✅ Performance Report received - Score: {performance_report.lighthouse_score_estimate}/100")
        elif isinstance(actual_output, AgentConfigOutput):
            log(f"Task output is AgentConfigOutput")
            log(f"  Agent Type: {actual_output.agent_type}")
            log(f"  Key Capabilities: {', '.join(actual_output.key_capabilities[:3])}...")
            log(f"  Recommended Design System: {actual_output.recommended_design_system}")
        elif isinstance(actual_output, UIComponentsOutput):
            log(f"Task output is UIComponentsOutput")
            log(f"  Components: {', '.join(actual_output.components[:5])}...")
            log(f"  Layout Structure: {actual_output.layout_structure[:80]}...")
            # Store design tokens for reference
            ui_code_dict['design_tokens.json'] = json.dumps(actual_output.design_tokens, indent=2)
        elif i >= 2 and i <= 4:  # HTML, CSS, JS tasks (tasks 3, 4, 5)
            # Check if this is a code generation task
            success, filename, code = OutputExtractor.extract_ui_code(task_output_item, i+1, log)
            
            if success and filename and code:
                ui_code_dict[filename] = code
                log(f"📝 Saved {filename} ({len(code)} characters)")
            else:
                log(f"⚠️  Failed to extract code from task {i+1}")
    
    return True, ui_code_dict, logs, qa_report, accessibility_report, revised_code, performance_report, contract_interface, web3_integration

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

def generate_readme(output_path, args, contract_interface, web3_integration):
    """Auto-generate README.md with setup and deployment instructions (per user's memory preference)."""
    readme_path = output_path / "README.md"
    
    web3_mode = bool(contract_interface and web3_integration)
    
    readme_content = f"""# {args.output_name.replace('-', ' ').title()}

**Generated by AI Agent UI/UX Generator**

## 📋 Overview

{args.agent_description}

### Key Capabilities
{chr(10).join(f"- {cap.strip()}" for cap in args.agent_capabilities.split(','))}

---

## 🚀 Quick Start

### Option 1: Open Directly in Browser

```bash
# Navigate to this directory
cd {output_path.name}

# Start a simple HTTP server
python3 -m http.server 8000

# Open in browser
open http://localhost:8000
```

### Option 2: Deploy to Production

Deploy to any static hosting service:
- **Vercel**: `vercel --prod`
- **Netlify**: Drag and drop this folder to netlify.com/drop
- **GitHub Pages**: Push to a gh-pages branch
- **Surge**: `surge .`

---
"""

    if web3_mode:
        readme_content += f"""## 🔗 Web3 Configuration

### Contract Details
- **Address**: `{contract_interface.contract_address}`
- **Network**: {contract_interface.network}
- **Contract Type**: {contract_interface.contract_name}

### Functions Available
- **Read Functions**: {len(contract_interface.read_functions)} (view/pure)
- **Write Functions**: {len(contract_interface.write_functions)} (state-changing)
- **Events**: {len(contract_interface.events)}
- **Access Roles**: {len(contract_interface.roles) if contract_interface.roles else 0}

### Prerequisites
1. **MetaMask Wallet** (or any Web3 wallet)
   - Install from https://metamask.io
   - Create or import a wallet
   - Switch to {contract_interface.network} network

2. **Test Funds** (for {contract_interface.network})
   - Get testnet ETH from a faucet
   - https://sepoliafaucet.com (for Sepolia)
   - https://faucet.polygon.technology (for Mumbai)

### Required Libraries
{chr(10).join(f"- {lib}" for lib in web3_integration.required_libraries)}

**All libraries are loaded via CDN in the HTML file. No npm install needed!**

---

## 🛠️ Customization

### Change Contract Address
Edit `app.js` and update:
```javascript
const CONTRACT_ADDRESS = '{contract_interface.contract_address}'; // Update this
```

### Change Network
Edit `network-config.json` or update in `app.js`:
```javascript
const NETWORK_CONFIG = {{
  chainId: '0x...', // Update chain ID
  name: 'Your Network',
  rpcUrl: 'https://...',
  // ...
}};
```

### Modify Contract Functions
The contract wrapper class in `contract-wrapper.js` includes methods for:

**Read Functions:**
{chr(10).join(f"- `{func.get('name', 'unknown')}()` - {func.get('description', 'No description')}" for func in contract_interface.read_functions[:5])}

**Write Functions:**
{chr(10).join(f"- `{func.get('name', 'unknown')}()` - {func.get('description', 'No description')}" for func in contract_interface.write_functions[:5])}

---
"""

    readme_content += f"""## 📂 Project Structure

```
{output_path.name}/
├── index.html          # Main HTML structure
├── styles.css          # Styling with design tokens
├── app.js              # JavaScript logic{'and Web3 integration' if web3_mode else ''}
├── design_tokens.json  # Design system configuration
├── README.md           # This file
"""

    if web3_mode:
        readme_content += """├── web3-wallet.js      # Wallet connection logic
├── contract-wrapper.js # Smart contract wrapper
├── network-config.json # Network configuration
"""

    readme_content += f"""└── reports/            # Generation reports
    ├── qa_report.json
    ├── accessibility_report.json
    ├── code_revision.json
    ├── performance_report.json
"""

    if web3_mode:
        readme_content += """    ├── contract_interface.json
    └── web3_integration.json
"""

    readme_content += """```

---

## 🎨 Design System

**Theme**: {theme}  
**Layout**: {layout}  
**Color Scheme**: {color}  

All design tokens are defined in `design_tokens.json` and can be customized.

---

## 📊 Quality Reports

This UI has been automatically tested and optimized:

✅ **QA Testing**: Syntax validation, bug detection, code quality  
✅ **Accessibility**: WCAG 2.1 AA compliance  
✅ **Code Revision**: Auto-fixed issues from QA and accessibility  
✅ **Performance**: Optimized for production (minified, lazy-loaded)  

View detailed reports in the `reports/` directory.

---

## 🐛 Troubleshooting

""".format(theme=args.theme, layout=args.layout, color=args.color_scheme)

    if web3_mode:
        readme_content += """### MetaMask Not Detected
- Ensure MetaMask extension is installed
- Reload the page after installing
- Check browser console for errors

### Wrong Network
- Click "Connect Wallet" - it will prompt to switch networks
- Or manually switch in MetaMask to {network}

### Transaction Fails
- Check you have enough testnet ETH for gas
- Verify contract address is correct
- Check if you have required role/permissions

### Functions Not Showing
- Contract may require role-based access
- Connect with an authorized wallet
- Check contract_interface.json for role requirements

""".format(network=contract_interface.network)

    readme_content += """### Styling Issues
- Clear browser cache
- Check console for CSS errors
- Verify all files are in the same directory

### General Issues
- Open browser console (F12) to see error messages
- Check that all files are loaded correctly
- Verify network connectivity

---

## 📝 License

Auto-generated UI - Free to use and modify

---

## 🙏 Credits

Generated by **AI Agent UI/UX Generator**  
- Uses CrewAI for multi-agent orchestration
- Powered by Google Gemini 2.5 Pro
"""

    if web3_mode:
        readme_content += "- Web3 integration with ethers.js v6\n"

    readme_content += f"""
---

**Generated on**: {Path(__file__).stat().st_mtime}  
**Agent Description**: {args.agent_description[:100]}...
"""

    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"  • {readme_path} (README)")

def generate_requirements_txt(output_path, web3_integration):
    """Auto-generate requirements.txt with required dependencies (per user's memory preference)."""
    requirements_path = output_path / "requirements.txt"
    
    # For HTML/CSS/JS projects, this lists JavaScript libraries (for documentation)
    requirements_content = """# JavaScript Dependencies (Loaded via CDN)
# This file documents the libraries used in this project.
# All libraries are loaded directly from CDN in the HTML file.
# No npm install or package manager needed for this vanilla JS project!

"""

    if web3_integration:
        requirements_content += f"""# Web3 Libraries
{chr(10).join(f"# - {lib}" for lib in web3_integration.required_libraries)}

# Additional Web3 Tools (optional)
# - @walletconnect/web3-provider@latest
# - web3modal@latest

"""

    requirements_content += """# If you want to convert to a Node.js project:
# npm install ethers@6.0.0
# npm install web3modal@3.0.0

# For local development server:
# npm install -g http-server
# OR use: python3 -m http.server 8000
"""

    with open(requirements_path, 'w') as f:
        f.write(requirements_content)
    
    print(f"  • {requirements_path} (Requirements)")

def main():
    """Main entry point for the CLI application."""
    args = parse_arguments()
    
    print(f"\n{'=' * 60}")
    print(f"🤖 AI Agent UI/UX Generator CLI")
    print(f"{'=' * 60}\n")
    
    # Construct full output path
    output_path = Path(args.output_dir) / args.output_name
    
    # 🔥 NEW: Pre-flight validation
    validate_or_exit(output_dir=output_path)
    
    print("📋 Generation Parameters:")
    print(f"  • Agent Description: {args.agent_description[:50]}...")
    print(f"  • Agent Capabilities: {args.agent_capabilities[:50]}...")
    print(f"  • Theme: {args.theme}")
    print(f"  • Layout: {args.layout}")
    print(f"  • Color Scheme: {args.color_scheme}")
    print(f"  • Output Directory: {output_path}")
    
    # PHASE 2.5: Show Web3 parameters if in Web3 mode
    if args.contract_address and args.contract_abi:
        print(f"\n🔗 Web3 Mode:")
        print(f"  • Contract Address: {args.contract_address}")
        print(f"  • Network: {args.network}")
        print(f"  • ABI Source: {'File' if os.path.isfile(args.contract_abi) else 'String'}")
    
    print("\n🚀 Starting UI/UX generation process...")
    success, ui_code_dict, logs, qa_report, accessibility_report, revised_code, performance_report, contract_interface, web3_integration = generate_ui(args)
    
    if not success:
        print("\n❌ UI/UX generation failed. See logs for details.")
        print("\n📝 Logs:")
        for log in logs:
            print(f"  • {log}")
        return 1
    
    if not ui_code_dict:
        print("\n⚠️ No UI code was generated.")
        print("\n💡 Troubleshooting:")
        print("   1. Run with --verbose to see detailed extraction logs")
        print("   2. Check that GEMINI_API_KEY is valid")
        print("   3. Ensure you have network connectivity")
        print("\n📝 Logs:")
        for log_msg in logs[-10:]:  # Show last 10 log messages
            print(f"  • {log_msg}")
        return 1
    
    print("\n✅ UI/UX generation completed successfully!")
    print(f"\n📦 Generated {len(ui_code_dict)} files:")
    for filename in ui_code_dict.keys():
        print(f"  • {filename}")
    
    # PHASE 1: Display QA Report
    if qa_report:
        print("\n" + "=" * 60)
        print("🧪 QUALITY ASSURANCE REPORT")
        print("=" * 60)
        
        if qa_report.passed:
            print("✅ Overall Status: PASSED")
        else:
            print("❌ Overall Status: FAILED")
        
        print(f"\n📊 Validation Results:")
        print(f"  • HTML Valid: {'✅' if qa_report.html_valid else '❌'}")
        print(f"  • CSS Valid: {'✅' if qa_report.css_valid else '❌'}")
        print(f"  • JavaScript Valid: {'✅' if qa_report.js_valid else '❌'}")
        print(f"  • Syntax Valid: {'✅' if qa_report.syntax_valid else '❌'}")
        
        if qa_report.issues_found:
            print(f"\n⚠️  Issues Found ({len(qa_report.issues_found)}):")
            for issue in qa_report.issues_found[:5]:  # Show first 5
                print(f"  • {issue}")
            if len(qa_report.issues_found) > 5:
                print(f"  ... and {len(qa_report.issues_found) - 5} more")
        else:
            print("\n✅ No issues found!")
        
        if qa_report.severity_levels:
            print(f"\n📈 Severity Breakdown:")
            for severity, count in qa_report.severity_levels.items():
                emoji = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                print(f"  {emoji} {severity.capitalize()}: {count}")
        
        if qa_report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in qa_report.recommendations[:3]:  # Show first 3
                print(f"  • {rec}")
            if len(qa_report.recommendations) > 3:
                print(f"  ... and {len(qa_report.recommendations) - 3} more")
    
    # PHASE 1: Display Accessibility Report
    if accessibility_report:
        print("\n" + "=" * 60)
        print("♿ ACCESSIBILITY AUDIT REPORT")
        print("=" * 60)
        
        print(f"\n🏆 WCAG Compliance Level: {accessibility_report.wcag_level}")
        
        if accessibility_report.passed:
            print("✅ Status: Meets WCAG 2.1 AA Standards")
        else:
            print("❌ Status: Does NOT meet WCAG 2.1 AA Standards")
        
        print(f"\n📊 Accessibility Scores:")
        print(f"  • ARIA Implementation: {accessibility_report.aria_score}/100")
        print(f"  • Keyboard Navigable: {'✅' if accessibility_report.keyboard_navigable else '❌'}")
        print(f"  • Screen Reader Compatible: {'✅' if accessibility_report.screen_reader_compatible else '❌'}")
        print(f"  • Color Contrast (4.5:1): {'✅' if accessibility_report.contrast_ratio_passed else '❌'}")
        print(f"  • Semantic HTML5: {'✅' if accessibility_report.semantic_html_used else '❌'}")
        
        if accessibility_report.violations:
            print(f"\n⚠️  Violations Found ({len(accessibility_report.violations)}):")
            for violation in accessibility_report.violations[:3]:  # Show first 3
                element = violation.get('element', 'Unknown')
                guideline = violation.get('guideline', 'N/A')
                severity = violation.get('severity', 'medium')
                fix = violation.get('fix', 'No fix provided')
                print(f"  • [{severity.upper()}] {element}")
                print(f"    Guideline: WCAG {guideline}")
                print(f"    Fix: {fix[:100]}..." if len(fix) > 100 else f"    Fix: {fix}")
            if len(accessibility_report.violations) > 3:
                print(f"  ... and {len(accessibility_report.violations) - 3} more violations")
        else:
            print("\n✅ No accessibility violations found!")
        
        if accessibility_report.recommendations:
            print(f"\n💡 Improvement Recommendations:")
            for rec in accessibility_report.recommendations[:3]:  # Show first 3
                print(f"  • {rec}")
            if len(accessibility_report.recommendations) > 3:
                print(f"  ... and {len(accessibility_report.recommendations) - 3} more")
    
    # PHASE 2: Display Code Revision Report
    if revised_code:
        print("\n" + "=" * 60)
        print("🔧 CODE REVISION REPORT")
        print("=" * 60)
        
        if revised_code.issues_remaining:
            print(f"⚠️  Status: {len(revised_code.issues_remaining)} issues could not be auto-fixed")
        else:
            print("✅ Status: All issues successfully fixed!")
        
        print(f"\n📝 Fixes Applied ({len(revised_code.fixes_applied)}):")
        for fix in revised_code.fixes_applied[:10]:  # Show first 10
            print(f"  ✓ {fix}")
        if len(revised_code.fixes_applied) > 10:
            print(f"  ... and {len(revised_code.fixes_applied) - 10} more fixes")
        
        if revised_code.issues_remaining:
            print(f"\n⚠️  Issues Remaining ({len(revised_code.issues_remaining)}):")
            for issue in revised_code.issues_remaining[:5]:
                print(f"  • {issue}")
            if len(revised_code.issues_remaining) > 5:
                print(f"  ... and {len(revised_code.issues_remaining) - 5} more")
    
    # PHASE 2: Display Performance Report
    if performance_report:
        print("\n" + "=" * 60)
        print("⚡ PERFORMANCE OPTIMIZATION REPORT")
        print("=" * 60)
        
        if performance_report.optimized:
            print("✅ Status: Code successfully optimized for production")
        else:
            print("⚠️  Status: Some optimizations could not be applied")
        
        print(f"\n📊 Performance Metrics:")
        print(f"  • Lighthouse Score (Estimate): {performance_report.lighthouse_score_estimate}/100")
        print(f"  • Bundle Size Reduction: {performance_report.bundle_size_reduction}")
        
        print(f"\n🚀 Optimizations Applied ({len(performance_report.optimizations_applied)}):")
        for opt in performance_report.optimizations_applied[:10]:  # Show first 10
            print(f"  ⚡ {opt}")
        if len(performance_report.optimizations_applied) > 10:
            print(f"  ... and {len(performance_report.optimizations_applied) - 10} more optimizations")
        
        if performance_report.recommendations:
            print(f"\n💡 Additional Recommendations:")
            for rec in performance_report.recommendations[:3]:  # Show first 3
                print(f"  • {rec}")
            if len(performance_report.recommendations) > 3:
                print(f"  ... and {len(performance_report.recommendations) - 3} more")
    
    # PHASE 2.5: Add Web3 integration files to ui_code_dict before saving
    if web3_integration:
        # Save wallet connection code as separate file
        ui_code_dict['web3-wallet.js'] = web3_integration.wallet_connection_code
        
        # Save contract wrapper code
        ui_code_dict['contract-wrapper.js'] = web3_integration.contract_wrapper_code
        
        # Save network config as JSON
        ui_code_dict['network-config.json'] = json.dumps(web3_integration.network_config, indent=2)
        
        # Merge Web3 code into main app.js (or create web3-integration.js)
        if 'app.js' in ui_code_dict:
            # Append Web3 code to existing app.js
            ui_code_dict['app.js'] += "\n\n// === WEB3 INTEGRATION (Auto-generated) ===\n\n"
            ui_code_dict['app.js'] += web3_integration.wallet_connection_code + "\n\n"
            ui_code_dict['app.js'] += web3_integration.contract_wrapper_code + "\n\n"
            
            # Add event listeners
            if web3_integration.event_listeners:
                ui_code_dict['app.js'] += "// === CONTRACT EVENT LISTENERS ===\n\n"
                for listener in web3_integration.event_listeners:
                    ui_code_dict['app.js'] += listener + "\n\n"
    
    saved_files = save_files(ui_code_dict, output_path)
    
    print("\n" + "=" * 60)
    print(f"💾 FILES SAVED TO: {output_path}")
    print("=" * 60)
    for file_path in saved_files:
        print(f"  • {file_path}")
    
    # Save reports as JSON
    if qa_report or accessibility_report or revised_code or performance_report or contract_interface or web3_integration:
        reports_path = output_path / "reports"
        reports_path.mkdir(exist_ok=True)
        
        if qa_report:
            qa_file = reports_path / "qa_report.json"
            with open(qa_file, 'w') as f:
                json.dump(qa_report.dict(), f, indent=2)
            print(f"  • {qa_file} (QA Report)")
        
        if accessibility_report:
            a11y_file = reports_path / "accessibility_report.json"
            with open(a11y_file, 'w') as f:
                json.dump(accessibility_report.dict(), f, indent=2)
            print(f"  • {a11y_file} (Accessibility Report)")
        
        if revised_code:
            revision_file = reports_path / "code_revision.json"
            with open(revision_file, 'w') as f:
                json.dump({
                    "fixes_applied": revised_code.fixes_applied,
                    "issues_remaining": revised_code.issues_remaining
                }, f, indent=2)
            print(f"  • {revision_file} (Code Revision Report)")
        
        if performance_report:
            perf_file = reports_path / "performance_report.json"
            with open(perf_file, 'w') as f:
                json.dump(performance_report.dict(), f, indent=2)
            print(f"  • {perf_file} (Performance Report)")
        
        # PHASE 2.5: Save Web3 reports
        if contract_interface:
            contract_file = reports_path / "contract_interface.json"
            with open(contract_file, 'w') as f:
                json.dump(contract_interface.dict(), f, indent=2)
            print(f"  • {contract_file} (Contract Interface)")
        
        if web3_integration:
            web3_file = reports_path / "web3_integration.json"
            with open(web3_file, 'w') as f:
                json.dump(web3_integration.dict(), f, indent=2)
            print(f"  • {web3_file} (Web3 Integration Details)")
    
    # PHASE 2.5: Auto-generate README.md and requirements.txt (per user's memory preference)
    generate_readme(output_path, args, contract_interface, web3_integration)
    generate_requirements_txt(output_path, web3_integration)
    
    if web3_integration:
        print("\n🎉 Done! Your Web3 dApp UI is ready with full smart contract integration!")
        print("\n📚 Next Steps:")
        print("  1. Read the generated README.md for deployment instructions")
        print("  2. Install dependencies from requirements.txt")
        print("  3. Update the contract address if deploying to a different network")
        print("  4. Open index.html in a browser with MetaMask installed")
    elif revised_code and performance_report:
        print("\n🎉 Done! Your UI has been tested, fixed, optimized, and is production-ready!")
    else:
        print("\n🎉 Done! Your UI has been tested for quality and accessibility.")
    
    return 0

if __name__ == "__main__":
    exit(main())
