# How to Use Tool Services: AI Agent Guide

## Overview

This guide teaches AI coding agents how to leverage the `app/tool_services.py` module when creating new tools. The tool services system provides a comprehensive set of pre-built functions that handle common operations, allowing you to focus on your tool's unique logic while avoiding code duplication.

## Core Philosophy: Don't Reinvent the Wheel

**CRITICAL PRINCIPLE**: Before implementing any functionality in a tool, check if `tool_services.py` already provides it. The tool services module is designed to eliminate boilerplate code and provide consistent, tested implementations of common operations.

### What Tool Services Provides

The `tool_services.py` module offers:

1. **LLM Integration**: Complete Pydantic AI integration with automatic configuration
2. **File Operations**: Smart file handling with run-aware organization and metadata
3. **API Integration**: HTTP requests with automatic authentication
4. **Template Rendering**: Jinja2 templating with built-in variables
5. **Structured Data**: JSON handling with metadata wrappers
6. **Error Handling**: Graceful error handling with Logfire instrumentation
7. **Run Context**: Automatic conversation context and artifact organization

## Quick Start: Single Import Pattern

Always start your tools with this single import:

```python
from app.tool_services import *
```

This gives you access to all helper functions AND common imports without additional setup or configuration. No need to import `json`, `yaml`, `Path`, `re`, `ast`, `os`, `datetime`, `BaseModel`, or typing imports separately.

### Available Imports

The single import provides these commonly used modules and types:

**Standard Library:**
- `json` - JSON encoding/decoding
- `yaml` - YAML parsing  
- `re` - Regular expressions
- `ast` - Abstract syntax trees (for safe evaluation)
- `os` - Operating system interface
- `datetime` - Date and time handling
- `Path` - Modern path handling (from pathlib)

**Pydantic & Typing:**
- `BaseModel` - Pydantic base class
- `Dict`, `Any`, `List`, `Optional`, `Type` - Common type hints

## Available Functions Reference

### LLM Operations

| Function | Purpose | Example | Don't Implement Yourself |
|----------|---------|---------|--------------------------|
| `llm(prompt, **kwargs)` | Basic LLM call | `llm("Summarize this text")` | ❌ OpenAI API calls |
| `llm_json(prompt, **kwargs)` | LLM returning JSON | `llm_json("List 3 colors as JSON")` | ❌ JSON parsing from LLM |
| `llm_structured(prompt, Model, **kwargs)` | Structured Pydantic output | `llm_structured("Analyze", Analysis)` | ❌ Pydantic model handling |
| `chain_prompts(prompts, **kwargs)` | Multi-step conversation | `chain_prompts(["Step 1", "Step 2"])` | ❌ Conversation state management |

### File Operations

| Function | Purpose | Example | Don't Implement Yourself |
|----------|---------|---------|--------------------------|
| `save(content, description, filename, add_frontmatter)` | Save with/without metadata | `save(text, "Analysis results")` or `save(text, "Clean content", add_frontmatter=False)` | ❌ File writing with frontmatter |
| `save_json(content, description, filename)` | Save JSON with wrapper | `save_json(data, "API results")` | ❌ JSON file structure |
| `read(filepath)` | Read any file | `read("data.txt")` | ❌ File reading |
| `read_for_llm(filepath, options)` | Read with frontmatter handling | `read_for_llm("file.md", frontmatter_only=True)` | ❌ YAML frontmatter parsing |

### API Operations

| Function | Purpose | Example | Don't Implement Yourself |
|----------|---------|---------|--------------------------|
| `api(url, method, **kwargs)` | HTTP requests | `api("https://api.example.com")` | ❌ HTTP client setup |
| Auto-authentication | Automatic API key injection | Headers added automatically | ❌ API key management |

### Template Operations

| Function | Purpose | Example | Don't Implement Yourself |
|----------|---------|---------|--------------------------|
| `template(template_str, **context)` | Jinja2 rendering | `template("Hello {{name}}", name="AI")` | ❌ Template engine setup |
| Built-in variables | Automatic datetime/path variables | `{{ current_datetime_friendly }}` | ❌ Built-in variable generation |

### Context Operations

