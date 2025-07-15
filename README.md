# Simple AI Agent Framework

A minimal but robust AI Agent framework using Pydantic AI and OpenRouter for your friends to easily create and run AI agents.

## Features

- **Simple agent creation**: Just add a markdown file to `/agents`
- **Flexible tool system**: Python scripts in `/tools` with OpenAI tools spec
- **Pydantic AI integration**: Built on the modern Pydantic AI framework
- **OpenRouter support**: Use any model available on OpenRouter
- **Robust error handling**: Comprehensive error handling and validation
- **Clean output by default**: Returns clean markdown with usage statistics
- **Debug mode**: Detailed tool call information available with `--debug` flag
- **Structured responses**: JSON output with detailed execution metadata

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your OpenRouter API key**:
   
   Either set it as an environment variable:
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file in the project root:
   ```
   OPENROUTER_API_KEY=your-api-key-here
   ```

3. **Run an agent**:
   ```bash
   python3 app/agent_runner.py web_agent "Search for information about Pydantic AI"
   ```

   Or get structured JSON output:
   ```bash
   python3 app/agent_runner.py web_agent "Search for information about Pydantic AI" --json
   ```

   Or get detailed debug output:
   ```bash
   python3 app/agent_runner.py web_agent "Search for information about Pydantic AI" --debug
   ```

## Creating Agents

Create a new agent by adding a markdown file to the `/agents` directory. The file should have this structure:

```markdown
---
name: my_agent
description: "Description of what this agent does"
model: openai/gpt-4o-mini    # Optional: overrides config.yaml default
temperature: 0.7             # Optional: overrides config.yaml default
max_tokens: 2048            # Optional: overrides config.yaml default
tools:
  - web_search
  - web_read_page
---

# ABOUT YOU

You are a helpful assistant...

## YOUR APPROACH

Your system prompt goes here...
```

## Configuration

The framework supports global configuration via `config.yaml`:

```yaml
# Default model settings (can be overridden per agent)
model_settings:
  model: "openai:gpt-4o-mini"
  temperature: 0.7
  max_tokens: 2048
  top_p: null
  presence_penalty: null
  frequency_penalty: null
  parallel_tool_calls: true
  seed: null
  stop_sequences: null
  timeout: 30.0

# Agent defaults
agent_defaults:
  retries: 1
  output_retries: 1
  end_strategy: "early"

# Usage limits to prevent infinite loops and control costs
usage_limits:
  request_limit: 50              # Max requests per agent run (prevents infinite loops)
  request_tokens_limit: null     # Max tokens in requests (null = no limit)
  response_tokens_limit: null    # Max tokens in responses (null = no limit)
  total_tokens_limit: null       # Max total tokens (null = no limit)
```

## Creating Tools

Create tools by adding Python scripts to the `/tools` directory. Each tool must have:

1. **TOOL_METADATA**: A dict conforming to OpenAI tools spec
2. **Function with same name as file**: The function that implements the tool

Example tool structure:

```python
#!/usr/bin/env python3

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "What this tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                }
            },
            "required": ["param1"]
        }
    }
}

def my_tool(param1: str) -> str:
    """Tool implementation"""
    return f"Result: {param1}"
```

**Important**: The function name must match the filename (e.g., `my_tool.py` contains `def my_tool(...)`).

## Directory Structure

```
basic/
├── agents/           # Agent definitions (.md files)
│   └── web_agent.md
├── tools/            # Tool implementations (.py files)
│   ├── web_search.py
│   └── web_read_page.py
├── app/
│   └── agent_runner.py
├── requirements.txt
└── README.md
```

## Output Formats

The framework supports three output formats:

### 1. Clean Output (Default)
Returns clean markdown with the agent's response and concise usage statistics:
```bash
python3 app/agent_runner.py web_agent "What is the weather like today?"
```
Output:
```
The weather in Brisbane today is partly cloudy with light winds...

---
**Usage:** 3 requests, 2,879 tokens
**Tools used:** web_read_page, web_search
```

### 2. Debug Output
Returns detailed information including tool calls, token breakdown, and execution details:
```bash
python3 app/agent_runner.py web_agent "What is the weather like today?" --debug
```
Additional debug information includes:
- Detailed token usage (request/response breakdown)
- Complete tool call history with arguments and results
- Model-specific details (caching, reasoning tokens, etc.)

### 3. JSON Output
Returns structured data for programmatic use:
```bash
python3 app/agent_runner.py web_agent "What is the weather like today?" --json
```

## Usage Examples

### Command Line Usage

```bash
# Basic usage - returns clean markdown output with usage statistics
python3 app/agent_runner.py web_agent "What is the weather like today?"

# JSON output - returns structured data
python3 app/agent_runner.py web_agent "What is the weather like today?" --json

# Debug output - returns detailed information including tool calls
python3 app/agent_runner.py web_agent "What is the weather like today?" --debug
```

### Programmatic Usage

```python
from app.agent_runner import AgentRunner, AgentResponse

runner = AgentRunner()

# Get structured response with usage stats and tool calls
result = runner.run_agent("web_agent", "Search for Python tutorials")

if isinstance(result, AgentResponse):
    print(f"Output: {result.output}")
    print(f"Success: {result.success}")
    print(f"Usage: {result.usage.requests} requests, {result.usage.total_tokens} tokens")
    print(f"Tool calls: {len(result.tool_calls)}")
    
    # Access individual tool calls
    for tool_call in result.tool_calls:
        print(f"Tool: {tool_call.tool_name}")
        print(f"Arguments: {tool_call.arguments}")
        print(f"Result: {tool_call.result}")

# Get JSON string response
json_result = runner.run_agent_json("web_agent", "Search for Python tutorials")
print(json_result)
```

### Response Structure

The `AgentResponse` object contains:

- `output`: The agent's response text
- `usage`: Token and request usage statistics
  - `requests`: Number of API requests made
  - `request_tokens`: Tokens used in requests
  - `response_tokens`: Tokens used in responses
  - `total_tokens`: Total tokens used
  - `details`: Additional model-specific details
- `tool_calls`: List of tool calls made during execution
  - `tool_name`: Name of the tool called
  - `call_id`: Unique identifier for the tool call
  - `arguments`: Arguments passed to the tool
  - `result`: Result returned by the tool
- `success`: Boolean indicating if execution was successful
- `error`: Error message if execution failed (null if successful)

## Available Tools

- **web_search**: Search the web using DuckDuckGo API
- **web_read_page**: Read and extract content from web pages

## Models

The framework supports any model available on OpenRouter. Popular choices:

- `openai/gpt-4o-mini` (fast, cheap)
- `openai/gpt-4o` (most capable)
- `anthropic/claude-3.5-sonnet` (excellent reasoning)
- `google/gemini-pro` (good performance)

## Error Handling

The framework includes comprehensive error handling:

- Agent file parsing errors
- Tool loading errors
- Model execution errors
- Network request failures

All errors are returned as descriptive strings rather than exceptions.

## Contributing

1. Add new tools to `/tools` following the OpenAI tools spec
2. Create new agents in `/agents` with proper YAML frontmatter
3. Test your changes with the provided examples

## License

MIT License - feel free to use and modify for your projects! 