# Restaurant Booking Agent

## Overview

This project implements a multi-agent system using CrewAI to automate the process of handling restaurant reservation requests received via email. The agent can parse booking details, check for table availability against a mock booking system, create reservations, and draft email responses for confirmation or to suggest alternative times.

## Quickstart

### 1. Setup Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

Install the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root by copying the `.env.example` file:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys.

```ini
# Serper API Key for enhanced search capabilities (Optional)
SERPER_API_KEY="your_serper_api_key_here"
```

### 4. Run the Agent

You can run the agent from the command line. It takes the path to an email file as an argument. A sample email is provided in `data/sample_email.txt`.

```bash
python main.py --email-file data/sample_email.txt
```

The agent will process the email, interact with the mock booking system (`data/mock_bookings.json`), and save a drafted response in `drafted_email.out`.

### 5. Run Tests

To ensure everything is set up correctly, run the smoke tests using pytest.

```bash
pytest
```
