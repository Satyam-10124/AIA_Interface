"""
Simple Web3 Generator - Main Orchestrator
Coordinates the 4-stage generation pipeline.
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import google.generativeai as genai

from .abi_parser import ABIParser
from .prompts import build_stage2_prompt, build_stage3_prompt, build_readme_template


class SimpleWeb3Generator:
    """
    Main generator class orchestrating the Web3 dApp generation pipeline.
    
    Pipeline:
    1. Stage 1: Parse ABI (no LLM)
    2. Stage 2: Plan UI (LLM call 1)
    3. Stage 3: Generate code (LLM call 2)
    4. Stage 4: Write files (no LLM)
    """
    
    def __init__(self, gemini_api_key: str, model: str = 'gemini-2.0-flash-exp'):
        """
        Initialize generator.
        
        Args:
            gemini_api_key: Google Gemini API key
            model: Gemini model to use
        """
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)
        self.parser = ABIParser()
        
        # Generation config for optimal output
        self.gen_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8000,
        }
    
    def generate(
        self,
        abi_path: str,
        contract_address: str,
        network: str,
        output_dir: str,
        theme: str = 'dark',
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete Web3 dApp.
        
        Args:
            abi_path: Path to ABI JSON file
            contract_address: Contract address
            network: Network name (sepolia, mainnet, etc.)
            output_dir: Output directory path
            theme: UI theme (dark/light)
            verbose: Print progress messages
            
        Returns:
            Dictionary with generation results
        """
        start_time = time.time()
        results = {
            'success': False,
            'output_dir': output_dir,
            'files': [],
            'stages': {},
            'total_time': 0,
            'error': None
        }
        
        try:
            # Stage 1: Parse ABI
            if verbose:
                print("🚀 Simple Web3 Generator v1.0")
                print("━" * 60)
                print("📖 Stage 1: Parsing ABI...", end=' ', flush=True)
            
            stage1_start = time.time()
            metadata = self.parser.parse(abi_path)
            compact_metadata = self.parser.get_compact_metadata()
            function_summary = self.parser.get_function_summary()
            stage1_time = time.time() - stage1_start
            
            results['stages']['stage1_parse'] = {
                'time': stage1_time,
                'metadata': metadata
            }
            
            if verbose:
                print(f"✓ ({stage1_time:.1f}s)")
                print(f"   Found {len(metadata['read_functions'])} read, {len(metadata['write_functions'])} write functions")
                print(f"   Contract type: {metadata['contract_type']}")
            
            # Stage 2: Plan UI
            if verbose:
                print("\n🎨 Stage 2: Planning UI...", end=' ', flush=True)
            
            stage2_start = time.time()
            ui_plan = self._stage2_plan_ui(compact_metadata, network, theme)
            stage2_time = time.time() - stage2_start
            
            results['stages']['stage2_plan'] = {
                'time': stage2_time,
                'ui_plan': ui_plan
            }
            
            if verbose:
                print(f"✓ ({stage2_time:.1f}s)")
                sections = ui_plan.get('sections', [])
                print(f"   Sections: {', '.join([s['title'] for s in sections])}")
                print(f"   Theme: {ui_plan.get('theme', {}).get('style', 'modern')}")
            
            # Stage 3: Generate Code
            if verbose:
                print("\n⚙️  Stage 3: Generating code...", end=' ', flush=True)
            
            stage3_start = time.time()
            files = self._stage3_generate_code(
                compact_metadata,
                ui_plan,
                contract_address,
                network,
                function_summary
            )
            stage3_time = time.time() - stage3_start
            
            results['stages']['stage3_generate'] = {
                'time': stage3_time,
                'file_count': len(files)
            }
            
            if verbose:
                print(f"✓ ({stage3_time:.1f}s)")
                for filename, content in files.items():
                    size_kb = len(content) / 1024
                    print(f"   {filename}: {size_kb:.1f} KB")
            
            # Stage 4: Write Files
            if verbose:
                print("\n📝 Stage 4: Writing files...", end=' ', flush=True)
            
            stage4_start = time.time()
            
            # Add README
            files['README.md'] = build_readme_template(
                metadata['contract_type'],
                contract_address,
                network,
                metadata['read_functions'],
                metadata['write_functions']
            )
            
            # Add requirements.txt
            files['requirements.txt'] = self._generate_requirements_txt()
            
            written_files = self._write_files(files, output_dir)
            stage4_time = time.time() - stage4_start
            
            results['stages']['stage4_write'] = {
                'time': stage4_time,
                'files': written_files
            }
            results['files'] = written_files
            
            if verbose:
                print(f"✓ ({stage4_time:.1f}s)")
                print(f"   Output: {output_dir}")
            
            # Calculate totals
            total_time = time.time() - start_time
            results['total_time'] = total_time
            results['success'] = True
            
            # Calculate cost estimate
            total_tokens = results['stages']['stage2_plan'].get('tokens', 1500) + \
                          results['stages']['stage3_generate'].get('tokens', 10000)
            cost_estimate = (total_tokens / 1_000_000) * 0.30  # $0.30 per 1M tokens
            
            if verbose:
                print(f"\n✅ Done! Total time: {total_time:.1f}s")
                print(f"💰 Estimated cost: ${cost_estimate:.3f}")
                print(f"\nNext steps:")
                print(f"1. Replace YOUR_INFURA_PROJECT_ID in app.js")
                print(f"2. Replace YOUR_WALLETCONNECT_PROJECT_ID in app.js")
                print(f"3. Run: python -m http.server 8000")
                print(f"4. Open: http://localhost:8000")
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            results['total_time'] = time.time() - start_time
            
            if verbose:
                print(f"\n❌ Error: {e}")
            
            raise
    
    def _stage2_plan_ui(self, metadata: Dict[str, Any], network: str, theme: str) -> Dict[str, Any]:
        """Stage 2: Plan UI structure with LLM."""
        prompt = build_stage2_prompt(metadata, network, theme)
        
        response = self.model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.3,  # Lower temp for structured output
                'max_output_tokens': 1000,
            }
        )
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        
        try:
            ui_plan = json.loads(response_text)
            return ui_plan
        except json.JSONDecodeError as e:
            # Fallback: create default UI plan
            print(f"Warning: Could not parse UI plan JSON, using default. Error: {e}")
            return self._default_ui_plan(metadata)
    
    def _stage3_generate_code(
        self,
        metadata: Dict[str, Any],
        ui_plan: Dict[str, Any],
        contract_address: str,
        network: str,
        function_summary: str
    ) -> Dict[str, str]:
        """Stage 3: Generate code files with LLM."""
        prompt = build_stage3_prompt(metadata, ui_plan, contract_address, network, function_summary)
        
        response = self.model.generate_content(
            prompt,
            generation_config=self.gen_config
        )
        
        # Parse code blocks from response
        files = self._parse_code_blocks(response.text)
        
        # Validate we got the expected files
        required_files = ['index.html', 'app.js', 'styles.css']
        missing = [f for f in required_files if f not in files]
        
        if missing:
            raise ValueError(f"LLM did not generate required files: {missing}")
        
        return files
    
    def _parse_code_blocks(self, text: str) -> Dict[str, str]:
        """Parse markdown code blocks from LLM response."""
        files = {}
        
        # Pattern to match ```language\n...\n```
        pattern = r'```(\w+)\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for lang, code in matches:
            lang = lang.lower()
            code = code.strip()
            
            if lang in ['html', 'htm']:
                files['index.html'] = code
            elif lang in ['javascript', 'js']:
                files['app.js'] = code
            elif lang == 'css':
                files['styles.css'] = code
        
        return files
    
    def _write_files(self, files: Dict[str, str], output_dir: str) -> list:
        """Write generated files to disk."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        written = []
        
        for filename, content in files.items():
            filepath = output_path / filename
            filepath.write_text(content, encoding='utf-8')
            written.append(str(filepath))
        
        return written
    
    def _default_ui_plan(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback UI plan if LLM fails."""
        return {
            "sections": [
                {"id": "wallet", "title": "Wallet Connection", "priority": 1},
                {"id": "info", "title": "Contract Info", "components": ["address", "network"]},
                {"id": "read", "title": "Read Functions", "layout": "grid"},
                {"id": "write", "title": "Write Functions", "layout": "card"}
            ],
            "theme": {
                "style": "glassmorphism",
                "primaryColor": "#3b82f6",
                "accentColor": "#8b5cf6",
                "bgGradient": "from-gray-900 to-gray-800"
            },
            "features": ["wallet-connect", "network-switcher", "transaction-status"]
        }
    
    def _generate_requirements_txt(self) -> str:
        """Generate requirements.txt content."""
        return """# Web3 DApp Frontend Dependencies (CDN-based, no installation needed)
# This file is for reference only

# JavaScript libraries (loaded via CDN in index.html):
# - ethers@^6.0.0
# - @web3modal/ethers@^5.0.0
# - @wagmi/core@^2.0.0

# Development server (optional):
# python -m http.server 8000
# OR
# npx http-server -p 8000
"""
