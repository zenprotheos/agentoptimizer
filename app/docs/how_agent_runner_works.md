# How Agent Runner Works: Technical Deep Dive

This document provides a comprehensive technical analysis of the `agent_runner.py` module, which serves as the core orchestrator for the Oneshot agent framework. This module is the primary entry point for all agent executions, whether initiated via CLI or the MCP server.

## Overview

The `agent_runner.py` module is fundamentally a sophisticated wrapper around the **Pydantic AI** library. It handles the complete lifecycle of agent execution, from configuration parsing to result persistence, while providing robust error handling and observability through Logfire integration.

## Core Architecture

### Class Structure

#### `AgentConfig`
A simplified configuration container that holds all agent-specific settings:

```python
class AgentConfig:
    def __init__(self, config_data: Dict[str, Any]):
        self.name = config_data['name']
        self.description = config_data['description']
        self.model = config_data['model']
        self.temperature = config_data.get('temperature', 0.7)
        self.max_tokens = config_data.get('max_tokens', 2048)
        # ... other model parameters
        self.tools = config_data.get('tools', [])
        self.mcp = config_data.get('mcp', [])
        self.system_prompt = config_data['system_prompt']
```

**Purpose**: Encapsulates all agent configuration parameters in a single, validated object.

#### `AgentRunner`
The main orchestrator class that manages the complete agent execution pipeline:

```python
class AgentRunner:
    def __init__(self, agents_dir: str = "agents", tools_dir: str = "tools", 
                 config_file: str = "config.yaml", debug: bool = False):
```

**Key Responsibilities**:
- Configuration management (YAML loading, defaults application)
- Tool discovery and loading
- MCP server management
- Agent template processing
- Run persistence coordination
- Pydantic AI agent instantiation and execution

## Initialization Process

### 1. Directory and Path Setup
```python
project_root = Path(__file__).parent.parent
self.agents_dir = project_root / agents_dir
self.tools_dir = project_root / tools_dir
self.config_file = project_root / config_file
```

The runner establishes the project structure, ensuring all paths are relative to the project root.

### 2. Configuration Loading
```python
def _load_config(self) -> Dict[str, Any]:
    """Load configuration from YAML file"""
```

Loads the global `config.yaml` file, which contains:
- Model defaults (`model_settings`)
- Usage limits
- Logfire configuration
- Template engine settings

### 3. Tool Discovery and Loading
```python
def _load_tools(self, debug: bool = False):
    """Load all tools from the tools directory"""
```

**Process**:
1. Scans the `/tools` directory for Python files
2. Dynamically imports each module using `importlib.util`
3. Validates that each tool has `TOOL_METADATA`
4. Stores tool functions in `self.loaded_tools` dictionary

**Tool Structure Expected**:
```python
# In each tool file
TOOL_METADATA = {
    "name": "tool_name",
    "description": "Tool description"
}

def tool_name(param1: str) -> str:
    # Tool implementation
    pass
```

### 4. Logfire Setup
```python
def _setup_logfire(self, debug: bool = False):
    """Setup Logfire logging"""
```

**Configuration**:
- Checks for `LOGFIRE_WRITE_TOKEN` environment variable
- Configures service name, version, and environment
- Enables Pydantic AI instrumentation for automatic LLM call tracking
- Adjusts verbosity based on debug mode

### 5. Component Initialization
```python
# MCP configuration manager
self.mcp_config_manager = MCPConfigManager(project_root, self.config, debug=debug)

# Run persistence
self.run_persistence = RunPersistence(project_root / "runs")

# Template processor
self.template_processor = AgentTemplateProcessor(...)

# Validator
self.validator = AgentConfigValidator(...)
```

## Agent Execution Flow

### Entry Point: `run_agent_async()`

```python
async def run_agent_async(self, agent_name: str, message: str, 
                         files: List[str] = None, run_id: Optional[str] = None):
```

This is the core execution method that orchestrates the entire agent run process.

### Step 1: Run Management
```python
# Handle run continuation or creation
message_history = []
is_new_run = run_id is None

if run_id is None:
    run_id = self.run_persistence.generate_run_id()
else:
    if self.run_persistence.run_exists(run_id):
        message_history = self.run_persistence.get_message_history(run_id)
```

**Logic**:
- If no `run_id` provided → Generate new 8-character alphanumeric ID
- If `run_id` provided → Load existing conversation history from `/runs/{run_id}/run.json`
- Validates run existence and handles errors gracefully

### Step 2: Agent Configuration Parsing
```python
agent_file = self.agents_dir / f"{agent_name}.md"
config = await self._parse_agent_config(agent_file, files)
```

