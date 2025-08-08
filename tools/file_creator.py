#!/usr/bin/env python3
"""
Tool: file_creator
Description: Create and save files with content, automatically organized by conversation run

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.file_creator import file_creator
result = file_creator('Hello world!', 'Test file', 'test_file.txt')
print(result)
"
"""

from app.tool_services import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "file_creator",
        "description": "Use this tool to create and save files with content to the artifacts directory. Files include metadata like creation time, token count, and description. Perfect for saving agent outputs, research results, or any generated content.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string", 
                    "description": "The text content to save in the file. Can be plain text, markdown, JSON, or any text format."
                },
                "description": {
                    "type": "string", 
                    "description": "Human-readable description of what the file contains. This appears in the file metadata and helps with organization.",
                    "default": "Generated file"
                },
                "filename": {
                    "type": "string", 
                    "description": "Optional specific filename. If not provided, a timestamped filename will be auto-generated. Include extension if needed (e.g., 'report.md', 'data.json')."
                },
                "add_frontmatter": {
                    "type": "boolean",
                    "description": "Whether to add YAML frontmatter with metadata to the file. Defaults to False.",
                    "default": False
                }
            },
            "required": ["content"]
        }
    }
}

def file_creator(content: str, description: str = "Generated file", filename: str = None, add_frontmatter: bool = False) -> str:
    """
    Create and save a file with the given content.
    
    Files are automatically organized by run ID in /artifacts/{run_id}/ directories.
    
    Args:
        content: The content to save in the file
        description: A description of what the file contains
        filename: Optional specific filename (if not provided, auto-generated)
        add_frontmatter: Whether to add YAML frontmatter with metadata (default: False)
    
    Returns:
        str: JSON response with file details
    """
    try:
        # Use the save function which organizes by run ID
        result = save(content, description, filename, add_frontmatter)
        
        # Return minimal JSON response with file reference
        return json.dumps({
            "success": True,
            "filepath": result["filepath"],
            "run_id": result["run_id"],
            "artifacts_dir": result["artifacts_dir"],
            "description": description,
            "tokens": result["frontmatter"]["tokens"],
            "created": result["frontmatter"]["created"],
            "preview": content[:100] + "..." if len(content) > 100 else content
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2) 