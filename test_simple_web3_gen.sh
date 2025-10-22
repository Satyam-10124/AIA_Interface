#!/bin/bash

# Test script for Simple Web3 Generator
# Tests ERC20 token dApp generation

set -e  # Exit on error

echo "🧪 Testing Simple Web3 Generator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Create .env with GEMINI_API_KEY=your_key"
    exit 1
fi

# Check if venv exists
if [ ! -d .venv ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Run: python -m venv .venv && .venv/bin/pip install -r requirements_ui_generator.txt"
    exit 1
fi

# Activate venv and install dependencies
echo "📦 Installing simple_web3_gen dependencies..."
.venv/bin/pip install -q -r simple_web3_gen/requirements.txt

# Run generation
echo ""
echo "🚀 Generating Web3 dApp for test ERC20 contract..."
echo ""

.venv/bin/python -m simple_web3_gen.cli \
  --abi-path test_erc20_abi.json \
  --contract-address 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238 \
  --network sepolia \
  --theme dark \
  --output-dir ./generated_ui/test_simple_web3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TEST PASSED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Generated files:"
ls -lh ./generated_ui/test_simple_web3/
echo ""
echo "To view the dApp:"
echo "  cd generated_ui/test_simple_web3"
echo "  python -m http.server 8000"
echo "  Open: http://localhost:8000"
