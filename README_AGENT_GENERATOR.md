# AI Agent Generator

A CrewAI-powered pipeline to turn your agent ideas into runnable Python agents, plus a verifier step to check syntax/imports/tests.

## What this adds

- A new package: `ai_agent_generator/`
- A CLI: `ai_agent_generator/agent_maker_cli.py`
- Pydantic schemas for idea/spec/bundle/verification
- A Crew with three agents:
  - AI Agent Architect (specifies the agent)
  - Agent Developer (generates code files)
  - Agent Verifier (checks syntax/import/tests)

## Prerequisites

- Python 3.9+
- A `.env` with `GEMINI_API_KEY` (required)
- Install dependencies (you can reuse `requirements_ui_generator.txt`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_ui_generator.txt
pip install pytest  # optional, if you want to run tests
```

## Usage

Generate an agent from an idea and write it into `./generated_agents/<slug>/`:

```bash
python -m ai_agent_generator.agent_maker_cli \
  --idea "A travel deal finder that monitors prices and alerts me via email" \
  --name "Travel Deal Notifier" \
  --output-dir ./generated_agents \
  --verify
```

- `--idea` is required.
- `--name` is optional; used to create the destination folder slug.
- `--output-dir` defaults to `./generated_agents`.
- `--verify` runs the verification step (syntax/import/tests).

## What gets generated

- Multiple Python modules (e.g., `agents.py`, `tasks.py`, `crew.py`, `main.py`)
- Optional tests under `tests/`
- An entrypoint script (usually `main.py`) you can run:

```bash
python generated_agents/travel-deal-notifier/main.py --help
```

## Notes

- The developer agent writes clear, typed code and uses `python-dotenv` to load env vars.
- The verifier agent runs AST parsing for syntax, attempts to import the entrypoint module, and optionally executes tests if produced.
- No secrets are ever written to code.

## Troubleshooting

- Ensure your `.env` contains a valid `GEMINI_API_KEY`.
- If verification fails on import, check the stack trace for missing dependencies and install them in your virtual environment.
- If tests fail, review `tests/test_smoke.py` and the generated code for API assumptions that need configuration.
