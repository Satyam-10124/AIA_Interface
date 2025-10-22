#!/usr/bin/env python3
"""
CLI Interface for Simple Web3 Generator
Fast Web3 dApp generation with minimal LLM calls.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from .generator import SimpleWeb3Generator


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description='Generate Web3 dApp frontend from smart contract ABI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for ERC20 token on Sepolia
  python -m simple_web3_gen.cli \\
    --abi-path test_erc20_abi.json \\
    --contract-address 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238 \\
    --network sepolia \\
    --output-dir ./generated_ui/my_token

  # Generate with light theme
  python -m simple_web3_gen.cli \\
    --abi-path my_contract_abi.json \\
    --contract-address 0xYOUR_ADDRESS \\
    --network mainnet \\
    --theme light

  # Specify custom Gemini model
  python -m simple_web3_gen.cli \\
    --abi-path contract.json \\
    --contract-address 0xADDRESS \\
    --network polygon \\
    --model gemini-1.5-pro

Networks supported:
  mainnet, sepolia, goerli, polygon, mumbai, arbitrum, optimism, bsc
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--abi-path',
        required=True,
        help='Path to contract ABI JSON file'
    )
    
    parser.add_argument(
        '--contract-address',
        required=True,
        help='Smart contract address (0x...)'
    )
    
    parser.add_argument(
        '--network',
        required=True,
        help='Network name (e.g., sepolia, mainnet, polygon)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory (default: ./generated_ui/simple_web3/<contract_name>)'
    )
    
    parser.add_argument(
        '--theme',
        choices=['dark', 'light'],
        default='dark',
        help='UI theme (default: dark)'
    )
    
    parser.add_argument(
        '--model',
        default='gemini-2.0-flash-exp',
        help='Gemini model to use (default: gemini-2.0-flash-exp)'
    )
    
    parser.add_argument(
        '--api-key',
        default=None,
        help='Gemini API key (or set GEMINI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found")
        print("Set it in .env file or use --api-key argument")
        sys.exit(1)
    
    # Validate ABI path
    abi_path = Path(args.abi_path)
    if not abi_path.exists():
        print(f"❌ Error: ABI file not found: {args.abi_path}")
        sys.exit(1)
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Auto-generate output directory name
        contract_name = abi_path.stem  # Filename without extension
        output_dir = f"./generated_ui/simple_web3/{contract_name}"
    
    # Validate contract address
    if not args.contract_address.startswith('0x') or len(args.contract_address) != 42:
        print(f"⚠️  Warning: Invalid contract address format: {args.contract_address}")
        print("Expected format: 0x followed by 40 hex characters")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(1)
    
    try:
        # Initialize generator
        generator = SimpleWeb3Generator(api_key, model=args.model)
        
        # Generate
        results = generator.generate(
            abi_path=str(abi_path),
            contract_address=args.contract_address,
            network=args.network,
            output_dir=output_dir,
            theme=args.theme,
            verbose=not args.quiet
        )
        
        if results['success']:
            sys.exit(0)
        else:
            print(f"❌ Generation failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
