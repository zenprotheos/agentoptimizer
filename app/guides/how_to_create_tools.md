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

```python
if __name__ == "__main__":
    # Test directly
    result = your_tool_name("test input")
    print(result)
```

## Quick Reference

| What You Need | Where to Find It |
|---------------|------------------|
| Available functions | "How to Use Tool Services" guide |
| Template variables | "How to Use Tool Services" guide |
| Anti-patterns | "How to Use Tool Services" guide |
| Advanced patterns | "How to Use Tool Services" guide |
| Tool structure | This guide |
| Best practices | Both guides |

## Summary

Creating tools is simple:
1. **Read the companion guide** to understand available functions
2. **Copy the template** structure
3. **Write 5-15 lines** of logic using tool_services
4. **Return minimal JSON** with file references
5. **Never reimplement** what tool_services provides

The companion guide "How to Use Tool Services" contains all the technical details you need. This guide focuses on the structure and patterns for creating tools that integrate seamlessly with the agent framework.