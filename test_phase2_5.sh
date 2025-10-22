#!/bin/bash
# Test script for Phase 2.5: Web3 & Smart Contract Integration

echo "============================================================="
echo "🧪 PHASE 2.5 TEST: Web3 Smart Contract Integration"
echo "============================================================="
echo ""

# Test contract address (USDC on Sepolia testnet)
CONTRACT_ADDRESS="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
NETWORK="sepolia"

echo "📋 Test Configuration:"
echo "  • Contract Address: $CONTRACT_ADDRESS"
echo "  • Network: $NETWORK"
echo "  • ABI File: test_erc20_abi.json"
echo ""

read -p "Press Enter to start test generation..."

echo ""
echo "🚀 Generating Web3 dApp UI..."
echo ""

python3 ui_generator_cli.py \
  --agent-description "ERC-20 token dashboard for viewing balances and transferring tokens" \
  --agent-capabilities "connect wallet, check balance, transfer tokens, view transaction history, approve spending" \
  --contract-address "$CONTRACT_ADDRESS" \
  --contract-abi "./test_erc20_abi.json" \
  --network "$NETWORK" \
  --theme "dark" \
  --layout "expanded" \
  --color-scheme "blue" \
  --output-name "test-web3-erc20" \
  --verbose

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================="
    echo "✅ TEST PASSED!"
    echo "============================================================="
    echo ""
    echo "📂 Generated Files:"
    echo "  generated_ui/test-web3-erc20/"
    echo ""
    echo "🌐 To view in browser:"
    echo "  cd generated_ui/test-web3-erc20"
    echo "  python3 -m http.server 8000"
    echo "  open http://localhost:8000"
    echo ""
    echo "📚 To read documentation:"
    echo "  cat generated_ui/test-web3-erc20/README.md"
    echo ""
    echo "📊 To view reports:"
    echo "  ls -la generated_ui/test-web3-erc20/reports/"
    echo ""
else
    echo ""
    echo "============================================================="
    echo "❌ TEST FAILED"
    echo "============================================================="
    echo ""
    echo "Check error messages above for details."
    echo ""
    exit 1
fi
