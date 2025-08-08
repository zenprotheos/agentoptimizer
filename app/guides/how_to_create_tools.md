---
name: "How to Create Tools"
purpose: "Read this guide when asked to create a new tool. It provides best practices for creating tools that work well in the oneshot system."
companion_guide: "how_to_use_tool_services.md"
---

# How to Create Tools: Complete Guide for AI Coding Assistants

## Overview

This guide teaches you how to create powerful, minimal-code tools using the `app/tool_services.py` system. Before implementing any tool functionality, **always refer to the companion guide "How to Use Tool Services"** for detailed documentation on available functions and patterns.

## Quick Start

### 1. Read the Companion Guide First

**CRITICAL**: Before creating any tool, read the **"How to Use Tool Services"** guide. It documents:
- All available helper functions
- Anti-patterns to avoid
- Advanced patterns and best practices
- Template variables and built-in imports

### 2. Tool Structure Template

Every tool follows this exact structure:

```python
# tools/your_tool_name.py
from app.tool_services import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "your_tool_name",
        "description": "Clear description of what the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Description of param1"},
                "param2": {"type": "integer", "description": "Description of param2", "default": 5}
            },
            "required": ["param1"]
        }
    }
}

def your_tool_name(param1: str, param2: int = 5) -> str:
    """Tool function with clear docstring"""
    
    # Your tool logic here (typically 5-15 lines)
    
    return json.dumps({"success": True, "result": "your_result"}, indent=2)
```

## Core Principles

1. **Minimal Code**: Most tools require only 10-20 lines of actual logic
2. **Single Import**: `from app.tool_services import *` gives you everything
3. **Check Tool Services First**: Never reimplement functionality that exists in tool_services
4. **Consistent Return Format**: Always return structured JSON
5. **Run-Aware Organization**: Files are automatically organized by conversation

## Creating Your First Tool

### Step 1: Define the Metadata

```python
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "text_analyzer",
        "description": "Analyze text content with AI",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"},
                "analysis_type": {"type": "string", "description": "Type of analysis"}
            },
            "required": ["text", "analysis_type"]
        }
    }
}
```

### Step 2: Implement the Function

```python
def text_analyzer(text: str, analysis_type: str) -> str:
    """Analyze text using tool services"""
    
    # Use tool_services functions (see companion guide for full list)
    analysis = llm(f"Perform {analysis_type} analysis on: {text}")
    
    # Save results with automatic organization
    saved_file = save(analysis, f"{analysis_type} analysis results")
    
    # Return minimal response
    return json.dumps({
        "success": True,
        "analysis_type": analysis_type,
        "filepath": saved_file["filepath"],
        "tokens": saved_file["frontmatter"]["tokens"]
    }, indent=2)
```

## Key Patterns

### 1. Content Generation Pattern

For tools that generate substantial content:

```python
def research_tool(topic: str) -> str:
    """Generate comprehensive research report"""
    
    # Generate content
    research_data = llm(f"Research: {topic}")
    
    # Save to file for downstream use
    saved_file = save(research_data, f"Research: {topic}")
    
    # Return file reference, not content
    return json.dumps({
        "success": True,
        "filepath": saved_file["filepath"],
        "summary": research_data[:100] + "..."  # Brief preview only
    }, indent=2)
```

### 2. File Processing Pattern

For tools that work with files:

```python
def process_file_tool(filepath: str, operation: str) -> str:
    """Process file content"""
    
    content = read(filepath)
    result = llm(f"Perform {operation} on: {content}")
    saved = save(result, f"{operation} results")
    
    return json.dumps({
        "success": True,
        "filepath": saved["filepath"]
    })
```

### 3. Structured Data Pattern

For tools that work with JSON data:

```python
def data_processor(query: str) -> str:
    """Generate and save structured data"""
    
    # Generate structured data
    data = llm_json(f"Generate data for: {query}")
    
    # Save with metadata wrapper
    saved = save_json(data, f"Data for: {query}")
    
    return json.dumps({
        "success": True,
        "filepath": saved["filepath"]
    })
```

## Agent-to-Agent Communication

Tools can enable powerful multi-agent workflows through file passing:

### File Passing Design

```python
def workflow_tool(task: str, files: List[str] = None) -> str:
    """Tool that accepts files from other agents"""
    
    if files:
        # Process provided files
        for filepath in files:
            content = read(filepath)
            # Process content...
    
    # Generate output for next agent
    result = llm(f"Complete task: {task}")
    saved = save(result, "Task output")
    
    return json.dumps({
        "success": True,
        "output_file": saved["filepath"],
        "ready_for_next_agent": True
    })
```

### Why File Passing Matters

- **Sequential Processing**: Agent A creates files → Agent B processes them
- **Context Preservation**: Rich context sharing between specialized agents
- **Workflow Orchestration**: Complex multi-step processes across agent teams

## Best Practices

### 1. Always Check Tool Services First

