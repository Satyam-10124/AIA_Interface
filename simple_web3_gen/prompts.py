"""
Prompt Templates for LLM Stages
Optimized for minimal token usage and maximum output quality.
"""

from typing import Dict, Any


def build_stage2_prompt(metadata: Dict[str, Any], network: str, theme: str) -> str:
    """
    Stage 2: UI Planning Prompt
    Asks LLM to design UI structure (NO code generation).
    
    Target: ~1K tokens input, ~500 tokens output
    """
    compact = metadata
    
    prompt = f"""You are a UX architect for Web3 dApps. Design the UI structure for a {compact['contract_type']} contract interface.

CONTRACT INFO:
- Type: {compact['contract_type']}
- Read functions ({compact['read_count']}): {', '.join(compact['read_names'])}
- Write functions ({compact['write_count']}): {', '.join(compact['write_names'])}
- Events ({compact['event_count']}): {', '.join(compact['event_names'])}
- Network: {network}
- Has payable functions: {compact['has_payable']}

USER PREFERENCES:
- Theme: {theme}

TASK: Design a modern, intuitive UI structure. Return ONLY a JSON object with this exact structure:

{{
  "sections": [
    {{"id": "wallet", "title": "Wallet Connection", "priority": 1}},
    {{"id": "info", "title": "Contract Info", "components": ["name", "symbol"]}},
    {{"id": "read", "title": "Read Functions", "layout": "grid"}},
    {{"id": "write", "title": "Write Functions", "layout": "card"}}
  ],
  "theme": {{
    "style": "glassmorphism",
    "primaryColor": "#3b82f6",
    "accentColor": "#8b5cf6",
    "bgGradient": "from-gray-900 to-gray-800"
  }},
  "features": ["wallet-connect", "transaction-history", "event-logs", "network-switcher"]
}}

Adapt sections and components based on the contract type. For ERC20: include balance display. For ERC721: include NFT gallery. Return ONLY valid JSON, no markdown, no explanations."""

    return prompt


def build_stage3_prompt(
    metadata: Dict[str, Any],
    ui_plan: Dict[str, Any],
    contract_address: str,
    network: str,
    function_summary: str
) -> str:
    """
    Stage 3: Code Generation Prompt
    Asks LLM to generate complete Web3 dApp files.
    
    Target: ~4K tokens input, ~6K tokens output
    """
    
    prompt = f"""You are an expert Web3 frontend developer. Generate a complete, production-ready dApp for this smart contract.

CONTRACT:
- Address: {contract_address}
- Network: {network}
- Type: {metadata['contract_type']}

{function_summary}

UI STRUCTURE:
{_format_ui_plan(ui_plan)}

TECHNICAL REQUIREMENTS:
1. **Ethers.js v6** (NOT v5) - Use latest syntax
2. **Web3Modal** (@web3modal/ethers v5+) + **Wagmi** for wallet connection
3. **Tailwind CSS** (CDN) for styling
4. **Vanilla JavaScript** (no frameworks)
5. Multi-network support (users can switch networks)
6. Comprehensive error handling with user-friendly messages
7. Gas estimation for all write functions
8. Transaction status tracking
9. Real-time event listeners
10. Responsive design (mobile-friendly)

GENERATE 3 FILES:

### 1. index.html
Complete HTML page with:
- Web3Modal integration
- Tailwind CSS CDN
- Sections from UI plan: {', '.join([s['title'] for s in ui_plan.get('sections', [])])}
- Status display for transactions
- Error message area
- Modern glassmorphism UI design

### 2. app.js
Complete JavaScript with:
- Import ethers, Web3Modal, Wagmi
- Contract ABI embedded
- Network configuration for: {network}, mainnet, polygon, arbitrum
- Wallet connection functions (connect, disconnect, network switching)
- Contract wrapper class with ALL {metadata['read_count'] + metadata['write_count']} functions
- Event listeners for: {', '.join(metadata['event_names'])}
- Gas estimation with 10% buffer
- Transaction handlers with confirmation tracking
- Error handling for: rejected tx, insufficient funds, wrong network
- UI update functions

### 3. styles.css
Modern styling with:
- {ui_plan.get('theme', {}).get('style', 'glassmorphism')} design
- Dark theme with colors: {ui_plan.get('theme', {}).get('primaryColor', '#3b82f6')}
- Smooth animations and transitions
- Button states: normal, hover, loading, disabled
- Responsive breakpoints
- Card components with backdrop blur

OUTPUT FORMAT:
Return files as markdown code blocks. Use this EXACT format:

```html
<!DOCTYPE html>
<html lang="en">
... complete HTML ...
</html>
```

```javascript
// app.js - Complete Web3 Integration
import {{ ethers }} from 'ethers';
... complete JavaScript ...
```

```css
/* styles.css - Modern Glassmorphism Theme */
... complete CSS ...
```

CRITICAL:
- ALL {metadata['read_count']} read functions MUST have UI controls
- ALL {metadata['write_count']} write functions MUST have forms with inputs
- Include placeholder for: YOUR_INFURA_PROJECT_ID, YOUR_WALLETCONNECT_PROJECT_ID
- Use ethers.js v6 syntax: `ethers.formatUnits()`, `ethers.parseUnits()`, `new ethers.Contract()`
- Make it immediately usable (copy-paste-run ready)

Begin generation now. Return ONLY the 3 code blocks, nothing else."""

    return prompt


