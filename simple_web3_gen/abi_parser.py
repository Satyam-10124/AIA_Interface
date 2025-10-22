"""
ABI Parser - Stage 1
Pure Python ABI analysis with NO LLM calls.
Extracts metadata from contract ABIs for UI generation.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class ABIParser:
    """Parses and analyzes Ethereum contract ABIs."""
    
    # Standard interfaces for contract type detection
    ERC20_FUNCTIONS = {'name', 'symbol', 'decimals', 'totalSupply', 'balanceOf', 'transfer', 'approve', 'allowance'}
    ERC721_FUNCTIONS = {'name', 'symbol', 'balanceOf', 'ownerOf', 'tokenURI', 'approve', 'transferFrom'}
    ERC1155_FUNCTIONS = {'balanceOf', 'balanceOfBatch', 'setApprovalForAll', 'safeTransferFrom'}
    
    def __init__(self):
        self.abi = []
        self.metadata = {}
    
    def parse(self, abi_path: str) -> Dict[str, Any]:
        """
        Parse ABI file and extract metadata.
        
        Args:
            abi_path: Path to ABI JSON file
            
        Returns:
            Dictionary with parsed metadata
        """
        abi_file = Path(abi_path)
        
        if not abi_file.exists():
            raise FileNotFoundError(f"ABI file not found: {abi_path}")
        
        with open(abi_file, 'r') as f:
            self.abi = json.load(f)
        
        if not isinstance(self.abi, list):
            raise ValueError("ABI must be a list of interface definitions")
        
        # Extract metadata
        self.metadata = {
            'read_functions': self._extract_read_functions(),
            'write_functions': self._extract_write_functions(),
            'events': self._extract_events(),
            'constructor': self._extract_constructor(),
            'contract_type': self._detect_contract_type(),
            'total_functions': 0,
            'has_payable': False
        }
        
        self.metadata['total_functions'] = len(self.metadata['read_functions']) + len(self.metadata['write_functions'])
        self.metadata['has_payable'] = any(f.get('stateMutability') == 'payable' for f in self.metadata['write_functions'])
        
        return self.metadata
    
    def _extract_read_functions(self) -> List[Dict[str, Any]]:
        """Extract read-only functions (view/pure)."""
        read_funcs = []
        
        for item in self.abi:
            if item.get('type') == 'function' and item.get('stateMutability') in ['view', 'pure']:
                func_info = {
                    'name': item.get('name'),
                    'inputs': [(inp.get('name', ''), inp.get('type')) for inp in item.get('inputs', [])],
                    'outputs': [out.get('type') for out in item.get('outputs', [])],
                    'stateMutability': item.get('stateMutability')
                }
                read_funcs.append(func_info)
        
        return read_funcs
    
    def _extract_write_functions(self) -> List[Dict[str, Any]]:
        """Extract state-changing functions (nonpayable/payable)."""
        write_funcs = []
        
        for item in self.abi:
            if item.get('type') == 'function' and item.get('stateMutability') in ['nonpayable', 'payable']:
                func_info = {
                    'name': item.get('name'),
                    'inputs': [(inp.get('name', ''), inp.get('type')) for inp in item.get('inputs', [])],
                    'outputs': [out.get('type') for out in item.get('outputs', [])],
                    'stateMutability': item.get('stateMutability')
                }
                write_funcs.append(func_info)
        
        return write_funcs
    
    def _extract_events(self) -> List[Dict[str, Any]]:
        """Extract contract events."""
        events = []
        
        for item in self.abi:
            if item.get('type') == 'event':
                event_info = {
                    'name': item.get('name'),
                    'inputs': [
                        {
                            'name': inp.get('name', ''),
                            'type': inp.get('type'),
                            'indexed': inp.get('indexed', False)
                        }
                        for inp in item.get('inputs', [])
                    ]
                }
                events.append(event_info)
        
        return events
    
    def _extract_constructor(self) -> Optional[Dict[str, Any]]:
        """Extract constructor info."""
        for item in self.abi:
            if item.get('type') == 'constructor':
                return {
                    'inputs': [(inp.get('name', ''), inp.get('type')) for inp in item.get('inputs', [])]
                }
        return None
    
    def _detect_contract_type(self) -> str:
        """Detect contract standard (ERC20, ERC721, ERC1155, or custom)."""
        func_names = {f['name'] for f in self._get_all_functions()}
        
        # Check for ERC standards
        if self.ERC20_FUNCTIONS.issubset(func_names):
            return 'ERC20'
        elif self.ERC721_FUNCTIONS.issubset(func_names):
            return 'ERC721'
        elif self.ERC1155_FUNCTIONS.issubset(func_names):
            return 'ERC1155'
        else:
            return 'Custom'
    
    def _get_all_functions(self) -> List[Dict[str, Any]]:
        """Get all functions from ABI."""
        return [item for item in self.abi if item.get('type') == 'function']
    
    def get_function_summary(self) -> str:
        """
        Get a concise summary of functions for LLM prompts.
        Returns a formatted string listing all functions.
        """
        summary_lines = []
        
        # Read functions
        if self.metadata['read_functions']:
            summary_lines.append("READ FUNCTIONS:")
            for func in self.metadata['read_functions']:
                params = ', '.join([f"{name}: {typ}" for name, typ in func['inputs']]) or 'none'
                returns = ', '.join(func['outputs']) or 'none'
                summary_lines.append(f"  • {func['name']}({params}) → {returns}")
        
        # Write functions
        if self.metadata['write_functions']:
            summary_lines.append("\nWRITE FUNCTIONS:")
            for func in self.metadata['write_functions']:
                params = ', '.join([f"{name}: {typ}" for name, typ in func['inputs']]) or 'none'
                payable = " [PAYABLE]" if func['stateMutability'] == 'payable' else ""
                summary_lines.append(f"  • {func['name']}({params}){payable}")
        
        # Events
        if self.metadata['events']:
            summary_lines.append("\nEVENTS:")
            for event in self.metadata['events']:
                indexed_params = [inp['name'] for inp in event['inputs'] if inp['indexed']]
                summary_lines.append(f"  • {event['name']} (indexed: {', '.join(indexed_params) or 'none'})")
        
        return '\n'.join(summary_lines)
    
    def get_compact_metadata(self) -> Dict[str, Any]:
        """
        Get compact metadata suitable for LLM prompts (reduced token size).
        """
        return {
            'contract_type': self.metadata['contract_type'],
            'read_count': len(self.metadata['read_functions']),
            'write_count': len(self.metadata['write_functions']),
            'event_count': len(self.metadata['events']),
            'read_names': [f['name'] for f in self.metadata['read_functions']],
            'write_names': [f['name'] for f in self.metadata['write_functions']],
            'event_names': [e['name'] for e in self.metadata['events']],
            'has_payable': self.metadata['has_payable']
        }
