"""
Static code analysis utilities for agent verification.
Performs validation without executing code or installing dependencies.
"""
import ast
from pathlib import Path
from typing import List, Tuple, Dict, Any


class StaticAnalyzer:
    """
    Static code analyzer for Python files.
    Uses AST parsing to validate code without execution.
    """
    
    @staticmethod
    def check_syntax(code: str) -> Tuple[bool, str]:
        """
        Validate Python syntax using AST.
        
        Args:
            code: Python code as string
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if not code or not isinstance(code, str):
            return False, "Code is empty or not a string"
        
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"
    
    @staticmethod
    def extract_imports(code: str) -> List[str]:
        """
        Extract all imported modules from code.
        
        Args:
            code: Python code as string
        
        Returns:
            List of imported module names
        """
        try:
            tree = ast.parse(code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return imports
        except:
            return []
    
    @staticmethod
    def check_crewai_patterns(code: str) -> Tuple[bool, List[str]]:
        """
        Verify code follows CrewAI patterns.
        
        Args:
            code: Python code as string
        
        Returns:
            (is_valid: bool, issues: List[str])
        """
        issues = []
        
        # Check for essential CrewAI imports
        if 'from crewai import' not in code and 'import crewai' not in code:
            issues.append("Missing crewai import")
        
        # Check for Agent definitions
        if 'Agent(' not in code and 'class' not in code.lower():
            issues.append("No Agent instances or custom Agent classes found")
        
        # Check for Task definitions
        if 'Task(' not in code:
            issues.append("No Task instances found")
        
        # Check for Crew definition (might not be in every file)
        # This is not an error, just a note
        
        return len(issues) == 0, issues
    
    @staticmethod
    def check_required_files(files_dict: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Verify all required files are present.
        
        Args:
            files_dict: Dict of {filename: code_content}
        
        Returns:
            (is_complete: bool, missing_files: List[str])
        """
        required = [
            'main.py',
            'agents.py',
            'tasks.py',
            'crew.py',
            'README.md',
            'requirements.txt'
        ]
        
        # Normalize paths (handle src/ subdirectories)
        present_files = set()
        for filepath in files_dict.keys():
            # Extract just the filename
            filename = Path(filepath).name
            present_files.add(filename.lower())
        
        missing = []
        for req in required:
            if req.lower() not in present_files:
                missing.append(req)
        
        return len(missing) == 0, missing
    
    @staticmethod
    def find_undefined_names(code: str) -> List[str]:
        """
        Find potentially undefined names using AST analysis.
        Note: This is a simplified check and may have false positives.
        
        Args:
            code: Python code as string
        
        Returns:
            List of potentially undefined names
        """
        try:
            tree = ast.parse(code)
            
            # Collect defined names
            defined = set()
            # Collect used names
            used = set()
            
            for node in ast.walk(tree):
                # Track definitions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    defined.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined.add(target.id)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        defined.add(alias.asname or alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        defined.add(alias.asname or alias.name)
                
                # Track usage
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used.add(node.id)
            
            # Built-in names to ignore
            builtins = {
                'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set',
                'tuple', 'range', 'enumerate', 'zip', 'map', 'filter', 'any', 'all',
                'open', 'file', 'Exception', 'ValueError', 'TypeError', 'KeyError',
                'True', 'False', 'None', '__name__', '__file__', '__main__'
            }
            
            # Find potentially undefined
            undefined = [name for name in used if name not in defined and name not in builtins]
            
            return undefined
        except:
            return []
    
    @staticmethod
    def count_code_metrics(code: str) -> Dict[str, int]:
        """
        Count basic code metrics.
        
        Args:
            code: Python code as string
        
        Returns:
            Dict with metrics like lines, functions, classes
        """
        metrics = {
            'total_lines': 0,
            'code_lines': 0,
            'functions': 0,
            'classes': 0,
            'imports': 0
        }
        
        try:
            lines = code.split('\n')
            metrics['total_lines'] = len(lines)
            
            # Count non-empty, non-comment lines
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            metrics['code_lines'] = len(code_lines)
            
            # Parse AST for detailed metrics
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    metrics['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    metrics['imports'] += 1
        except:
            pass
        
        return metrics
    
    @staticmethod
    def verify_agent_bundle(files_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Comprehensive verification of an agent bundle.
        
        Args:
            files_dict: Dict of {filename: code_content}
        
        Returns:
            Dict with verification results
        """
        results = {
            'passed': True,
            'files_valid': {},
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'metrics': {}
        }
        
        # Check required files
        files_complete, missing = StaticAnalyzer.check_required_files(files_dict)
        if not files_complete:
            results['passed'] = False
            results['issues'].extend([f"Missing required file: {f}" for f in missing])
        
        # Validate each Python file
        for filename, code in files_dict.items():
            if not filename.endswith('.py'):
                continue
            
            # Syntax check
            syntax_ok, syntax_error = StaticAnalyzer.check_syntax(code)
            results['files_valid'][filename] = syntax_ok
            
            if not syntax_ok:
                results['passed'] = False
                results['issues'].append(f"{filename}: {syntax_error}")
            else:
                # Check imports
                imports = StaticAnalyzer.extract_imports(code)
                
                # Check undefined names (may have false positives)
                undefined = StaticAnalyzer.find_undefined_names(code)
                if undefined and len(undefined) < 5:  # Only report if few items
                    results['warnings'].append(
                        f"{filename}: Potentially undefined names: {', '.join(undefined[:3])}"
                    )
                
                # Metrics
                metrics = StaticAnalyzer.count_code_metrics(code)
                results['metrics'][filename] = metrics
                
                # Check CrewAI patterns for key files
                if filename in ['agents.py', 'tasks.py', 'crew.py']:
                    patterns_ok, pattern_issues = StaticAnalyzer.check_crewai_patterns(code)
                    if not patterns_ok:
                        results['warnings'].extend([
                            f"{filename}: {issue}" for issue in pattern_issues
                        ])
        
        # Suggestions based on metrics
        total_code_lines = sum(m.get('code_lines', 0) for m in results['metrics'].values())
        if total_code_lines < 50:
            results['suggestions'].append(
                "Consider adding more implementation details or documentation"
            )
        
        return results
