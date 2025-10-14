"""
Robust output extraction utilities for parsing CrewAI task outputs.
Implements multiple fallback strategies to ensure code is harvested reliably.
"""
import json
import re
from typing import Tuple, Optional, Any


class OutputExtractor:
    """
    Multi-strategy extractor for CrewAI task outputs.
    Handles various output formats with intelligent fallbacks.
    """
    
    @staticmethod
    def extract_ui_code(task_output, task_index: int, log_fn=None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract filename and code from a UI generation task output.
        
        Args:
            task_output: The task output object from CrewAI
            task_index: Index of the task (for logging)
            log_fn: Optional logging function
        
        Returns:
            (success: bool, filename: Optional[str], code: Optional[str])
        """
        def log(msg):
            if log_fn:
                log_fn(msg)
        
        if not task_output:
            log(f"❌ Task {task_index}: No output object")
            return False, None, None
        
        # Strategy 1: Pydantic exported_output
        if hasattr(task_output, 'exported_output') and task_output.exported_output:
            output = task_output.exported_output
            
            # Check if it has filename and code attributes
            if hasattr(output, 'filename') and hasattr(output, 'code'):
                log(f"✅ Task {task_index}: Extracted via Pydantic exported_output")
                return True, output.filename, output.code
        
        # Strategy 2: Parse raw_output as JSON
        if hasattr(task_output, 'raw_output') and task_output.raw_output:
            raw = task_output.raw_output
            
            if isinstance(raw, str):
                # Try direct JSON parsing
                success, filename, code = OutputExtractor._try_json_parse(raw, task_index, log)
                if success:
                    return True, filename, code
                
                # Try markdown JSON block extraction
                success, filename, code = OutputExtractor._extract_json_from_markdown(raw, task_index, log)
                if success:
                    return True, filename, code
        
        # Strategy 3: Check 'text' property (CrewAI sometimes uses this)
        if hasattr(task_output, 'text') and task_output.text:
            text = task_output.text
            
            if isinstance(text, str):
                # Try JSON parsing on text
                success, filename, code = OutputExtractor._try_json_parse(text, task_index, log)
                if success:
                    log(f"✅ Task {task_index}: Extracted from .text property")
                    return True, filename, code
                
                # Try markdown extraction
                success, filename, code = OutputExtractor._extract_json_from_markdown(text, task_index, log)
                if success:
                    log(f"✅ Task {task_index}: Extracted from .text markdown")
                    return True, filename, code
        
        # Strategy 4: Check pydantic property (alternate property name)
        if hasattr(task_output, 'pydantic') and task_output.pydantic:
            pyd = task_output.pydantic
            if hasattr(pyd, 'filename') and hasattr(pyd, 'code'):
                log(f"✅ Task {task_index}: Extracted via .pydantic property")
                return True, pyd.filename, pyd.code
        
        log(f"❌ Task {task_index}: All extraction strategies failed")
        return False, None, None
    
    @staticmethod
    def _try_json_parse(text: str, task_index: int, log_fn) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Attempt to parse text as JSON containing filename and code.
        """
        try:
            data = json.loads(text)
            if isinstance(data, dict) and 'filename' in data and 'code' in data:
                if log_fn:
                    log_fn(f"✅ Task {task_index}: Parsed JSON from string")
                return True, data['filename'], data['code']
        except (json.JSONDecodeError, ValueError):
            pass
        
        return False, None, None
    
    @staticmethod
    def _extract_json_from_markdown(text: str, task_index: int, log_fn) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract JSON from markdown code blocks (```json ... ```).
        """
        # Find JSON code blocks
        json_blocks = re.findall(r'```json\s*\n([\s\S]*?)\n```', text, re.DOTALL | re.IGNORECASE)
        
        for block in json_blocks:
            try:
                data = json.loads(block)
                if isinstance(data, dict) and 'filename' in data and 'code' in data:
                    if log_fn:
                        log_fn(f"✅ Task {task_index}: Extracted from markdown JSON block")
                    return True, data['filename'], data['code']
            except (json.JSONDecodeError, ValueError):
                continue
        
        return False, None, None
    
    @staticmethod
    def diagnostic_dump(crew, log_fn=None):
        """
        Debug helper to understand what crew actually returns.
        
        Args:
            crew: The Crew object with completed tasks
            log_fn: Optional logging function
        """
        def log(msg):
            if log_fn:
                log_fn(msg)
            else:
                print(msg)
        
        log("\n" + "="*60)
        log("🔍 DIAGNOSTIC: Task Output Structure")
        log("="*60)
        
        for i, task in enumerate(crew.tasks):
            log(f"\nTask {i+1}:")
            log(f"  Description: {task.description[:80]}...")
            
            if not task.output:
                log(f"  ❌ No output object")
                continue
            
            output_obj = task.output
            log(f"  Output type: {type(output_obj).__name__}")
            log(f"  Has exported_output: {hasattr(output_obj, 'exported_output')}")
            log(f"  Has raw_output: {hasattr(output_obj, 'raw_output')}")
            log(f"  Has text: {hasattr(output_obj, 'text')}")
            log(f"  Has pydantic: {hasattr(output_obj, 'pydantic')}")
            
            # Show preview of raw_output if present
            if hasattr(output_obj, 'raw_output') and output_obj.raw_output:
                preview = str(output_obj.raw_output)[:200]
                log(f"  Raw output preview: {preview}...")
            
            # Show preview of text if present
            if hasattr(output_obj, 'text') and output_obj.text:
                preview = str(output_obj.text)[:200]
                log(f"  Text property preview: {preview}...")
        
        log("="*60 + "\n")