| Function | Purpose | Example | Don't Implement Yourself |
|----------|---------|---------|--------------------------|
| `set_run_id(run_id)` | Set conversation context | `set_run_id("a1b2c3d4")` | ❌ Run context management |
| `get_run_id()` | Get current run ID | `get_run_id()` | ❌ Context retrieval |

## Built-in Template Variables

All LLM functions automatically support these template variables in system prompts:

```python
system_prompt = """You are analyzing data at {{ current_datetime_friendly }}.
Working directory: {{ working_directory }}
Current date: {{ current_date }}

Provide analysis with timestamp context."""

result = llm(data, system_prompt=system_prompt)
```

**Available Variables:**
- `{{ current_timestamp }}` - ISO 8601 timestamp
- `{{ current_date }}` - YYYY-MM-DD format  
- `{{ current_time }}` - HH:MM:SS format
- `{{ current_datetime_friendly }}` - Human-readable format
- `{{ current_unix_timestamp }}` - Unix timestamp
- `{{ working_directory }}` - Current working directory
- `{{ user_home }}` - User's home directory
- `{{ project_root }}` - Project root directory

## Run-Aware Artifact Organization

The tool services system automatically organizes files by conversation:

### How It Works

1. **Automatic Organization**: Files are saved to `/artifacts/{run_id}/`
2. **Metadata Inclusion**: Run ID is included in file frontmatter
3. **Context Correlation**: Easy to correlate files with conversation history

### File Structure Example

```
/runs/a1b2c3d4/              # Conversation history
├── run.json                 # Complete conversation data
└── messages.json            # Message history

/artifacts/a1b2c3d4/         # Files generated during conversation  
├── analysis_report.md       # First tool output
├── summary.txt              # Second tool output
└── processed_data.json      # Third tool output
```

### Generated File Frontmatter

```yaml
---
description: Analysis report for user query
created: 2024-01-15T10:32:00Z
tokens: 450
summary: This report analyzes the provided data...
run_id: a1b2c3d4
---

[Your file content here]
```

## Anti-Patterns: What NOT to Implement

### ❌ Don't Implement These Yourself

```python
# DON'T DO THIS - tool_services provides llm()
import openai
def my_tool():
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(...)
    return response.choices[0].message.content

# DON'T DO THIS - tool_services provides save()
def my_tool():
    with open(f"output_{datetime.now()}.txt", "w") as f:
        f.write(content)
    return "File saved"

# DON'T DO THIS - tool_services provides api()
import requests
def my_tool():
    headers = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}
    response = requests.get(url, headers=headers)
    return response.json()

# DON'T DO THIS - tool_services provides template()
def my_tool():
    from jinja2 import Template
    template = Template(template_string)
    return template.render(context)
```

### ✅ Do This Instead

```python
# USE tool_services functions
def my_tool():
    result = llm("Generate analysis")
    saved_file = save(result, "Analysis results")
    api_data = api("https://api.example.com")
    rendered = template("Hello {{name}}", name="User")
    return json.dumps({"filepath": saved_file["filepath"]})
```

## Practical Examples

### Example 1: Basic Analysis Tool

```python
# tools/text_analyzer.py
from app.tool_services import *

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

def text_analyzer(text: str, analysis_type: str) -> str:
    """Analyze text using tool services - minimal code required"""
    
    # Use tool_services llm() instead of implementing OpenAI calls
    analysis = llm(f"Perform {analysis_type} analysis on: {text}")
    
    # Use tool_services save() instead of implementing file operations
    saved_file = save(analysis, f"{analysis_type} analysis results")
    
    # Return minimal response - file contains the actual content
    return json.dumps({
        "success": True,
        "analysis_type": analysis_type,
        "filepath": saved_file["filepath"],
        "tokens": saved_file["frontmatter"]["tokens"],
        "run_id": saved_file["run_id"]
    }, indent=2)
```

**Key Points:**
- Only 3 lines of actual logic
- No OpenAI API setup required
- No file handling boilerplate
- Automatic run-aware organization
- Comprehensive metadata included

### Example 2: API Integration Tool

