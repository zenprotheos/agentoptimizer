# FastMCP Python Server Creation Guide

A comprehensive guide for creating stdio MCP servers in Python using the FastMCP library.

## Overview

FastMCP enables rapid development of Model Context Protocol (MCP) servers by decorating Python functions as tools. The server communicates via stdio, making it compatible with AI coding agents like Cursor.

## Core Components

### 1. Server Instantiation
```python
from fastmcp import FastMCP

mcp = FastMCP("Server Name")
```
The server name should be descriptive and unique within your MCP ecosystem.

### 2. Tool Definition
Functions become MCP tools through the `@mcp.tool()` decorator:

```python
@mcp.tool()
def function_name(param1: type, param2: type) -> return_type:
    """
    Clear docstring describing the tool's purpose.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        Description of return value
    """
    # Implementation
    return result
```

**Critical requirements:**
- Type hints are mandatory for all parameters and return values
- Docstrings must clearly explain functionality, parameters, and return values
- Function names should be descriptive and follow snake_case convention

### 3. Server Execution
```python
if __name__ == "__main__":
    mcp.run()
```
This starts the stdio server when the script is executed directly.

## Implementation Patterns

### Error Handling
Return structured error information rather than raising exceptions:

```python
@mcp.tool()
def safe_operation(value: float) -> dict:
    """Handle errors gracefully."""
    if value < 0:
        return {
            "error": "Value must be non-negative",
            "result": None
        }
    
    return {
        "result": process_value(value),
        "error": None
    }
```

### Data Structures
Use dictionaries for complex return types to maintain JSON compatibility:

```python
@mcp.tool()
def structured_response(query: str) -> dict:
    """Return structured data."""
    return {
        "query": query,
        "results": [{"id": 1, "data": "example"}],
        "metadata": {"count": 1, "timestamp": "2025-01-01"}
    }
```

### Multiple Tools Per Server
Group related functionality in a single server:

```python
mcp = FastMCP("File Operations")

@mcp.tool()
def read_file(path: str) -> dict:
    """Read file contents."""
    # Implementation

@mcp.tool()
def write_file(path: str, content: str) -> dict:
    """Write content to file."""
    # Implementation

@mcp.tool()
def list_directory(path: str) -> dict:
    """List directory contents."""
    # Implementation
```

## Configuration

