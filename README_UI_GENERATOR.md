# AI Agent UI/UX Generator

A powerful AI-powered tool that automatically generates tailored UI/UX interfaces for different AI agents based on their purpose, capabilities, and user preferences. This system uses a chain prompt pipeline to analyze agent requirements and create beautiful, functional interfaces.

## Features

- **Agent Configuration**: Define your AI agent's purpose, capabilities, and API integrations
- **Dynamic UI/UX Generation**: Automatically creates tailored interfaces based on agent analysis
- **User Preference Integration**: Customize themes, layouts, and color schemes
- **Complete Frontend Code**: Generates HTML, CSS, and JavaScript code ready for deployment
- **Live Preview**: View the generated UI in real-time

## Project Structure

```
AIA_Interface/
├── ui_generator.py            # Flask application entry point
├── ui_generator_crew.py       # CrewAI agent and task definitions for UI generation
├── templates/                 # HTML templates
│   └── index.html             # Main interface for the UI generator
├── static/                    # Static assets
│   └── generated/             # Directory for generated UI code
├── .env                       # Environment variables configuration
└── README_UI_GENERATOR.md     # This documentation
```

## Installation

1. Ensure you have Python 3.8+ installed
2. Install dependencies:
   ```bash
   pip install flask crewai pydantic python-dotenv
   ```
3. Create a `.env` file with the following variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Usage

### Starting the Server

Start the Flask server:

```bash
python ui_generator.py
```

The server will be available at `http://localhost:5000`.

### Creating an AI Agent UI

1. Open your browser and navigate to `http://localhost:5000`
2. Fill in the form with your AI agent details:
   - **Agent Description**: Describe the purpose and functionality of your AI agent
   - **Agent Capabilities**: List the key capabilities of your agent
   - **API Integrations**: Specify any APIs your agent will use (optional)
   - **User Preferences**: Select theme, layout, color scheme, and font size
3. Click "Generate UI/UX"
4. View the generated UI in the preview panel
5. Examine the generated HTML, CSS, and JavaScript code
6. Download the files for use in your project

## Architecture

The application follows a pipeline architecture using CrewAI:

1. **Agent Analyzer**: Analyzes the agent description and capabilities to determine the optimal UI/UX approach
2. **UI Designer**: Designs the components, layout, and interaction model based on the agent analysis
3. **Frontend Developer**: Implements the design as clean, maintainable HTML, CSS, and JavaScript code

Each stage in the pipeline builds on the previous stage's output, creating a cohesive and tailored UI/UX solution.

## API Reference

### POST /api/generate-ui

Generates a UI/UX interface based on the provided agent specifications.

**Request Body**:
```json
{
  "agent_description": "A travel planning assistant that helps users find destinations and create itineraries",
  "agent_capabilities": "Search destinations, create itineraries, recommend hotels and flights",
  "agent_api": "OpenAI API for text generation, Google Maps API for location data",
  "user_preferences": {
    "theme": "dark",
    "layout": "compact",
    "color_scheme": "blue",
    "font_size": "medium"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "UI generation completed successfully",
  "ui_code": {
    "index.html": "<!-- HTML code -->",
    "styles.css": "/* CSS code */",
    "app.js": "// JavaScript code"
  },
  "preview_url": "/static/generated/index.html",
  "logs": "Process logs..."
}
```

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

## Dependencies

- **Flask**: Web framework for building the application
- **CrewAI**: Framework for creating autonomous AI agents
- **Pydantic**: Data validation and settings management
- **Python-dotenv**: Environment variable management

## Environment Variables

- `GEMINI_API_KEY`: API key for Google's Gemini model (required)

## Troubleshooting

- **Missing API Keys**: Ensure the GEMINI_API_KEY is set in your `.env` file
- **Generation Errors**: Check the logs for detailed error information
- **Preview Issues**: If the preview doesn't load, check the generated HTML for syntax errors
