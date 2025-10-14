"""
Environment validation utilities for AIA_Interface.
Validates API keys, dependencies, and output directories before crew execution.
"""
import os
import sys
from pathlib import Path
from typing import Tuple, List


class ValidationError(Exception):
    """Raised when environment validation fails."""
    pass


class EnvironmentValidator:
    """Validates environment setup before crew execution."""
    
    @staticmethod
    def validate_gemini_api_key() -> Tuple[bool, str]:
        """
        Validate GEMINI_API_KEY is present and correctly formatted.
        
        Returns:
            (is_valid: bool, message: str)
        """
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            return False, (
                "❌ GEMINI_API_KEY not found in environment.\n"
                "   Please add it to your .env file:\n"
                "   GEMINI_API_KEY=AIzaSy...\n"
                "   Get your key at: https://aistudio.google.com/app/apikey"
            )
        
        if api_key.strip() == "":
            return False, "❌ GEMINI_API_KEY is empty"
        
        # Gemini keys typically start with "AIza"
        if not api_key.startswith("AIza"):
            return True, (
                f"⚠️  Warning: API key format looks unusual (expected to start with 'AIza')\n"
                f"   Key starts with: {api_key[:4]}...\n"
                f"   Key will still be attempted, but may fail."
            )
        
        return True, f"✅ GEMINI_API_KEY found ({api_key[:10]}...{api_key[-4:]})"
    
    @staticmethod
    def validate_output_directory(path: Path) -> Tuple[bool, str]:
        """
        Validate output directory is writable.
        
        Args:
            path: Path to the output directory
        
        Returns:
            (is_valid: bool, message: str)
        """
        path = Path(path)
        
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                return True, f"✅ Created output directory: {path}"
            except PermissionError:
                return False, f"❌ Cannot create directory: {path} (permission denied)"
            except Exception as e:
                return False, f"❌ Cannot create directory: {path} ({str(e)})"
        
        if not os.access(path, os.W_OK):
            return False, f"❌ Output directory not writable: {path}"
        
        return True, f"✅ Output directory writable: {path}"
    
    @staticmethod
    def check_dependencies() -> Tuple[bool, str, List[str]]:
        """
        Check if required packages are installed.
        
        Returns:
            (all_installed: bool, message: str, missing: List[str])
        """
        required = [
            'crewai',
            'crewai_tools',
            'litellm',
            'pydantic',
            'dotenv',  # python-dotenv package, imported as 'dotenv'
        ]
        
        missing = []
        for package in required:
            try:
                __import__(package)
            except ImportError:
                # Handle special case for python-dotenv
                if package == 'dotenv':
                    missing.append('python-dotenv')
                else:
                    missing.append(package)
        
        if missing:
            return False, f"❌ Missing dependencies: {', '.join(missing)}", missing
        
        return True, "✅ All dependencies installed", []
    
    @staticmethod
    def run_full_validation(output_dir: Path = None) -> bool:
        """
        Run all validation checks.
        
        Args:
            output_dir: Optional output directory to validate
        
        Returns:
            True if all checks pass
        
        Raises:
            ValidationError if critical checks fail
        """
        print("\n" + "="*60)
        print("🔍 Pre-Flight Environment Validation")
        print("="*60 + "\n")
        
        # Check 1: Dependencies
        deps_ok, deps_msg, missing = EnvironmentValidator.check_dependencies()
        print(deps_msg)
        if not deps_ok:
            print(f"\n💡 Fix: pip install {' '.join(missing)}")
            raise ValidationError("Missing dependencies")
        
        # Check 2: API Key
        key_ok, key_msg = EnvironmentValidator.validate_gemini_api_key()
        print(f"\n{key_msg}")
        if not key_ok:
            raise ValidationError("API key not configured")
        
        # Check 3: Output Directory (if provided)
        if output_dir:
            dir_ok, dir_msg = EnvironmentValidator.validate_output_directory(output_dir)
            print(f"\n{dir_msg}")
            if not dir_ok:
                raise ValidationError("Output directory not accessible")
        
        print("\n" + "="*60)
        print("✅ All checks passed - ready to proceed")
        print("="*60 + "\n")
        
        return True


def validate_or_exit(output_dir: Path = None):
    """
    Run validation and exit if it fails.
    
    Args:
        output_dir: Optional output directory to validate
    """
    try:
        EnvironmentValidator.run_full_validation(output_dir)
    except ValidationError as e:
        print(f"\n❌ Validation failed: {e}")
        print("\n🛠️  Please fix the above issues and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during validation: {e}")
        sys.exit(1)