### MCP Server Configuration
Create or update the **local** `.cursor/mcp.json` in your project (NOT the global one at `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "server_key": {
      "command": "python3",
      "type": "stdio",
      "args": ["/absolute/path/to/your_server.py"]
    }
  }
}
```

**Configuration notes:**
- `server_key`: Unique identifier for your server
- **Use local project configuration**: Add to `.cursor/mcp.json` in your project directory
- Use absolute paths to avoid path resolution issues
- Ensure Python executable matches your environment (`python3`, `python`, or virtual environment path)
- **Path example**: `/Users/username/project/tools/local_mcp_servers/your_server.py`

### Virtual Environment Support
For servers requiring specific dependencies:

```json
{
  "mcpServers": {
    "data_processor": {
      "command": "/path/to/venv/bin/python",
      "type": "stdio",
      "args": ["/path/to/data_processor.py"]
    }
  }
}
```

## Complete Server Template

```python
#!/usr/bin/env python3

"""
[Server Name] MCP Server
[Brief description of server functionality]
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import json
import os

# Create the MCP server
mcp = FastMCP("Server Name")

@mcp.tool()
def example_tool(input_param: str, optional_param: Optional[int] = None) -> dict:
    """
    Example tool demonstrating best practices.
    
    Args:
        input_param: Primary input parameter
        optional_param: Optional parameter with default value
        
    Returns:
        Dictionary containing results and metadata
    """
    try:
        # Process input
        result = process_input(input_param, optional_param)
        
        return {
            "success": True,
            "result": result,
            "metadata": {
                "processed_at": "timestamp",
                "input_length": len(input_param)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

def process_input(param: str, optional: Optional[int]) -> str:
    """Helper function - not exposed as MCP tool."""
    # Implementation logic
    return f"Processed: {param}"

if __name__ == "__main__":
    mcp.run()
```

## Development Workflow

### 1. Planning Phase
- Define server purpose and scope
- Identify required tools and their interfaces
- Plan data structures for inputs and outputs
- Consider error scenarios and edge cases

### 2. Implementation Phase
- Create basic server structure
- Implement tools incrementally
- Test each tool independently
- Add comprehensive error handling
- Add the python file to /tools/local_mcp_servers as *_mcp.py

### 3. Set up the MCP Servers

(The Cursor Agent should do this step for the user)

1. **Use Local MCP Configuration**: Look in the project's `.cursor` folder and find `mcp.json` (NOT the global one at `~/.cursor/mcp.json`)
2. You should see mcp server config details for various mcp servers including the oneshot mcp server
3. Add the newly created mcp server to the **local** mcp.json config
4. **Important**: Use absolute paths to the server file in the project's `tools/local_mcp_servers/` directory

### 4. Switch on MCP Servers

(The human will need to do this step - please guide them through it)

**📸 Reference Screenshot**: [View MCP Settings Interface](./app/guides/images/mcp_settings.jpg)

1. Go to Cursor > Settings > Cursor Settings > Tools & Integrations
2. Toggle on the new MCP Server
3. The user should now see a green dot icon next to each server to show that they are configured and working
4. You should now see the new mcp server in your available tools.


## Common Patterns

### File System Operations
```python
@mcp.tool()
def safe_file_read(filepath: str) -> dict:
    """Read file with proper error handling."""
    if not os.path.exists(filepath):
        return {"error": "File not found", "content": None}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "size": len(content)}
    except Exception as e:
        return {"error": f"Read failed: {str(e)}", "content": None}
```

### API Integration
```python
@mcp.tool()
def api_request(endpoint: str, method: str = "GET") -> dict:
    """Make API requests with error handling."""
    try:
        # Implementation with requests or urllib
        response = make_request(endpoint, method)
        return {
            "status_code": response.status_code,
            "data": response.json(),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "data": None
        }
```

### Data Processing
```python
@mcp.tool()
def process_data_list(data: List[dict], operation: str) -> dict:
    """Process list of data with specified operation."""
    operations = {
        "count": len,
        "sum": lambda x: sum(item.get('value', 0) for item in x),
        "average": lambda x: sum(item.get('value', 0) for item in x) / len(x)
    }
    
    if operation not in operations:
        return {
            "error": f"Unknown operation: {operation}",
            "available_operations": list(operations.keys())
        }
    
    try:
        result = operations[operation](data)
        return {"result": result, "operation": operation, "input_count": len(data)}
    except Exception as e:
        return {"error": str(e), "result": None}
```

## Troubleshooting

### Common Issues

**Server Not Appearing**
- Verify absolute path in configuration
- Check Python executable path
- Ensure script has execute permissions
- Validate JSON syntax in mcp.json
- Make sure user has enabled in Toosl & Settings Cursor/Claude Code etc

**Tool Not Working**
- Confirm type hints on all parameters
- Verify docstring format
- Check for syntax errors in function
- Ensure return type matches annotation

**Import Errors**
- Use virtual environment path in configuration
- Install required dependencies in correct environment
- Handle import failures gracefully within tools

### Debugging Techniques
Add logging to your server:

```python
import logging
logging.basicConfig(level=logging.DEBUG, filename='/tmp/mcp_server.log')

@mcp.tool()
def debug_tool(input_data: str) -> dict:
    """Tool with debug logging."""
    logging.info(f"Received input: {input_data}")
    try:
        result = process_data(input_data)
        logging.info(f"Processing successful: {result}")
        return {"result": result}
    except Exception as e:
        logging.error(f"Processing failed: {str(e)}")
        return {"error": str(e)}
```

## Assigning MCP servers to agents

The user may want the mcp server available to an agent but not available to you (the Cursor agent). In that case, they can add it to the agent frontmatter - example below

```yaml
---
name: search_analyst
description: "Specialized search and analysis agent that conducts focused, deep-dive research on specific topics"
model: openai/gpt-4o-mini
temperature: 0.7
max_tokens: 8000
request_limit: 30
tools:
  - web_search
  - web_read_page
mcp:
  - arxiv
  - biorxiv
---

# ABOUT YOU

You are a specialized search analyst
```

## Seeking help

If you get stuck and need help, use the context7 mcp server to search up documentation on fastmcp to help debug issues you might be facing.