def _format_ui_plan(ui_plan: Dict[str, Any]) -> str:
    """Format UI plan for inclusion in prompt."""
    lines = []
    
    sections = ui_plan.get('sections', [])
    for section in sections:
        components = section.get('components', [])
        layout = section.get('layout', 'default')
        lines.append(f"  - {section['title']}: {', '.join(components) if components else layout + ' layout'}")
    
    theme = ui_plan.get('theme', {})
    lines.append(f"\nTheme: {theme.get('style', 'modern')} with {theme.get('primaryColor', 'blue')} primary")
    
    features = ui_plan.get('features', [])
    if features:
        lines.append(f"Features: {', '.join(features)}")
    
    return '\n'.join(lines)


def build_readme_template(
    contract_type: str,
    contract_address: str,
    network: str,
    read_functions: list,
    write_functions: list
) -> str:
    """Generate README content (template-based, no LLM)."""
    
    return f"""# {contract_type} DApp Interface

A Web3 frontend for interacting with the {contract_type} smart contract.

## Contract Information

- **Address**: `{contract_address}`
- **Network**: {network}
- **Type**: {contract_type}

## Setup Instructions

### 1. Prerequisites

- Modern web browser (Chrome, Firefox, Brave, Edge)
- MetaMask or another Web3 wallet installed
- Connected to {network} network

### 2. Configuration

Before using the dApp, replace the following placeholders in `app.js`:

```javascript
// Line ~10: Replace with your Infura Project ID
const projectId = 'YOUR_INFURA_PROJECT_ID';  // Get from https://infura.io

// Line ~5: Replace with your WalletConnect Project ID  
const walletConnectId = 'YOUR_WALLETCONNECT_PROJECT_ID';  // Get from https://cloud.walletconnect.com
```

### 3. Running Locally

**Option A: Simple HTTP Server**
```bash
python -m http.server 8000
```
Then open: http://localhost:8000

**Option B: Node.js http-server**
```bash
npx http-server -p 8000
```

**Option C: VS Code Live Server**
- Right-click `index.html` → "Open with Live Server"

### 4. Usage

1. **Connect Wallet**: Click "Connect Wallet" and select your wallet
2. **Switch Network**: If prompted, switch to {network} network
3. **Read Functions**: View contract data (no transaction needed)
4. **Write Functions**: Submit transactions (requires gas fees)
5. **Monitor Events**: Real-time updates when contract events occur

## Available Functions

### Read Functions ({len(read_functions)})
{chr(10).join([f'- `{f["name"]}()`' for f in read_functions])}

### Write Functions ({len(write_functions)})
{chr(10).join([f'- `{f["name"]}()`' for f in write_functions])}

## Technical Stack

- **Ethers.js v6**: Ethereum interaction
- **Web3Modal + Wagmi**: Multi-wallet support
- **Tailwind CSS**: Styling
- **Vanilla JavaScript**: No framework dependencies

## Troubleshooting

### "User rejected transaction"
→ You cancelled the transaction in your wallet. Try again.

### "Insufficient funds"
→ You need more ETH for gas fees. Add funds to your wallet.

### "Wrong network"
→ Switch to {network} network in your wallet.

### "Gas estimation failed"
→ Transaction would fail. Check your inputs (amount, address, etc.).

## Security Notes

⚠️ **IMPORTANT**:
- Never share your private keys
- Always verify contract addresses
- Double-check transaction details before confirming
- Test with small amounts first

## Support

Contract Address: {contract_address}
Network: {network}
Block Explorer: [View Contract](https://{_get_explorer_url(network)}/address/{contract_address})

---
Generated by AIA Interface - Simple Web3 Generator
"""


def _get_explorer_url(network: str) -> str:
    """Get block explorer URL for network."""
    explorers = {
        'mainnet': 'etherscan.io',
        'sepolia': 'sepolia.etherscan.io',
        'goerli': 'goerli.etherscan.io',
        'polygon': 'polygonscan.com',
        'mumbai': 'mumbai.polygonscan.com',
        'arbitrum': 'arbiscan.io',
        'optimism': 'optimistic.etherscan.io',
        'bsc': 'bscscan.com'
    }
    return explorers.get(network.lower(), 'etherscan.io')
