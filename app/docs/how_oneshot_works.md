# How the Oneshot System Works: A Technical Guide for AI Agents

This document provides a technical deep-dive into the Oneshot system's core architecture and code, intended for an AI agent responsible for its maintenance, extension, and troubleshooting.

## Core Philosophy: Pydantic AI Engine

The system is fundamentally a wrapper around the **Pydantic AI** library. Pydantic AI is responsible for:
1.  **LLM Interaction**: Managing API calls to the specified LLM provider (OpenRouter).
2.  **System Prompt Construction**: Taking the processed agent definition as the primary instruction.
3.  **Tool Orchestration**: Binding Python functions (from `/tools`) to the agent and handling tool calls and responses.
4.  **Message History Management**: Appending user, assistant, and tool messages to the conversation context.

Your primary analysis of agent execution issues should start with the assumption that the core logic is being executed by a `pydantic_ai.agent.Agent` instance.

## System Execution Flow

### 1. Primary Entry Point: `agent_runner.py`

The main execution logic resides in `app/agent_runner.py`. This script is the orchestrator for any agent run, whether initiated from the command line or the MCP server.

Its key responsibilities are:
- **Argument Parsing**: Uses `click` to parse CLI arguments (`agent_name`, `message`, `--run-id`, `--files`).
- **Configuration Loading**: Reads `config.yaml` to load model defaults, framework settings, and other global configuration parameters.
- **Agent Definition Loading**: Reads the specified agent's markdown file from `/agents/{agent_name}.md`.
- **Tool Loading**: Dynamically imports and collects tool functions from the `/tools/` directory via `app/tool_services.py`.
- **Context Processing**: Utilizes `app/agent_template_processor.py` to inject dynamic content (like passed file contents) into the agent's system prompt.
- **Run Persistence**: Interacts with `app/run_persistence.py` to load a message history for an existing run or create a new one.
- **Agent Invocation**: Instantiates the Pydantic AI agent and executes it with the message history and system prompt.
- **State Saving**: Saves the updated message history as runs.json to the /runs directory.

### 2. Conversation State Management: `run_persistence.py`

Pydantic AI is stateless. This system achieves conversation continuity via `app/run_persistence.py`.

- **Class**: `RunPersistence`
- **Storage Location**: `/runs/{run_id}/`
- **Mechanism**: Each run is an 8-character alphanumeric ID. The directory contains three key files:
    - `run.json`: The complete state, including all metadata and the Pydantic AI message list. This is the canonical source of truth for a run.
- **Key Methods**:
    - `load_run(run_id)`: Reads `run.json` and returns the message history.
    - `save_run(...)`: Updates `run.json` with the latest state after an agent execution.
    - `create_run(...)`: Creates a new run directory and initial files.

**Troubleshooting**: Issues with conversation history, "run not found" errors, or context loss are almost always located in this module or are due to corrupted/missing files in the `/runs` directory.

### 3. Dynamic Context Injection: `agent_template_processor.py`

This module is responsible for preparing the final system prompt that Pydantic AI uses. It processes the agent's `.md` file as a Jinja2 template.

- **Primary Function**: It injects dynamic content into the agent's prompt *before* execution.
- **File Passing Implementation**: The file passing feature (`--files` argument) is handled here. The processor reads the content of the specified files and injects them into the prompt using the `provided_files` template variable.
- **Template Snippet**: The `{% include "provided_content.md" %}` directive in an agent's template is the placeholder where this module injects the file content.

**Troubleshooting**: If an agent is not "seeing" the content of passed files, the issue is likely within this processor or the agent's `.md` template is missing the correct include snippet.

### 4. API Exposure: `oneshot_mcp.py`

This script exposes the core functionality of `agent_runner.py` as a service using the **FastMCP** framework.

- **Mechanism**: It defines functions (e.g., `call_agent`, `list_agents`) that are decorated to become MCP endpoints.
- **Execution**: Internally, these functions often call the logic from `agent_runner.py` or other application modules. For example, `call_agent` essentially simulates a CLI call to `agent_runner.py`.
- **Purpose**: Allows other systems (including other AI agents or a UI) to interact with the Oneshot agent system programmatically.

**Troubleshooting**: If the MCP server is running but agent calls fail, inspect the `subprocess` calls within `oneshot_mcp.py` to ensure they correctly invoke the `agent` script. Changes to the mcp server require a restart of the server. The user will have to do this manually (not you, the coding agent), in Cursor>Settings>Cursor Settings>Tools & Integrations by toggling the setting on and off again. Sometimes, Cursor requires a restart because there is some kind of cached background process for the mcp server. In the worst case, inspect background processes.

## External Service Integration

- **OpenRouter**: The LLM gateway. The API key (`OPENROUTER_API_KEY`) is passed directly to the Pydantic AI `Agent` constructor. All LLM API errors originate from here.
- **Logfire**: The observability platform. The system is configured to automatically instrument Pydantic AI calls. Logfire provides detailed traces of agent execution, including tool calls, LLM inputs/outputs, and performance metrics. It is the primary source for debugging runtime behavior.
- **Context7**: A documentation service, accessed via a dedicated MCP tool. It is not part of the core execution logic but is a resource for you to query for external library documentation.

## Model Parameter Loading and Configuration Hierarchy