```python
# tools/api_processor.py
from app.tool_services import *

def api_processor(api_url: str, processing_task: str) -> str:
    """Process API data - tool_services handles complexity"""
    
    # Use tool_services api() - automatic auth handling
    response = api(api_url)
    
    if response.status_code != 200:
        return json.dumps({"error": f"API failed: {response.status_code}"})
    
    # Use tool_services llm() for processing
    processed = llm(f"Process this API data: {response.json()}\nTask: {processing_task}")
    
    # Use tool_services save() for results
    saved_file = save(processed, f"API processing: {processing_task}")
    
    return json.dumps({
        "success": True,
        "api_url": api_url,
        "filepath": saved_file["filepath"],
        "status_code": response.status_code
    }, indent=2)
```

**Key Points:**
- No requests setup required
- Automatic API key injection
- No error handling boilerplate
- Integrated LLM processing

### Example 3: Structured Data Tool

```python
# tools/data_structurer.py
from app.tool_services import *

class Analysis(BaseModel):
    summary: str
    key_points: List[str]
    confidence: float

def data_structurer(data: str, structure_type: str) -> str:
    """Create structured data using tool_services"""
    
    # Use tool_services llm_structured() - no Pydantic setup needed
    structured_result = llm_structured(
        f"Structure this data as {structure_type}: {data}",
        Analysis
    )
    
    # Use tool_services save_json() for structured data
    saved_file = save_json(
        structured_result.dict(), 
        f"Structured {structure_type} data"
    )
    
    return json.dumps({
        "success": True,
        "structure_type": structure_type,
        "filepath": saved_file["filepath"],
        "confidence": structured_result.confidence
    }, indent=2)
```

**Key Points:**
- No Pydantic AI setup required
- Automatic model handling
- Structured JSON output with metadata

## Best Practices for Tool Services Usage

### 1. Always Import Everything

```python
# DO THIS
from app.tool_services import *

# NOT THIS
from app.tool_services import llm, save  # You might miss useful functions
```

### 2. Use Appropriate Save Functions

```python
# For text/markdown content
save(text_content, "Analysis report")

# For structured data
save_json(data_dict, "API results")
```

### 3. Leverage Built-in Variables

```python
# Use built-in template variables in system prompts
system_prompt = """Analyze this data at {{ current_datetime_friendly }}.
Provide insights relevant to {{ current_date }}."""

result = llm(data, system_prompt=system_prompt)
```

### 4. Return Minimal Responses

```python
# GOOD - minimal response, content is in file
return json.dumps({
    "success": True,
    "filepath": saved_file["filepath"],
    "summary": "Brief description"
})

# BAD - wastes tokens by including full content
return json.dumps({
    "success": True,
    "result": full_analysis_text,  # Don't do this!
    "filepath": saved_file["filepath"]
})
```

### 5. Handle Errors Gracefully

```python
def my_tool(param: str) -> str:
    try:
        result = llm(f"Process: {param}")
        saved_file = save(result, "Processing results")
        return json.dumps({"success": True, "filepath": saved_file["filepath"]})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

## Advanced Patterns

### Multi-Step Processing

```python
def multi_step_tool(data: str) -> str:
    """Use chain_prompts for multi-step processing"""
    
    steps = [
        f"Analyze this data: {data}",
        "Identify key insights from the analysis",
        "Generate actionable recommendations"
    ]
    
    # tool_services handles conversation state
    results = chain_prompts(steps)
    
    # Save final result
    saved_file = save(results[-1], "Multi-step analysis")
    
    return json.dumps({
        "success": True,
        "steps_completed": len(results),
        "filepath": saved_file["filepath"]
    })
```

### Template-Based Generation

```python
def template_tool(topic: str, audience: str) -> str:
    """Use tool_services template function"""
    
    # Generate content with LLM
    content = llm(f"Write about {topic} for {audience}")
    
    # Use tool_services template with built-in variables
    formatted = template("""
# {{topic}} - {{current_date}}

**Audience:** {{audience}}
**Generated:** {{current_datetime_friendly}}

{{content}}

---
*Report generated automatically*
    """, topic=topic, audience=audience, content=content)
    
    saved_file = save(formatted, f"Report: {topic}")
    
    return json.dumps({
        "success": True,
        "topic": topic,
        "filepath": saved_file["filepath"]
    })
