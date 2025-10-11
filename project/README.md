# Claim Triage Agent

## Overview

This CrewAI-powered agent automates the initial screening of insurance claims. It parses claim data, investigates the context using web searches, checks for common fraud indicators, and categorizes each claim as 'Standard', 'Complex', or 'Potential Fraud'. The final output is a JSON report detailing the triage decision and reasoning.

## Quickstart

### 1. Setup Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file in the root of the project and add your Serper API key.

```
SERPER_API_KEY="your_serper_api_key_here"
# OPENAI_API_KEY="your_openai_api_key_here" # Or configure another LLM
```

### 4. Run the Agent

You can run the agent from the command line, providing a path to a JSON file containing the claim details. An example claim file `sample_claim.json` is provided.

```bash
python -m src.claim_triage_agent.main --claim-file sample_claim.json
```

### 5. Run Tests

To ensure the system is set up correctly, run the smoke tests.

```bash
pytest
```

## Environment Variables

- `SERPER_API_KEY`: **Required**. Your API key for the Serper service, used by the Fraud Investigator Agent for web searches.
- `OPENAI_API_KEY`: **Optional**. Your OpenAI API key. If not set, you may need to configure a different LLM provider in your environment.