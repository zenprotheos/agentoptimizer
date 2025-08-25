---
id: oneshot-api
owner: oneshot-system
last_updated: 2025-08-25  
status: active
summary: Public interfaces, CLI commands, and integration points for the oneshot framework
---

# Versioning

- **Policy**: Semantic versioning for major changes, backward compatibility maintained for configuration files
- **Deprecation window**: 30 days notice for breaking changes, migration guides provided
- **Configuration compatibility**: Agent and tool definitions remain compatible across minor versions

# CLI Interface

## `./oneshot` - Primary CLI Entry Point

**Location**: `app/oneshot` (bash script)
**Purpose**: Direct agent execution from terminal

### Basic Usage
```bash
./oneshot <agent_name> "<message>" [--files file1|file2] [--run-id <id>] [--json] [--debug]
```

### Parameters
- `agent_name` - Name of specialist agent (research_agent, vision_agent, web_agent, etc.)
- `message` - Instructions for the agent to execute
- `--files` - Pipe-separated file paths to provide as context (optional)
- `--run-id` - Continue existing conversation (optional) 
- `--json` - Return structured JSON response instead of human-readable format
- `--debug` - Enable verbose logging and execution traces

### Response Format
**Success (human-readable)**:
```
Agent: research_agent
Run ID: 0825_164532_a1b2

[Agent response content]

Files created:
- artifacts/0825_164532_a1b2/research_report.md
- artifacts/0825_164532_a1b2/data_summary.json
```

**Success (JSON)**:
```json
{
  "success": true,
  "agent": "research_agent", 
  "run_id": "0825_164532_a1b2",
  "response": "[Agent response content]",
  "artifacts": [
    "artifacts/0825_164532_a1b2/research_report.md",
    "artifacts/0825_164532_a1b2/data_summary.json"
  ],
  "usage": {
    "tokens": 1250,
    "duration": 23.5
  }
}
```

**Error**:
```json
{
  "success": false,
  "error": "Agent 'invalid_agent' not found",
  "available_agents": ["research_agent", "vision_agent", "web_agent", ...]
}
```

# MCP Server Interface

## oneshot_mcp.py - Model Context Protocol Server

**Transport**: stdio (standard input/output)
**Protocol**: JSON-RPC over MCP
**Purpose**: Integration with Cursor IDE and other AI development tools

### Tools Exposed

#### `call_agent`
```json
{
  "name": "call_agent",
  "description": "Execute a specialist agent with message and optional file context",
  "parameters": {
    "agent_name": "string",
    "message": "string", 
    "files": "string (pipe-separated paths, optional)",
    "urls": "string (pipe-separated URLs, optional)",
    "run_id": "string (optional)",
    "debug": "boolean (optional)"
  }
}
```

#### `list_agents`  
```json
{
  "name": "list_agents",
  "description": "Get available agents with descriptions and capabilities",
  "parameters": {}
}
```

#### `list_tools`
```json
{
  "name": "list_tools", 
  "description": "Get available tools with metadata and parameters",
  "parameters": {}
}
```

#### `read_instructions_for`
```json
{
  "name": "read_instructions_for",
  "description": "Read system guides for agent/tool creation",
  "parameters": {
    "guide_name": "string (onboarding|how_oneshot_works|how_to_create_agents|how_to_create_tools|how_to_use_tool_services|how_to_create_mcp_servers)"
  }
}
```

#### `ask_oneshot_expert`
```json
{
  "name": "ask_oneshot_expert", 
  "description": "Get expert guidance on oneshot system architecture and usage",
  "parameters": {
    "question": "string"
  }
}
```

### Configuration

**Cursor Integration** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "oneshot": {
      "command": "python",
      "args": ["/absolute/path/to/oneshot/app/oneshot_mcp.py"]
    }
  }
}
```

# Tool Developer Interface

## Tool Creation Pattern

**File Location**: `tools/{tool_name}.py`
**Required Elements**: `TOOL_METADATA` dict, main function matching filename

### Tool Metadata Schema
```python
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "Clear description of tool purpose and capabilities",
        "parameters": {
            "type": "object", 
            "properties": {
                "param_name": {
                    "type": "string|number|boolean|array|object",
                    "description": "Parameter description"
                }
            },
            "required": ["required_param1", "required_param2"]
        }
    }
}
```

### Tool Services Integration
```python
from app.tool_services import *