```

## Debugging and Instrumentation

Tool services automatically provides Logfire instrumentation:

### Automatic Logging

- All function calls are automatically logged
- Error handling is built-in
- Performance metrics are captured
- No additional logging code needed

### Accessing Logs

Use the Logfire MCP tools to debug:

```python
# Check recent tool errors
mcp_logfire_arbitrary_query(
    query="SELECT * FROM records WHERE service_name = 'oneshot-tools' AND is_exception = true ORDER BY start_timestamp DESC LIMIT 10",
    age=60
)
```

## Common Mistakes to Avoid

### 1. Reimplementing Existing Functionality

```python
# ❌ DON'T DO THIS
def bad_tool():
    import openai
    import yaml
    import json
    from datetime import datetime
    
    # Reimplementing what tool_services already provides
    client = openai.OpenAI()
    response = client.chat.completions.create(...)
    
    # Manual file operations
    timestamp = datetime.now().isoformat()
    frontmatter = f"---\ncreated: {timestamp}\n---\n"
    with open("output.md", "w") as f:
        f.write(frontmatter + content)

# ✅ DO THIS INSTEAD
def good_tool():
    result = llm("Generate content")
    saved_file = save(result, "Generated content")
    return json.dumps({"filepath": saved_file["filepath"]})
```

### 2. Not Using Run Context

```python
# ❌ MISSING CONTEXT
def bad_tool():
    result = llm("Analyze data")
    # File saved without run context
    with open("analysis.txt", "w") as f:
        f.write(result)

# ✅ CONTEXT AWARE
def good_tool():
    result = llm("Analyze data")
    # Automatically organized by run
    saved_file = save(result, "Data analysis")
    return json.dumps({
        "filepath": saved_file["filepath"],
        "run_id": saved_file["run_id"]  # Educational value
    })
```

### 3. Returning Too Much Content

```python
# ❌ TOKEN WASTE
def bad_tool():
    analysis = llm("Long analysis...")
    return json.dumps({
        "result": analysis,  # Wastes tokens!
        "full_data": large_dataset  # Even worse!
    })

# ✅ EFFICIENT
def good_tool():
    analysis = llm("Long analysis...")
    saved_file = save(analysis, "Analysis results")
    return json.dumps({
        "success": True,
        "filepath": saved_file["filepath"],
        "summary": analysis[:100] + "..."  # Brief preview only
    })
```

## Summary

The `tool_services.py` module eliminates the need for boilerplate code in tools by providing:

1. **Complete LLM Integration**: No OpenAI setup required
2. **Smart File Operations**: Automatic metadata, run organization
3. **API Integration**: Built-in authentication and error handling
4. **Template System**: Jinja2 with built-in variables
5. **Context Management**: Run-aware artifact organization
6. **Error Handling**: Graceful failures with logging
7. **Instrumentation**: Automatic Logfire integration

### Key Principles for AI Agents:

1. **Always import everything**: `from app.tool_services import *`
2. **Check existing functions first**: Don't reimplement what exists
3. **Use appropriate save functions**: `save()` for text, `save_json()` for data
4. **Return minimal responses**: File paths, not full content
5. **Leverage built-in variables**: Use template variables in system prompts
6. **Trust the system**: Let tool_services handle complexity

### Special Case: WIP Document Tools

**Important Note**: WIP (Work-In-Progress) document tools should use `tool_services` functions with the `add_frontmatter=False` parameter to maintain clean markdown format while still benefiting from run-aware organization and other tool_services features.

**Correct Pattern for WIP Tools:**
```python
# ✅ DO THIS for WIP tools - use tool_services with add_frontmatter=False
content = read(str(doc_path))  # Use tool_services for reading
saved_file = save(new_content, "WIP document edit", f"{doc_name}.md", add_frontmatter=False)
audit_data = {...}
save_json(audit_data, "Audit log", "audit.json")  # Use tool_services for audit logs

# ❌ DON'T DO THIS for WIP tools  
saved_file = save(new_content, "WIP edit")  # This adds frontmatter by default
doc_path.write_text(new_content)  # This bypasses tool_services benefits
```

**Benefits of `add_frontmatter=False` approach:**
- Maintains clean WIP document structure without frontmatter
- Still gets run-aware file organization
- Still gets automatic token counting and metadata in return value
- Still gets Logfire instrumentation
- Keeps tools DRY by using tool_services consistently 