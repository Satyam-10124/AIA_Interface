# AI Agent UI/UX Generator CLI

A command-line tool that automatically generates tailored UI/UX interfaces for different AI agents based on their purpose, capabilities, and user preferences. This tool uses a chain prompt pipeline to analyze agent requirements and create beautiful, functional interfaces.

## Installation

1. Run the setup script to install all required dependencies:

```bash
python3 setup_cli.py
```

2. Edit the `.env` file to add your API keys:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

The CLI tool provides a simple interface to generate UI/UX for AI agents:

```bash
python3 ui_generator_cli.py --agent-description "A travel planning assistant that helps users find destinations and create itineraries" --agent-capabilities "Search destinations, create itineraries, recommend hotels and flights" --theme dark --color-scheme blue
```

### Command Line Arguments

| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `--agent-description` | `-d` | Description of the AI agent's purpose and functionality | Yes |
| `--agent-capabilities` | `-c` | Comma-separated list of the agent's key capabilities | Yes |
| `--agent-api` | `-a` | APIs the agent will use | No |
| `--theme` | `-t` | UI theme preference (light, dark, system) | No |
| `--layout` | `-l` | UI layout preference (standard, compact, expanded) | No |
| `--color-scheme` | `-cs` | UI color scheme (blue, green, purple, red, orange, teal) | No |
| `--font-size` | `-fs` | UI font size preference (small, medium, large) | No |
| `--output-dir` | `-o` | Directory to save the generated UI files | No |
| `--verbose` | `-v` | Enable verbose output | No |

### Example Commands

1. **Basic Usage**:
   ```bash
   python3 ui_generator_cli.py -d "A customer support chatbot" -c "Answer FAQs, troubleshoot issues, escalate to human support"
   ```

2. **With User Preferences**:
   ```bash
   python3 ui_generator_cli.py -d "An educational tutor for mathematics" -c "Explain concepts, provide practice problems, give feedback" -t dark -l compact -cs purple
   ```

3. **With API Integration and Custom Output Directory**:
   ```bash
   python3 ui_generator_cli.py -d "A news aggregator assistant" -c "Fetch news, summarize articles, filter by topic" -a "NewsAPI, OpenAI API" -o "./news_ui"
   ```

## Output

The tool generates the following files in the specified output directory (default: `./generated_ui`):

- `index.html`: The main HTML structure for the UI
- `styles.css`: CSS styles for the UI
- `app.js`: JavaScript functionality for the UI
- `design_tokens.json`: Design tokens used for styling
- `preview.html`: A simple preview file (if index.html is not generated)

## How It Works

The CLI tool uses a pipeline of AI agents to generate the UI/UX:

1. **Agent Analyzer**: Analyzes the agent description and capabilities to determine the optimal UI/UX approach
2. **UI Designer**: Designs the components, layout, and interaction model based on the agent analysis
3. **Frontend Developer**: Implements the design as clean, maintainable HTML, CSS, and JavaScript code

Each stage in the pipeline builds on the previous stage's output, creating a cohesive and tailored UI/UX solution.

## Troubleshooting

If you encounter any issues:

1. Ensure your API keys are correctly set in the `.env` file
2. Check that all dependencies are installed by running `setup_cli.py` again
3. Use the `--verbose` flag to see detailed logs of the generation process

## Example Agent Types

You can use the generator for various types of AI agents, including:

1. **Travel Planning Assistant**
   ```
   Description: An AI agent that helps users plan trips by suggesting destinations, creating itineraries, and booking accommodations.
   Capabilities: Destination search, itinerary creation, hotel and flight recommendations, budget planning
   ```

2. **Customer Support Agent**
   ```
   Description: An AI agent that handles customer inquiries, troubleshoots common issues, and escalates complex problems to human agents.
   Capabilities: Answer FAQs, troubleshoot technical issues, process returns and refunds, escalate to human support
   ```

3. **Educational Tutor**
   ```
   Description: An AI agent that provides personalized learning assistance across various subjects and adapts to the student's learning style.
   Capabilities: Answer questions, provide explanations, generate practice problems, track learning progress
   ```
