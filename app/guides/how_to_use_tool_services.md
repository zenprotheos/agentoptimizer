---
name: "How to Use Tool Services"
purpose: "Read this guide when creating new tools. to learn for how to leverage the tool_services.py module which brings seamless Pydantic AI integration and run-aware artifact organization. "
companion_guide: "how_to_create_tools.md"
---

# How to Use Tool Services: Technical Reference

## Overview

This is the complete technical reference for the `app/tool_services.py` module. It documents every function, pattern, and capability available when creating tools. For step-by-step instructions on creating tools, see the companion guide **"How to Create Tools"**.

## Core Philosophy

**CRITICAL PRINCIPLE**: Before implementing any functionality in a tool, check if `tool_services.py` already provides it. This module eliminates boilerplate code and provides consistent, tested implementations.

## Quick Start: Single Import Pattern

```python
from app.tool_services import *
```

This single import provides:

### Standard Library Modules
- `json` - JSON encoding/decoding
- `yaml` - YAML parsing
- `re` - Regular expressions
- `ast` - Abstract syntax trees (safe evaluation)
- `os` - Operating system interface
- `datetime` - Date and time handling
- `Path` - Modern path handling (from pathlib)

### Pydantic & Typing
- `BaseModel` - Pydantic base class
- `Dict`, `Any`, `List`, `Optional`, `Type` - Common type hints

## Function Reference

### LLM Operations

#### `llm(prompt, **kwargs)`
Basic LLM call with automatic Pydantic AI configuration.

```python
result = llm("Summarize this text: ...")
```

**Options:**
- `system_prompt`: Override default system prompt
- `max_tokens`: Set token limit
- `temperature`: Control randomness

#### `llm_json(prompt, **kwargs)`
LLM call that returns parsed JSON.

```python
colors = llm_json("List 3 colors as JSON array")
# Returns: ["red", "blue", "green"]
```

#### `llm_structured(prompt, Model, **kwargs)`
LLM call with Pydantic model validation.

```python
class Analysis(BaseModel):
    summary: str
    score: float

result = llm_structured("Analyze this...", Analysis)
# Returns: Analysis instance
```

#### `chain_prompts(prompts, **kwargs)`
Execute multiple prompts in sequence with context preservation.

```python
results = chain_prompts([
    "Step 1: Outline the topic",
    "Step 2: Expand each section",
    "Step 3: Write conclusion"
])
# Returns: List of results
```

### File Operations

#### `save(content, description, filename=None, add_frontmatter=True)`
Save content with automatic metadata and run-aware organization.

```python
saved = save(text, "Analysis results")
# Returns: {
#   "filepath": "/artifacts/run_id/analysis_20240115_103200.md",
#   "frontmatter": {"tokens": 450, "created": "...", ...},
#   "run_id": "a1b2c3d4",
#   "artifacts_dir": "/artifacts/a1b2c3d4"
# }
```

**Parameters:**
- `content`: Text content to save
- `description`: Human-readable description
- `filename`: Optional specific filename
- `add_frontmatter`: Include YAML metadata (default: True)

#### `save_json(content, description, filename=None)`
Save structured data with metadata wrapper.

```python
saved = save_json(data_dict, "API results")
# Creates file with structure:
# {
#   "metadata": {...},
#   "data": {your_data_here}
# }
```

#### `read(filepath)`
Read any file with automatic encoding detection.

```python
content = read("data.txt")
```

#### `read_for_llm(filepath, options=None)`
Read file with frontmatter handling options.

```python
# Read only frontmatter
meta = read_for_llm("file.md", {"frontmatter_only": True})

# Skip frontmatter
content = read_for_llm("file.md", {"skip_frontmatter": True})
```

### API Operations

#### `api(url, method="GET", **kwargs)`
HTTP requests with automatic authentication.

```python
response = api("https://api.example.com/data")
data = response.json()
```

**Features:**
- Automatic API key injection from environment
- Support for all HTTP methods
- Pass any requests kwargs (headers, json, data, etc.)

### Template Operations

#### `template(template_str, **context)`
Jinja2 templating with built-in variables.

```python
result = template("""
# {{title}} - {{current_date}}

{{content}}

Generated at {{current_datetime_friendly}}
""", title="Report", content=analysis)
```

### Context Operations

#### `set_run_id(run_id)`
Set the current conversation run ID.

```python
set_run_id("a1b2c3d4")
```

#### `get_run_id()`
Get the current conversation run ID.

```python
run_id = get_run_id()  # Returns: "a1b2c3d4" or None
```

## Built-in Template Variables

All LLM functions automatically support these variables in system prompts:

```python
system_prompt = """You are analyzing data at {{ current_datetime_friendly }}.
Working directory: {{ working_directory }}
Current date: {{ current_date }}"""

result = llm(data, system_prompt=system_prompt)
```

### Available Variables

- `{{ current_timestamp }}` - ISO 8601 timestamp
- `{{ current_date }}` - YYYY-MM-DD format
- `{{ current_time }}` - HH:MM:SS format
- `{{ current_datetime_friendly }}` - Human-readable format
- `{{ current_unix_timestamp }}` - Unix timestamp
- `{{ working_directory }}` - Current working directory
- `{{ user_home }}` - User's home directory
- `{{ project_root }}` - Project root directory

## Run-Aware Artifact Organization

### Automatic File Organization

```
/runs/a1b2c3d4/              # Conversation history
├── run.json
└── messages.json

/artifacts/a1b2c3d4/         # Generated files
├── analysis_report.md
├── summary.txt
└── processed_data.json
```