Before implementing ANY functionality, check if `tool_services.py` provides it. See the companion guide for the complete function reference.

### 2. Return Minimal Responses

```python
# ✅ GOOD - Return file reference
return json.dumps({
    "success": True,
    "filepath": saved_file["filepath"],
    "summary": "Analysis completed"
})

# ❌ BAD - Return full content
return json.dumps({
    "success": True,
    "result": full_analysis_text,  # Wastes tokens!
    "filepath": saved_file["filepath"]
})
```

### 3. Use Appropriate Save Functions

- Use `save()` for text/markdown content
- Use `save_json()` for structured data
- Both include automatic metadata and organization

### 4. Include Error Handling

```python
def my_tool(param: str) -> str:
    try:
        result = llm(f"Process: {param}")
        saved = save(result, "Results")
        return json.dumps({"success": True, "filepath": saved["filepath"]})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

### 5. Design for Multi-Agent Workflows

Consider how your tool fits into larger workflows:
- Save substantial output to files
- Accept optional file parameters
- Return file paths for downstream tools


## Example tools

### Tool using tool_services module

```python
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "simple_analysis_example",
        "description": "Analyze text and save results using Pydantic AI",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"}
            },
            "required": ["text"]
        }
    }
}

def simple_analysis_example(text: str) -> str:
    """Ultra-minimal tool using Pydantic AI through tool helper"""
    
    # One line LLM call using Pydantic AI!
    analysis = llm(f"Analyze this text and provide insights: {text}")
    
    # One line save with metadata!
    result = save(analysis, "Text analysis results")
    
    return json.dumps({
        "success": True, 
        "filepath": result["filepath"],
        "tokens": result["frontmatter"]["tokens"]
    }, indent=2) 

```

### Tool showing structured output with Pydantic AI

```python
from app.tool_services import *

class Analysis(BaseModel):
    summary: str
    key_points: List[str]
    sentiment: str
    confidence: float

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "structured_example",
        "description": "Analyze text with structured output using Pydantic AI",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"}
            },
            "required": ["text"]
        }
    }
}

def structured_example(text: str) -> str:
    """Example of structured output with minimal code"""
    
    # One line structured LLM call using Pydantic AI!
    analysis = llm_structured(f"Analyze this text: {text}", Analysis)
    
    # Convert to markdown for saving
    markdown = f"""# Analysis Results

## Summary
{analysis.summary}

## Key Points
{chr(10).join(f"- {point}" for point in analysis.key_points)}

## Sentiment: {analysis.sentiment}
**Confidence:** {analysis.confidence}
"""
    
    # Save with one line
    result = save(markdown, "Structured analysis")
    
    return json.dumps({
        "success": True,
        "analysis": analysis.dict(),
        "filepath": result["filepath"],
        "tokens": result["frontmatter"]["tokens"]
    }, indent=2) 

```

### Tool showing prompt chaining with Pydantic AI

```python
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "chain_example",
        "description": "Research and write using prompt chaining with Pydantic AI",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to research and write about"}
            },
            "required": ["topic"]
        }
    }
}

def chain_example(topic: str) -> str:
    """Example of prompt chaining with minimal code"""
    
    # Define the chain of prompts
    prompts = [
        f"Create a detailed research outline for the topic: {topic}",
        "Based on the outline you just created, research each section in detail and provide comprehensive information.",
        "Using the research you've compiled, write a well-structured, engaging article."
    ]
    
    # Execute the chain with one line using Pydantic AI conversation!
    results = chain_prompts(prompts, system_prompt="You are a research assistant and writer.")
    
    # Get the final article (last result)
    article = results[-1]
    
    # Save with metadata
    result = save(article, f"Article about {topic}")
    
    return json.dumps({
        "success": True,
        "topic": topic,
        "filepath": result["filepath"],
        "tokens": result["frontmatter"]["tokens"],
        "preview": article[:200] + "...",
        "chain_steps": len(results)
    }, indent=2) 
```


## Special Cases

### WIP Document Tools

For Work-In-Progress document tools, use `add_frontmatter=False`:

```python
# Maintain clean markdown without frontmatter
saved_file = save(content, "WIP edit", filename, add_frontmatter=False)
```

### Context-Aware Tools

Tools can access conversation context:

```python
def context_tool(query: str) -> str:
    current_run_id = get_run_id()
    
    if current_run_id:
        result = llm(f"In context of run {current_run_id}: {query}")
        # Files automatically organized by run
```

## Testing Your Tools

All tools should be testable via CLI. Include a standard docstring at the top of each tool file showing how to test it:

```python
"""
Tool: text_analyzer
Description: Analyze text content with AI

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.text_analyzer import text_analyzer
result = text_analyzer('Sample text to analyze', 'sentiment')
print(result)
"
"""
```

### Standard Tool File Structure

```python
"""
Tool: your_tool_name
Description: Brief description of what the tool does

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.your_tool_name import your_tool_name
result = your_tool_name('test_param1', 'test_param2')
print(result)
"
"""