**Process Flow in `_parse_agent_config()`**:
1. **Template Processing**: Uses `AgentTemplateProcessor` to:
   - Extract YAML frontmatter from agent `.md` file
   - Process Jinja2 template with file contents (if provided)
   - Generate final system prompt
2. **Validation**: Uses `AgentConfigValidator` to:
   - Validate tool names exist in loaded tools
   - Validate MCP server names exist in configuration
   - Validate model names and numeric parameters
3. **Default Application**: Merges agent-specific config with global defaults from `config.yaml`

### Step 3: Model and Provider Setup
```python
model = OpenAIModel(
    model_name=config.model,
    provider=OpenAIProvider(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
)
```

**Error Handling**:
- Validates `OPENROUTER_API_KEY` environment variable
- Provides specific error messages for common issues:
  - 404: Model not found on OpenRouter
  - 401: Authentication failed
  - Other initialization errors

### Step 4: Model Settings Configuration
```python
model_settings = ModelSettings(
    temperature=config.temperature,
    max_tokens=config.max_tokens,
    top_p=config.top_p,
    presence_penalty=config.presence_penalty,
    frequency_penalty=config.frequency_penalty,
    timeout=config.timeout,
    stream=config.stream,
    parallel_tool_calls=True
)
```

**Configuration Hierarchy**:
1. Agent-specific settings (from YAML frontmatter)
2. Global defaults (from `config.yaml`)
3. Pydantic AI defaults

### Step 5: Tool and MCP Server Loading
```python
tool_functions = self._create_tool_functions(config.tools)
mcp_servers = await self._create_mcp_servers(config.mcp)
```

#### Tool Function Creation (`_create_tool_functions()`)
**Process**:
1. Iterates through requested tool names
2. Looks up each tool in `self.loaded_tools`
3. Extracts the actual function object
4. Provides helpful error messages with suggestions for typos
5. Returns list of callable functions for Pydantic AI

