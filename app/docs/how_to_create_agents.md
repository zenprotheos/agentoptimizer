# Agent Creation Guide

## Agent File Structure

Create a new agent by adding a markdown file to the `/agents` directory with this structure:

```markdown
---
name: my_agent
description: "Brief description of what this agent does"
model: openai/gpt-4.1-mini    # Optional: overrides config.yaml default
temperature: 0.7             # Optional: overrides config.yaml default
max_tokens: 2048            # Optional: overrides config.yaml default
top_p: 1.0                  # Optional: nucleus sampling
presence_penalty: 0.0       # Optional: presence penalty
frequency_penalty: 0.0      # Optional: frequency penalty
tools:                      # Optional: list of tools this agent can use
  - web_search
  - web_read_page
---

# ABOUT YOU

You are a helpful assistant that...

## YOUR APPROACH

Describe how the agent should approach tasks...

## GUIDELINES

- Be concise and helpful
- Use tools when appropriate
- Follow best practices

## Built-in Template Variables

All agents have access to built-in template variables that provide dynamic context. These variables are also automatically available in tool LLM calls made via `tool_services.py`:

### Date & Time Variables
- `{{ current_timestamp }}` - ISO 8601 timestamp (e.g., "2025-01-15T14:30:00.123456")
- `{{ current_date }}` - Date in YYYY-MM-DD format (e.g., "2025-01-15")
- `{{ current_time }}` - Time in HH:MM:SS format (e.g., "14:30:00")
- `{{ current_datetime_friendly }}` - Human-readable format (e.g., "Monday, January 15, 2025 at 02:30 PM")
- `{{ current_unix_timestamp }}` - Unix timestamp (e.g., 1736950200)

### Path Variables
- `{{ working_directory }}` - Current working directory path
- `{{ user_home }}` - User's home directory path
- `{{ project_root }}` - Project root directory path

### Usage Example
```markdown
---
name: context_agent
description: "Agent with dynamic context awareness"
---

# Context-Aware Assistant

## Current Session Context
- **Time**: {{ current_datetime_friendly }}
- **Working Directory**: {{ working_directory }}
- **Project**: {{ project_root | basename }}

You have full awareness of the current context and timing...
```

### Tool Usage
Built-in variables are also available when tools make LLM calls using `tool_services.py`:

```python
from app.tool_services import llm

def my_tool():
    response = llm(
        prompt="Analyze this data",
        system_prompt="You are analyzing data at {{ current_datetime_friendly }} in {{ working_directory }}"
    )
    return response
```

## Available Tools

Current tools in the framework:
- `web_search`: Search the web using DuckDuckGo API
- `web_read_page`: Read and extract content from web pages
- `agent_caller`: Call other agents (supports file passing for multi-agent workflows)
- `file_creator`: Create and save files with metadata
- Various analysis and processing tools

## File Passing and Context Management

### Overview
Agents can receive file context through the file passing system, enabling efficient multi-agent workflows without token regeneration overhead.

### Template Integration
Include `{% include "provided_content.md" %}` in your agent's system prompt to automatically handle file content:

```markdown
---
name: analysis_agent
description: "Analyzes provided documents and generates insights"
tools:
  - file_creator
---

# ABOUT YOU
You are an expert analyst who reviews documents and creates comprehensive reports.

{% include "about_me.md" %}

## PROVIDED CONTENT
{% include "provided_content.md" %}

## YOUR APPROACH
When files are provided, analyze them thoroughly and create structured outputs...
```

### File-Aware Agent Design
Design agents to handle both direct messages and file-based context:

1. **Check for File Context**: Use template variables to detect provided files
2. **Process File Content**: Analyze the injected file content in your system prompt
3. **Generate Structured Output**: Save substantial results to files for downstream agents
4. **Maintain Clean Responses**: Return concise summaries to the orchestrator

### Multi-Agent Workflow Patterns

#### Sequential Processing
```
Research Agent → generates report.md
     ↓
Analysis Agent → receives report.md, creates analysis.md  
     ↓
Presentation Agent → receives both files, creates slides.pdf
```

#### Parallel Processing with Aggregation
```
Data Agent → processes data.csv → insights.md
Content Agent → reviews content.md → summary.md
     ↓
Report Agent → receives insights.md + summary.md → final_report.pdf
```

## Configuration Options

### Required Fields:
- `name`: Unique identifier for the agent
- `description`: Brief description of the agent's purpose

### Optional Fields:
- `model`: OpenRouter model to use (defaults to config.yaml)
- `temperature`: Creativity level (0.0-2.0)
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling parameter
- `presence_penalty`: Penalty for new topics
- `frequency_penalty`: Penalty for repetition
- `tools`: List of tool names to make available

## Best Practices

1. **Clear Purpose**: Define a specific role and purpose for your agent
2. **Appropriate Tools**: Only include tools the agent actually needs
3. **Good Prompts**: Write clear, specific system prompts
4. **File-Aware Design**: Include `{% include "provided_content.md" %}` for file handling
5. **Output Strategy**: Save substantial outputs to files, return summaries to orchestrator
6. **Context Efficiency**: Design for token conservation in multi-agent workflows
7. **Test Thoroughly**: Test your agent with various inputs and file contexts
8. **Document Well**: Include good descriptions and examples

## Example Agents

### Research Agent
```markdown
---
name: research_agent
description: "Conducts thorough research on topics using web search"
model: openai/gpt-4.1-mini
temperature: 0.3
tools:
  - web_search
  - web_read_page
---

# ABOUT YOU
You are a thorough research assistant...
```

### Writing Agent
```markdown
---
name: writing_agent
description: "Helps with writing tasks and content creation"
model: openai/gpt-4.1-mini
temperature: 0.8
max_tokens: 4096
---

# ABOUT YOU
You are a skilled writing assistant...
``` 