def my_tool(param: str) -> str:
    # Use tool services functions
    result = llm(f"Process: {param}")
    saved = save(result, "Processing results") 
    return json.dumps({"filepath": saved["filepath"]})
```

## Agent Configuration Interface

**File Location**: `agents/{agent_name}.md`
**Format**: Markdown with YAML frontmatter + system prompt

### Agent Configuration Schema
```yaml
---
name: agent_name
description: "Agent purpose and capabilities"
model: "openai/gpt-5-nano" 
temperature: 0.7
max_tokens: 4096
tools:
  - tool_name1
  - tool_name2
mcp_servers:
  - server_name (optional)
---

# System Prompt Content
Agent instructions and behavior definition...
```

# External Integration Points

## OpenRouter LLM Gateway
- **Endpoint**: https://openrouter.ai/api/v1/
- **Authentication**: Bearer token via `OPENROUTER_API_KEY` environment variable
- **Models**: 200+ models available, configured per agent
- **Usage tracking**: Automatic token counting and cost monitoring

## Logfire Observability 
- **Integration**: Automatic instrumentation of all agent and tool operations
- **Authentication**: `LOGFIRE_TOKEN` environment variable
- **Data**: Execution traces, performance metrics, error tracking
- **Access**: Dashboard at logfire.pydantic.dev

## External APIs
- **Brave Search**: Web search functionality via `BRAVE_SEARCH_API_KEY`
- **Custom MCP Servers**: Configurable external service integrations
- **File System**: Controlled access to project directory and user-specified paths

# Configuration Files

## Global Configuration (`config.yaml`)
```yaml
model_settings:
  model: "openai/gpt-5-nano"
  temperature: 0.7
  max_tokens: 4096

usage_limits:
  request_limit: 100
  show_usage_stats: true

logfire:
  enabled: true
  service_name: "oneshot"
```

## Agent Defaults
- Model: openai/gpt-5-nano (cost-effective default)
- Temperature: 0.7 (balanced creativity/consistency)  
- Max tokens: 4096 (sufficient for most tasks)
- Retries: 1 (error recovery)
- Timeout: 30 seconds (prevents hangs)

# Error Codes & Responses

## Common Error Patterns
- `AGENT_NOT_FOUND`: Specified agent does not exist in agents/ directory
- `TOOL_LOADING_ERROR`: Tool file has syntax errors or missing metadata  
- `CONFIGURATION_ERROR`: Invalid YAML frontmatter in agent definition
- `API_AUTHENTICATION_ERROR`: Missing or invalid API keys
- `EXECUTION_TIMEOUT`: Agent execution exceeded timeout limits
- `FILE_ACCESS_ERROR`: Cannot read specified file paths
- `MODEL_NOT_AVAILABLE`: Requested model not supported by OpenRouter

## Error Response Format
```json
{
  "success": false,
  "error_code": "AGENT_NOT_FOUND", 
  "error_message": "Agent 'invalid_agent' not found",
  "suggestions": [
    "Check available agents with list_agents",
    "Verify agent name spelling",
    "Ensure agent file exists in agents/ directory"
  ],
  "available_agents": ["research_agent", "vision_agent", "web_agent"]
}
```

# Examples

## Basic Agent Call
```bash
./oneshot research_agent "Research the latest developments in quantum computing"
```

## Multi-file Context
```bash  
./oneshot vision_agent "Analyze these images" --files "image1.jpg|image2.png|report.pdf"
```

## Continuing Conversation
```bash
./oneshot research_agent "Expand on the quantum computing research" --run-id "0825_164532_a1b2"
```

## MCP Integration (via Cursor)
```python
# Cursor agent automatically calls:
call_agent(
    agent_name="web_agent",
    message="Find contact information for quantum computing researchers",
    files="artifacts/0825_164532_a1b2/research_report.md"
)
```