**Error Handling**:
- Fuzzy matching for typo suggestions
- Lists all available tools
- Continues execution with available tools (doesn't fail completely)

#### MCP Server Creation (`_create_mcp_servers()`)
**Process**:
1. Processes MCP configuration (string names or `MCPServerConfig` objects)
2. Looks up server configuration in MCP JSON files
3. Creates actual MCP server instances using `MCPConfigManager`
4. Handles connection and authentication errors gracefully

### Step 6: Agent Instantiation
```python
if mcp_servers:
    agent = Agent(
        model=model,
        system_prompt=config.system_prompt,
        tools=tool_functions if tool_functions else [],
        model_settings=model_settings,
        mcp_servers=mcp_servers
    )
else:
    agent = Agent(
        model=model,
        system_prompt=config.system_prompt,
        tools=tool_functions if tool_functions else [],
        model_settings=model_settings
    )
```

**Note**: Separate instantiation paths for agents with and without MCP servers due to Pydantic AI requirements.

### Step 7: Agent Execution
```python
if mcp_servers:
    async with agent.run_mcp_servers():
        result = await agent.run(message, message_history=message_history, usage_limits=usage_limits)
else:
    result = await agent.run(message, message_history=message_history, usage_limits=usage_limits)
```

**Key Points**:
- MCP servers require async context management
- Message history enables conversation continuity
- Usage limits prevent runaway costs
- Pydantic AI handles all LLM interaction, tool calling, and response generation

### Step 8: Response Processing and Persistence
```python
response_data = {
    "output": str(result.output),
    "success": True,
    "run_id": run_id,
    "is_new_run": is_new_run,
    "usage": {
        "requests": result.usage().requests,
        "request_tokens": result.usage().request_tokens,
        "response_tokens": result.usage().response_tokens,
        "total_tokens": result.usage().total_tokens,
    },
    "tool_calls_summary": self._extract_tool_call_summary(result.all_messages())
}

# Update run persistence with new messages
self.run_persistence.update_run(run_id, response_data, result.new_messages())
```

**Data Captured**:
- Agent output (the actual response)
- Success/failure status
- Run identification and continuation status
- Detailed usage statistics
- Tool call summary
- Complete message history (for persistence)

## Configuration Hierarchy System

The agent runner implements a sophisticated configuration hierarchy that allows for flexible parameter management:

### 1. Agent-Specific Configuration (Highest Priority)
From the agent's `.md` file YAML frontmatter:
```yaml
---
name: research_agent
model: "openai/gpt-4o-mini"
temperature: 0.3
max_tokens: 4096
tools:
  - web_search
  - web_read_page
---
```

### 2. Global Defaults (Fallback)
From `config.yaml`:
```yaml
model_settings:
  model: "openai/gpt-4o-mini"
  temperature: 0.7
  max_tokens: 2048
  timeout: 30.0
```

### 3. Pydantic AI Defaults (Lowest Priority)
Built-in defaults from the Pydantic AI library.

## Error Handling Strategy

The agent runner implements comprehensive error handling at multiple levels:

### Configuration Errors
```python
except AgentConfigError as e:
    return {
        "output": "",
        "success": False,
        "error": f"Agent Configuration Error: {e.get_formatted_message()}",
        "error_type": "configuration",
        "agent_file": str(agent_file)
    }
```

**Handles**:
- Invalid YAML frontmatter
- Missing required fields
- Invalid tool names
- Invalid MCP server names
- Invalid model parameters

### API and Model Errors
```python
if "404" in model_error or "not found" in model_error.lower():
    return {
        "error": f"Model '{config.model}' not found on OpenRouter...",
        "error_type": "model_not_found",
        "model_name": config.model
    }
```

**Handles**:
- Model not found (404)
- Authentication failures (401)
- API key issues
- Network connectivity problems

### MCP Server Errors
```python
if "401 Unauthorized" in error_message:
    return {
        "error": f"MCP server authentication failed: {e}\n"
                f"This usually means the MCP server requires authentication credentials.\n"
                f"Check your MCP server configuration for missing API keys or tokens."
    }
```

**Handles**:
- Authentication failures
- Connection timeouts
- Server unavailability
- Configuration issues

## CLI Interface

The module provides a command-line interface through the `main()` function:

```bash
python agent_runner.py <agent_name> <message> [--files <file1|file2|...>] [--run-id <run_id>] [--json] [--debug]
```

**Arguments**:
- `agent_name`: Name of the agent to execute
- `message`: User message to send to the agent
- `--files`: Pipe-separated list of file paths to provide as context
- `--run-id`: Continue an existing conversation
- `--json`: Output raw JSON response
- `--debug`: Enable verbose debug output

## Integration Points

### With MCP Server (`oneshot_mcp.py`)
The agent runner is called by the MCP server through the `call_agent` endpoint, which essentially wraps the CLI interface.

### With Run Persistence (`run_persistence.py`)
Manages conversation state across multiple interactions:
- Creates new runs with unique IDs
- Loads existing conversation history
- Updates runs with new messages and metadata

### With Template Processor (`agent_template_processor.py`)
Handles dynamic content injection:
- Processes Jinja2 templates in agent files
- Injects file contents when `--files` is used
- Manages template snippets and includes

### With Tool Services (`tool_services.py`)
Provides helper functions for tools:
- Sets run ID context for file organization
- Provides common utilities for tool implementations

## Performance and Observability

### Logfire Integration
Automatic instrumentation provides:
- Complete traces of agent execution
- LLM API call details
- Tool execution traces
- Performance metrics
- Error tracking

### Usage Tracking
Built-in usage limits and tracking:
```python
usage_limits = UsageLimits(
    request_limit=50,
    request_tokens_limit=None,
    response_tokens_limit=None,
    total_tokens_limit=None
)
```

### Debug Mode
Comprehensive debug output when enabled:
- Tool loading details
- MCP server initialization
- Configuration merging
- Error details and stack traces

## Best Practices for Modifications

### 1. Preserve Error Handling
Any modifications should maintain the comprehensive error handling patterns, providing specific error types and helpful messages.

### 2. Maintain Configuration Hierarchy
Respect the three-tier configuration system (agent-specific → global → defaults).

### 3. Update Documentation
Changes to core logic should trigger updates to this document and `how_oneshot_works.md`.

### 4. Test with Debug Mode
Always test modifications with `debug=True` to ensure proper logging and error visibility.

### 5. Consider Backwards Compatibility
Agent files and tool interfaces should remain compatible across updates.

## Common Troubleshooting Scenarios

### Agent Not Found
- Check agent file exists in `/agents/{agent_name}.md`
- Verify file permissions and readability

### Tool Loading Failures
- Verify tool files have `TOOL_METADATA`
- Check for syntax errors in tool files
- Ensure tool function names match file names

### MCP Server Issues
- Verify MCP server configuration in `.cursor/mcp.json`
- Check authentication credentials
- Test server connectivity independently

### Model API Errors
- Validate `OPENROUTER_API_KEY` environment variable
- Check model name against OpenRouter's available models
- Verify account credits and rate limits

### Run Persistence Problems
- Check `/runs` directory permissions
- Verify run ID format (8 alphanumeric characters)
- Look for corrupted `run.json` files

This comprehensive architecture makes the agent runner a robust, observable, and extensible foundation for the Oneshot agent framework. 