The system uses a **hierarchical configuration approach** where agent-specific settings override global defaults. This allows for flexible model configuration while maintaining sensible defaults.

### Configuration Sources (in order of precedence):

1. **Agent File YAML Frontmatter** (highest priority)
2. **`config.yaml` model_settings** (fallback defaults)
3. **Pydantic AI defaults** (lowest priority)

### Implementation in `agent_runner.py`:

The parameter loading happens in the `_parse_agent_config()` method:

```python
async def _parse_agent_config(self, agent_file: Path, files: List[str] = None) -> AgentConfig:
    """Parse agent configuration using template processor"""
    try:
        # 1. Extract agent-specific config from YAML frontmatter
        template_result = await self.template_processor.process_agent_template(
            agent_file=agent_file,
            files=files,
            additional_context={}
        )
        
        config_data = template_result['config_data']
        
        # 2. Apply defaults from config.yaml for any missing parameters
        model_defaults = self.config.get('model_settings', {})
        for key, default_value in model_defaults.items():
            if key not in config_data:
                config_data[key] = default_value
        
        return AgentConfig(config_data)
```

### Parameter Categories:

#### **Core Model Settings**:
- `model`: LLM model name (e.g., "openai/gpt-4o-mini")
- `temperature`: Creativity level (0.0-2.0)
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling parameter
- `presence_penalty`: Penalty for new topics
- `frequency_penalty`: Penalty for repetition
- `timeout`: Request timeout in seconds

#### **Agent Behavior Settings**:
- `tools`: List of available tools for the agent
- `mcp`: List of MCP servers to load
- `stream`: Whether to use streaming responses

### Example Configuration Scenarios:

#### Scenario 1: Agent with Custom Settings
```yaml
# agents/research_agent.md frontmatter
---
name: research_agent
description: "Conducts thorough research"
model: "openai/gpt-4.1-mini"           # Overrides config.yaml default
temperature: 0.3                  # Lower temperature for factual work
max_tokens: 4096                  # Longer responses than default
tools:
  - web_search
  - web_read_page
---
```

#### Scenario 2: Agent Using Global Defaults
```yaml
# agents/simple_agent.md frontmatter
---
name: simple_agent
description: "Basic assistant"
# No model parameters specified - will use config.yaml defaults
---
```

#### Scenario 3: Mixed Configuration
```yaml
# agents/creative_agent.md frontmatter
---
name: creative_agent
description: "Creative writing assistant"
temperature: 0.9                  # Override for creativity
# model, max_tokens, etc. will use config.yaml defaults
---
```

### Global Defaults in `config.yaml`:

```yaml
model_settings:
  model: "openai/gpt-4.1-mini"    # Default model for all agents
  temperature: 0.7                # Balanced creativity
  max_tokens: 2048                # Standard response length
  top_p: null                     # Use temperature instead
  presence_penalty: null          # No penalty by default
  frequency_penalty: null         # No penalty by default
  timeout: 30.0                   # 30 second timeout
  parallel_tool_calls: true       # Allow multiple tool calls
```

### Parameter Application Flow:

1. **Agent Template Processing**: `AgentTemplateProcessor` extracts YAML frontmatter from the agent's `.md` file
2. **Default Application**: Any missing parameters are filled from `config.yaml` `model_settings`
3. **AgentConfig Creation**: Parameters are validated and stored in an `AgentConfig` object
4. **Pydantic AI Integration**: Parameters are passed to `ModelSettings` and the `Agent` constructor

### ModelSettings Creation:

```python
# In run_agent_async()
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

### Troubleshooting Parameter Issues:

- **Agent not using expected model**: Check YAML frontmatter syntax and ensure `model` field is correctly specified
- **Unexpected behavior**: Verify `temperature` and penalty settings in both agent file and `config.yaml`
- **Timeout errors**: Check `timeout` setting in agent configuration
- **Token limit exceeded**: Adjust `max_tokens` in agent file or global config

## Data Flow: File Passing Example

1.  **CLI Call**: `./oneshot writing_agent "summarize this" --files "report.md"`
2.  **`agent_runner.py`**: Parses arguments. `files` = `["report.md"]`.
3.  **`agent_template_processor.py`**:
    - Reads the content of `report.md`.
    - Loads `agents/writing_agent.md`.
    - **Extracts YAML frontmatter** containing agent-specific model parameters (temperature, model, max_tokens, etc.).
    - Renders the template, injecting the content of `report.md` into the `provided_files` variable.
4.  **`agent_runner.py` - Parameter Loading**:
    - **Applies config.yaml defaults** for any model parameters not specified in the agent's YAML frontmatter.
    - **Creates AgentConfig object** with the merged parameter set.
    - **Instantiates ModelSettings** with the final parameter configuration.
5.  **Pydantic AI Agent Creation**:
    - **Creates OpenAIModel** with the specified model name and OpenRouter configuration.
    - **Creates Agent instance** with the ModelSettings, system prompt, and available tools.
6.  **Agent Execution**:
    - Receives the fully-rendered system prompt, which now contains the text of `report.md`.
    - Receives the user's message: "summarize this".
    - **Executes the LLM call** using the configured model parameters and combined context.
7.  **Result**: The agent's response is based on the content of the file, which was provided in its initial context, and generated using the agent's specific model configuration.