### File Metadata Structure

Files saved with `save()` include frontmatter:

```yaml
---
description: Analysis report for user query
created: 2024-01-15T10:32:00Z
tokens: 450
summary: This report analyzes...
run_id: a1b2c3d4
---

[Your content here]
```

Files saved with `save_json()` include metadata wrapper:

```json
{
  "metadata": {
    "description": "API results",
    "created": "2024-01-15T10:32:00Z",
    "tokens": 123,
    "run_id": "a1b2c3d4"
  },
  "data": {
    // Your actual data
  }
}
```

## Anti-Patterns: What NOT to Implement

### ❌ Don't Implement OpenAI Calls

```python
# DON'T DO THIS
import openai
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(...)

# DO THIS INSTEAD
result = llm("Your prompt")
```

### ❌ Don't Implement File Operations

```python
# DON'T DO THIS
with open(f"output_{datetime.now()}.txt", "w") as f:
    f.write(content)

# DO THIS INSTEAD
saved = save(content, "Description")
```

### ❌ Don't Implement HTTP Clients

```python
# DON'T DO THIS
import requests
headers = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}
response = requests.get(url, headers=headers)

# DO THIS INSTEAD
response = api(url)
```

### ❌ Don't Implement Template Engines

```python
# DON'T DO THIS
from jinja2 import Template
template = Template(template_string)
result = template.render(context)

# DO THIS INSTEAD
result = template(template_string, **context)
```

## Advanced Patterns

### Multi-Step Processing

```python
def multi_step_tool(data: str) -> str:
    steps = [
        f"Analyze: {data}",
        "Identify key insights",
        "Generate recommendations"
    ]
    
    results = chain_prompts(steps)
    saved = save(results[-1], "Multi-step analysis")
    
    return json.dumps({
        "success": True,
        "filepath": saved["filepath"]
    })
```

### Template-Based Generation

```python
def report_tool(topic: str, audience: str) -> str:
    content = llm(f"Write about {topic} for {audience}")
    
    formatted = template("""
# {{topic}} - {{current_date}}

**Audience:** {{audience}}
**Generated:** {{current_datetime_friendly}}

{{content}}
    """, topic=topic, audience=audience, content=content)
    
    saved = save(formatted, f"Report: {topic}")
    return json.dumps({"filepath": saved["filepath"]})
```

### Structured Data Processing

```python
class DataModel(BaseModel):
    items: List[str]
    summary: str
    confidence: float

def structured_tool(query: str) -> str:
    result = llm_structured(
        f"Process this query: {query}",
        DataModel
    )
    
    saved = save_json(result.dict(), "Structured data")
    return json.dumps({
        "filepath": saved["filepath"],
        "confidence": result.confidence
    })
```

## Special Cases

### WIP Document Tools

For clean markdown without frontmatter:

```python
# Save without frontmatter
saved = save(content, "WIP edit", "doc.md", add_frontmatter=False)

# Still gets run-aware organization and metadata in return value
```

### Large File Handling

```python
# Check file size before processing
file_path = Path(filepath)
if file_path.stat().st_size > 10_000_000:  # 10MB
    return json.dumps({"error": "File too large"})

content = read(filepath)
```

## Error Handling and Instrumentation

### Automatic Features

- All functions include Logfire instrumentation
- Errors are logged automatically
- Performance metrics captured
- No additional error handling needed in most cases

### Debugging with Logfire

```python
# Use Logfire MCP tools to debug
mcp_logfire_arbitrary_query(
    query="SELECT * FROM records WHERE service_name = 'oneshot-tools' AND is_exception = true",
    age=60
)
```

## Best Practices Summary

1. **Always use tool_services functions** instead of implementing your own
2. **Check this reference** before writing any functionality
3. **Use appropriate save function**: `save()` for text, `save_json()` for data
4. **Leverage built-in variables** in LLM system prompts
5. **Trust the error handling** - it's comprehensive
6. **Return minimal responses** - file paths instead of content
7. **Use type hints** for all parameters

## Common Mistakes

### Mistake 1: Reimplementing Existing Functions

```python
# ❌ WRONG
client = openai.OpenAI()
response = client.chat.completions.create(...)

# ✅ CORRECT
result = llm("Your prompt")
```

### Mistake 2: Ignoring Run Context

```python
# ❌ WRONG
with open("output.txt", "w") as f:
    f.write(content)

# ✅ CORRECT
saved = save(content, "Output")  # Automatically organized by run
```

### Mistake 3: Returning Full Content

```python
# ❌ WRONG
return json.dumps({"result": large_content})

# ✅ CORRECT
saved = save(large_content, "Results")
return json.dumps({"filepath": saved["filepath"]})
```

## Quick Lookup Table

| Need to... | Use this function |
|------------|-------------------|
| Call LLM | `llm()` |
| Get JSON from LLM | `llm_json()` |
| Get structured data | `llm_structured()` |
| Multi-step prompts | `chain_prompts()` |
| Save text/markdown | `save()` |
| Save JSON data | `save_json()` |
| Read any file | `read()` |
| Read with options | `read_for_llm()` |
| Make API calls | `api()` |
| Use templates | `template()` |
| Get run context | `get_run_id()` |

## Summary

This technical reference documents everything available in `tool_services.py`. For practical guidance on creating tools, see the companion guide **"How to Create Tools"**. Together, these guides provide complete documentation for building powerful, minimal-code tools that integrate seamlessly with the agent framework.