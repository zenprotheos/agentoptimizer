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

from app.tool_services import ai

# Tool metadata for the agent system
TOOL_METADATA = {
    "name": "file_creator",
    "description": "Create and save files with content, automatically organized by conversation run",
    "parameters": {
        "content": "The content to save in the file",
        "description": "A description of what the file contains", 
        "filename": "Optional specific filename (if not provided, auto-generated)"
    }
}

def file_creator(content: str, description: str = "Generated file", filename: str = None) -> str:
    """
    Create and save a file with the given content.
    
    Files are automatically organized by run ID in /artifacts/{run_id}/ directories.
    
    Args:
        content: The content to save in the file
        description: A description of what the file contains
        filename: Optional specific filename (if not provided, auto-generated)
    
    Returns:
        str: Information about the saved file including filepath and run organization
    """
    try:
        # Use the ai.save function which now organizes by run ID
        result = ai.save(content, description, filename)
        
        # Format a nice response
        response = f"""✅ **File Created Successfully**

**File Details:**
- **Filepath:** `{result['filepath']}`
- **Run ID:** `{result['run_id'] or 'No run ID set'}`
- **Artifacts Directory:** `{result['artifacts_dir']}`
- **Description:** {description}
- **Tokens:** {result['frontmatter']['tokens']}
- **Created:** {result['frontmatter']['created']}

**Content Preview:**
```
{content[:200]}{'...' if len(content) > 200 else ''}
```

The file has been saved to the run-specific artifacts directory for easy organization and educational inspection."""
        
        return response
        
    except Exception as e:
        return f"❌ **Error creating file:** {str(e)}" 