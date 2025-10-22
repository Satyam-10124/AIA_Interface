# Simple Web3 Generator

⚡ **Fast Web3 dApp frontend generation in 30 seconds**

A lightweight alternative to CrewAI for generating smart contract interfaces. Uses **2 LLM calls** instead of 11 agents.

## Performance Comparison

| Metric | CrewAI Pipeline | Simple Web3 Gen |
|--------|----------------|-----------------|
| **Time** | 15-20 minutes | 30-60 seconds |
| **LLM Calls** | 11 agents | 2 calls |
| **Total Tokens** | ~88K | ~5K |
| **Cost** | $2-5 | $0.08-0.10 |
| **Success Rate** | ~30% | ~95% |

## Architecture

```
Input (ABI + Address) → 4 Stages → Complete dApp

Stage 1: Parse ABI        (Python, no LLM)   <1s
Stage 2: Plan UI          (LLM call #1)      3-5s
Stage 3: Generate Code    (LLM call #2)      20-30s
Stage 4: Write Files      (Python, no LLM)   <1s
```

## Installation

Already installed as part of AIA_Interface dependencies. No additional setup needed.

## Usage

### Basic Command

```bash
python -m simple_web3_gen.cli \
  --abi-path test_erc20_abi.json \
  --contract-address 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238 \
  --network sepolia
```

### With Options

```bash
python -m simple_web3_gen.cli \
  --abi-path my_contract.json \
  --contract-address 0xYOUR_ADDRESS \
  --network mainnet \
  --theme dark \
  --output-dir ./my_dapp \
  --model gemini-2.0-flash-exp
```

### All Options

```
Required:
  --abi-path PATH              Path to ABI JSON file
  --contract-address ADDRESS   Contract address (0x...)
  --network NETWORK            Network (sepolia, mainnet, polygon, etc.)

Optional:
  --output-dir DIR            Output directory (default: auto-generated)
  --theme {dark,light}        UI theme (default: dark)
  --model MODEL               Gemini model (default: gemini-2.0-flash-exp)
  --api-key KEY               Gemini API key (or use GEMINI_API_KEY env var)
  --quiet                     Suppress progress output
```

## Output

Generates a complete Web3 dApp with:

```
output_dir/
├── index.html          # Complete UI with Web3Modal
├── app.js              # Contract wrapper + wallet logic
├── styles.css          # Modern glassmorphism theme
├── README.md           # Setup instructions
└── requirements.txt    # Dependencies reference
```

### Generated Features

✅ **Multi-wallet support** (MetaMask, WalletConnect, Coinbase, etc.)  
✅ **Multi-network support** (mainnet, testnets, L2s)  
✅ **All contract functions** (read + write)  
✅ **Gas estimation** with 10% buffer  
✅ **Transaction tracking** with confirmations  
✅ **Event listeners** for contract events  
✅ **Error handling** with user-friendly messages  
✅ **Responsive design** (mobile-friendly)  
✅ **Modern UI** (glassmorphism, smooth animations)  

## Example Output

```bash
$ python -m simple_web3_gen.cli \
    --abi-path test_erc20_abi.json \
    --contract-address 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238 \
    --network sepolia

🚀 Simple Web3 Generator v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 Stage 1: Parsing ABI... ✓ (0.1s)
   Found 6 read, 3 write functions
   Contract type: ERC20

🎨 Stage 2: Planning UI... ✓ (4.2s)
   Sections: Wallet Connection, Contract Info, Read Functions, Write Functions
   Theme: glassmorphism

⚙️  Stage 3: Generating code... ✓ (28.7s)
   index.html: 9.2 KB
   app.js: 17.8 KB
   styles.css: 4.1 KB

📝 Stage 4: Writing files... ✓ (0.2s)
   Output: ./generated_ui/simple_web3/test_erc20

✅ Done! Total time: 33.2 seconds
💰 Estimated cost: $0.09

Next steps:
1. Replace YOUR_INFURA_PROJECT_ID in app.js
2. Replace YOUR_WALLETCONNECT_PROJECT_ID in app.js
3. Run: python -m http.server 8000
4. Open: http://localhost:8000
```

## Supported Networks

- Ethereum: `mainnet`, `sepolia`, `goerli`
- Polygon: `polygon`, `mumbai`
- Arbitrum: `arbitrum`
- Optimism: `optimism`
- BSC: `bsc`

## Supported Contract Types

Auto-detects and optimizes for:
- ✅ **ERC20** - Token interfaces
- ✅ **ERC721** - NFT interfaces
- ✅ **ERC1155** - Multi-token interfaces
- ✅ **Custom** - Any contract ABI

## Technical Details

### Stage 1: ABI Parsing
- Pure Python analysis
- Extracts read functions (view/pure)
- Extracts write functions (nonpayable/payable)
- Extracts events
- Detects contract standard (ERC20, ERC721, etc.)
- **Time**: <1 second
- **Cost**: $0

### Stage 2: UI Planning
- LLM designs UI structure (no code)
- Outputs JSON with sections, theme, features
- **Input**: ~1K tokens
- **Output**: ~500 tokens
- **Time**: 3-5 seconds
- **Cost**: ~$0.001

### Stage 3: Code Generation
- LLM generates complete files
- Outputs HTML, JavaScript, CSS
- **Input**: ~4K tokens
- **Output**: ~6K tokens
- **Time**: 20-30 seconds
- **Cost**: ~$0.08

### Stage 4: File Writing
- Parse markdown code blocks
- Write files to disk
- Generate README and requirements.txt
- **Time**: <1 second
- **Cost**: $0

## When to Use

**Use Simple Web3 Gen for:**
- ✅ Smart contract frontends
- ✅ Quick prototypes
- ✅ Standard token interfaces (ERC20, ERC721)
- ✅ Time-sensitive development

**Use CrewAI Pipeline for:**
- ✅ Complex AI agent UIs
- ✅ Domain-specific workflows (travel, insurance)
- ✅ Multi-step user interactions
- ✅ Custom design systems

## Integration with AIA_Interface

Both systems coexist:

```
AIA_Interface/
├── ui_generator_cli.py          # CrewAI (AI agents)
├── simple_web3_gen/             # This module (smart contracts)
└── generated_ui/
    ├── crewai_outputs/          # From ui_generator_cli.py
    └── simple_web3/             # From simple_web3_gen
```

## Troubleshooting

### "GEMINI_API_KEY not found"
→ Add `GEMINI_API_KEY=your_key` to `.env` file

### "ABI file not found"
→ Check path to ABI JSON file

### "No completion choices found"
→ Usually means the prompt is too long. This shouldn't happen with Simple Web3 Gen (uses only ~5K tokens)

### Generation takes longer than expected
→ Check your network connection. Stage 3 (code generation) should take 20-30 seconds max.

## Development

To modify prompts:
- Edit `prompts.py`

To change generation logic:
- Edit `generator.py`

To update CLI:
- Edit `cli.py`

## License

Part of AIA_Interface project.
