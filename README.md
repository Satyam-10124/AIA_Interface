# AI dApp Developer Assistant

A powerful AI-powered assistant for generating, testing, and deploying decentralized applications (dApps) on various blockchain networks. This tool leverages CrewAI agents and the CodeInterpreterTool to automate the development process of smart contracts, frontend code, and deployment scripts.

## Features

- **Smart Contract Generation**: Creates secure, gas-efficient smart contracts based on your requirements
- **Frontend Development**: Generates interactive web frontends with blockchain integration
- **Deployment Scripts**: Provides deployment scripts and configurations for your chosen blockchain
- **Framework Flexibility**: Supports multiple blockchain frameworks (Hardhat, Truffle, etc.)
- **Frontend Framework Options**: Supports various frontend frameworks (React, Vue, Angular)

## Project Structure

```
CodeToolAgent/
├── app.py                # FastAPI application entry point
├── crew.py               # CrewAI agent and task definitions
├── .env                  # Environment variables configuration
├── requirements.txt      # Python dependencies
├── README.md             # This documentation
└── venv/                 # Python virtual environment
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

## Usage

### Starting the Server

Start the FastAPI server:

```bash
venv/bin/python app.py
```

The server will be available at `http://localhost:8000`.

### Building a dApp

Send a POST request to the `/build-and-deploy-dapp` endpoint with your dApp specifications:

```bash
curl -X POST "http://localhost:8000/build-and-deploy-dapp" \
-H "Content-Type: application/json" \
-d '{
  "description": "A simple NFT minting DApp that allows users to mint a unique token with an image, and also lists minted NFTs.",
  "blockchain": "Ethereum",
  "framework": "hardhat",
  "frontend_framework": "react",
  "tests_required": true
}'
```

### Example Projects

You can use the assistant to build various types of dApps, including:

1. **NFT Minting Platforms**
   ```json
   {
     "description": "A simple NFT minting DApp that allows users to mint a unique token with an image, and also lists minted NFTs.",
     "blockchain": "Ethereum",
     "framework": "hardhat",
     "frontend_framework": "react",
     "tests_required": true
   }
   ```

2. **E-commerce Platforms**
   ```json
   {
     "description": "An e-commerce dApp that allows users to browse products, add items to cart, process payments with cryptocurrency, and track order history. Include product listings with images, descriptions, and prices.",
     "blockchain": "Arbitrum Sepolia",
     "framework": "hardhat",
     "frontend_framework": "react",
     "tests_required": true
   }
   ```

3. **DAO Governance**
   ```json
   {
     "description": "A DAO governance dApp where users can create proposals, vote on them, and execute decisions based on voting results. Include token-weighted voting and proposal execution mechanisms.",
     "blockchain": "Polygon",
     "framework": "hardhat",
     "frontend_framework": "vue",
     "tests_required": true
   }
   ```

## Architecture

The application follows a modular architecture using CrewAI:

1. **Smart Contract Agent**: Generates secure, gas-efficient smart contracts based on user requirements
2. **Frontend Developer Agent**: Creates interactive web frontend interfaces for dApp user interaction
3. **Deployment Script Agent**: Creates deployment scripts for the specified blockchain network

Each agent is specialized in its domain and uses tools like CodeInterpreterTool and FileWriterTool to accomplish tasks.

## API Reference

### POST /build-and-deploy-dapp

Generates a complete dApp based on the provided specifications.

**Request Body**:
```json
{
  "description": "Description of the dApp functionality",
  "blockchain": "Target blockchain (e.g., Ethereum, Polygon, Arbitrum)",
  "framework": "Development framework (e.g., hardhat, truffle)",
  "frontend_framework": "Frontend framework (e.g., react, vue, angular)",
  "tests_required": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "dApp generated successfully",
  "generated_code": {
    "SmartContract.sol": "// Smart contract code...",
    "App.jsx": "// Frontend code...",
    "deploy.js": "// Deployment script..."
  },
  "logs": "Process logs...",
  "deployment_instructions": "Step-by-step deployment instructions..."
}
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **CrewAI**: Framework for creating autonomous AI agents
- **CrewAI-tools**: Tools for CrewAI (CodeInterpreterTool, SerperDevTool, FileWriterTool)
- **Pydantic**: Data validation and settings management
- **Python-dotenv**: Environment variable management

## Environment Variables

- `GEMINI_API_KEY`: API key for Google's Gemini model (required)
- `SERPER_API_KEY`: API key for the Serper search tool (for web search capabilities)
- `AZURE_LLM_MODEL_NAME`: Optional, for using Azure OpenAI models

## Troubleshooting

- **Missing API Keys**: Ensure all required API keys are set in your `.env` file
- **Model Output Format**: If experiencing issues with output parsing, check the logs for detailed error information
- **Task Outputs**: The CrewAI agents need to return outputs in the expected format

## License

This project is licensed under the MIT License.
