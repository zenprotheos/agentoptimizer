#!/usr/bin/env python3
"""
Documentation-related MCP functions
"""

def how_to_create_agent() -> str:
    """Returns comprehensive instructions and examples for creating new agents dynamically. This guide covers agent architecture, configuration requirements, tool selection, system prompt design, and best practices for agent creation.
    
    Returns:
        str: Complete agent creation guide with examples and best practices
    """
    guide = """
# Agent Creation Guide

## Agent File Structure

Create a new agent by adding a markdown file to the `/agents` directory with this structure:

```markdown
---
name: my_agent
description: "Brief description of what this agent does"
model: openai/gpt-4o-mini    # Optional: overrides config.yaml default
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
```

## Available Tools

Current tools in the framework:
- `web_search`: Search the web using DuckDuckGo API
- `web_read_page`: Read and extract content from web pages

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
4. **Test Thoroughly**: Test your agent with various inputs
5. **Document Well**: Include good descriptions and examples

## Example Agents

### Research Agent
```markdown
---
name: research_agent
description: "Conducts thorough research on topics using web search"
model: openai/gpt-4o-mini
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
model: openai/gpt-4o
temperature: 0.8
max_tokens: 4096
---

# ABOUT YOU
You are a skilled writing assistant...
```
"""
    return guide 