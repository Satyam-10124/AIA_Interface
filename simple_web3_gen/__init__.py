"""
Simple Web3 Generator
A lightweight, fast alternative to CrewAI for generating Web3 dApp frontends.

Uses 2 LLM calls instead of 11 agents:
- Stage 2: UI Planning
- Stage 3: Code Generation
"""

__version__ = "1.0.0"
__author__ = "AIA Interface Team"

from .generator import SimpleWeb3Generator
from .abi_parser import ABIParser

__all__ = ["SimpleWeb3Generator", "ABIParser"]
