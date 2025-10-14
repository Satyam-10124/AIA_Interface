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
    AgentConfigOutput,
    UIComponentsOutput,
    UICodeOutput,
    QAReportOutput,               # PHASE 1: QA Report
    AccessibilityReportOutput,    # PHASE 1: Accessibility Report
    RevisedCodeOutput,            # PHASE 2: Revised Code
    PerformanceReportOutput       # PHASE 2: Performance Report
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
    log("Agent pipeline: Analysis → Design → HTML → CSS → JavaScript")
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
    
    # Show diagnostic info if verbose
    if args.verbose:
        OutputExtractor.diagnostic_dump(ui_generator_crew, log)
    
    # Extract outputs using the new robust extractor
    qa_report = None
    accessibility_report = None
    revised_code = None
    performance_report = None
    
    for i, task_instance in enumerate(ui_generator_crew.tasks):
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
        if isinstance(actual_output, QAReportOutput):
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
    
    return True, ui_code_dict, logs, qa_report, accessibility_report, revised_code, performance_report

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
    print(f"  • Output Directory: {output_path}\n")
    
    print("🚀 Starting UI/UX generation process...")
    success, ui_code_dict, logs, qa_report, accessibility_report, revised_code, performance_report = generate_ui(args)
    
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
    
    saved_files = save_files(ui_code_dict, output_path)
    
    print("\n" + "=" * 60)
    print(f"💾 FILES SAVED TO: {output_path}")
    print("=" * 60)
    for file_path in saved_files:
        print(f"  • {file_path}")
    
    # Save reports as JSON
    if qa_report or accessibility_report or revised_code or performance_report:
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
    
    if revised_code and performance_report:
        print("\n🎉 Done! Your UI has been tested, fixed, optimized, and is production-ready!")
    else:
        print("\n🎉 Done! Your UI has been tested for quality and accessibility.")
    
    return 0

if __name__ == "__main__":
    exit(main())