from app.tool_services import *
import json

TOOL_METADATA = {
    # ... metadata here
}

def your_tool_name(param1: str, param2: str = "default") -> str:
    """Tool function with clear docstring"""
    
    # Your tool logic here
    
    return json.dumps({"success": True, "result": "your_result"}, indent=2)

if __name__ == "__main__":
    # Direct testing
    result = your_tool_name("test input")
    print(result)
```

### Why CLI Testing Matters

1. **Immediate Validation**: Test tools without running the full system
2. **Debugging**: Isolate issues in individual tools
3. **Development Workflow**: Quick iteration during tool creation
4. **Documentation**: Shows exactly how to use the tool
5. **Agent Context**: AI agents can test tools before using them

### Testing Best Practices

1. **Use the docstring pattern** above for every tool
2. **Test with realistic data** that matches expected usage
3. **Include error cases** in your testing
4. **Verify file outputs** if your tool creates files
5. **Test from the oneshot root directory** to ensure proper imports

## Managing Dependencies

When creating tools that require new Python packages not in `requirements.txt`, follow this workflow:

### 1. Identify New Dependencies

If your tool imports packages not in the current requirements:

```python
# Example: Your tool needs a new package
import requests  # ✅ Already in requirements.txt
import pandas   # ❌ Not in requirements.txt - needs to be added
import beautifulsoup4   # ❌ Not in requirements.txt - needs to be added
```

### 2. Add to Requirements.txt

Add the new dependencies to `requirements.txt`:

```bash
# Add the package to requirements.txt
echo "pandas>=2.0.0" >> requirements.txt
echo "beautifulsoup4>=4.12.0" >> requirements.txt
```

### 3. Install Dependencies

Install the new requirements:

```bash
pip install -r requirements.txt
```

### 4. Test Your Tool

After installing dependencies, test your tool:

```python
if __name__ == "__main__":
    # Test with new dependencies
    result = your_tool_name("test input")
    print(result)
```

### 5. Document Dependencies

Consider adding a comment in your tool about why the dependency is needed:

```python
# tools/data_analysis_tool.py
import pandas as pd  # Required for data processing functionality

def data_analysis_tool(data: str) -> str:
    """Analyze data using pandas"""
    # Tool logic here...
```

### Dependency Best Practices

1. **Specify Versions**: Use `package>=version` format for stability
2. **Minimize Dependencies**: Only add what's absolutely necessary
3. **Test Installation**: Always test after adding new dependencies
4. **Document Purpose**: Comment why each new dependency is needed

## Quick Reference

| What You Need | Where to Find It |
|---------------|------------------|
| Available functions | "How to Use Tool Services" guide |
| Template variables | "How to Use Tool Services" guide |
| Anti-patterns | "How to Use Tool Services" guide |
| Advanced patterns | "How to Use Tool Services" guide |
| Tool structure | This guide |
| Best practices | Both guides |

## Checking Available MCP Servers

Before creating any new tools, you must check what tools AND MCP servers already exist so that you don't reinvent the wheel.

### How to Check Available MCP Servers

#### 1. List All Available Tools
Use the oneshot MCP tool to see all available tools including MCP server tools:

```python
# Available via mcp.oneshot.list_tools
# This shows regular, native python tools in the /tools directory
```

#### 2. Check MCP Configuration
Examine the local `.cursor/mcp.json` file to see what MCP servers are already configured:

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "python3",
      "type": "stdio", 
      "args": ["/path/to/arxiv_mcp.py"],
      "prefix": "arxiv_"
    }
    // ... other servers
  }
}
```

### Best Practices for MCP Server Discovery

1. **Check Before Creating**: Always verify if functionality already exists
2. **Understand Prefixes**: MCP servers often use prefixes (e.g., `arxiv_`) to namespace their tools

## MCP Server Creation for Agents

When a user requests that an MCP server should be created for an agent, the Cursor agent should:

1. **Read the MCP Server Guide**: Use the `mcp.oneshot.read_instructions_for` tool to read the "how_to_create_mcp_servers" guide for detailed instructions
2. **Follow MCP Patterns**: MCP servers use different patterns than regular tools - they require FastMCP framework and stdio communication
3. **Configure Properly**: MCP servers need to be added to the local `.cursor/mcp.json` configuration
4. **Enable in Cursor**: Guide the user to enable the MCP server in Cursor Settings → Tools & Integrations

**Important**: MCP server creation is distinct from regular tool creation. Always refer to the dedicated MCP server guide for proper implementation patterns.

## Summary

Creating tools is simple:
1. **Read the companion guide** to understand available functions
2. **Copy the template** structure
3. **Write 5-15 lines** of logic using tool_services
4. **Return minimal JSON** with file references
5. **Never reimplement** what tool_services provides

The companion guide "How to Use Tool Services" contains all the technical details you need. This guide focuses on the structure and patterns for creating tools that integrate seamlessly with the agent framework.