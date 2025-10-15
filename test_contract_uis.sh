#!/bin/bash

# Test Script: Generate Multiple Contract UIs
# Purpose: Validate current system capabilities with different contract types

echo "🧪 Testing UI Generator with Multiple Contract Types"
echo "===================================================="

# Activate virtual environment
source .venv/bin/activate

# Test 1: ERC-20 Token Interface (Simple)
echo ""
echo "📝 Test 1: ERC-20 Token Interface"
echo "-----------------------------------"
python3 ui_generator_cli.py \
  --agent-description "ERC-20 token dashboard for managing token transfers, approvals, and balance checking" \
  --agent-capabilities "connect MetaMask wallet, display token balance, display token symbol and decimals, transfer tokens to another address, approve spending allowance, check allowance, view transaction history" \
  --agent-api "Ethereum blockchain, ethers.js v6, ERC-20 standard interface: transfer(address,uint256), approve(address,uint256), balanceOf(address), allowance(address,address), decimals(), symbol()" \
  --theme "light" \
  --layout "standard" \
  --color-scheme "blue" \
  --output-name "test-erc20-token" \
  --verbose

echo ""
echo "✅ Test 1 Complete: generated_ui/test-erc20-token/"
echo ""
read -p "Press Enter to continue to Test 2..."

# Test 2: NFT Minting Interface (Medium)
echo ""
echo "📝 Test 2: NFT Minting Interface"
echo "-----------------------------------"
python3 ui_generator_cli.py \
  --agent-description "NFT minting platform for ERC-721 collection with metadata display" \
  --agent-capabilities "connect wallet, mint new NFT, view owned NFTs, display NFT metadata (name, image, description), transfer NFT to another address, view total supply, check minting price" \
  --agent-api "Ethereum blockchain, ethers.js v6, ERC-721 interface: mint(), ownerOf(uint256), tokenURI(uint256), transferFrom(address,address,uint256), balanceOf(address), totalSupply()" \
  --theme "dark" \
  --layout "expanded" \
  --color-scheme "purple" \
  --output-name "test-nft-minter" \
  --verbose

echo ""
echo "✅ Test 2 Complete: generated_ui/test-nft-minter/"
echo ""
read -p "Press Enter to continue to Test 3..."

# Test 3: DAO Governance (Complex)
echo ""
echo "📝 Test 3: DAO Governance Interface"
echo "-----------------------------------"
python3 ui_generator_cli.py \
  --agent-description "DAO governance dashboard with proposal creation and voting" \
  --agent-capabilities "connect wallet, view all proposals, view proposal details (description, votes, status), create new proposal, vote on proposals (for/against), check voting power, view voting history, display proposal results" \
  --agent-api "Ethereum blockchain, ethers.js v6, Governor contract interface: propose(targets,values,calldatas,description), castVote(proposalId,support), getVotes(account), state(proposalId), proposalVotes(proposalId)" \
  --theme "system" \
  --layout "expanded" \
  --color-scheme "green" \
  --output-name "test-dao-governance" \
  --verbose

echo ""
echo "✅ Test 3 Complete: generated_ui/test-dao-governance/"
echo ""

# Summary
echo ""
echo "========================================"
echo "🎉 All Tests Complete!"
echo "========================================"
echo ""
echo "Generated UIs:"
echo "  1. test-erc20-token/     - ERC-20 Token Interface"
echo "  2. test-nft-minter/      - NFT Minting Platform"
echo "  3. test-dao-governance/  - DAO Governance Dashboard"
echo ""
echo "Next Steps:"
echo "  1. Review each generated UI"
echo "  2. Test in browser"
echo "  3. Document manual steps needed"
echo "  4. Fill out testing checklist"
echo ""
echo "Testing checklist: testing_results.md"
