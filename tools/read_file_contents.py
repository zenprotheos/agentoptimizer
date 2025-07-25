# tools/read_file_contents.py
# Tool to read full content from markdown or JSON files in the artifacts directory

from app.tool_services import *
import json
from pathlib import Path

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "read_file_contents",
        "description": "Read the full content from markdown or JSON files in the artifacts directory",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file in the artifacts directory (e.g., 'ec3aa3b5/20250725_083525_results.md' or '1910ea06/20250725_084543_results.json')"
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Whether to include metadata in the response (default: true)",
                    "default": True
                }
            },
            "required": ["filepath"]
        }
    }
}

def read_file_contents(filepath: str, include_metadata: bool = True) -> str:
    """Read full content from markdown or JSON files in the artifacts directory"""
    
    try:
        # Construct full path to artifacts directory
        artifacts_dir = Path(__file__).parent.parent / "artifacts"
        full_path = artifacts_dir / filepath
        
        # Validate the path is within artifacts directory
        if not str(full_path).startswith(str(artifacts_dir)):
            return json.dumps({
                "error": "File path must be within the artifacts directory",
                "filepath": filepath
            }, indent=2)
        
        # Check if file exists
        if not full_path.exists():
            return json.dumps({
                "error": "File not found",
                "filepath": str(full_path)
            }, indent=2)
        
        # Read file content
        content = full_path.read_text()
        
        # Determine file type and extract content
        if full_path.suffix.lower() == '.json':
            # JSON file - parse and return structured content
            try:
                json_data = json.loads(content)
                
                if include_metadata:
                    return json.dumps({
                        "success": True,
                        "filepath": str(full_path),
                        "file_type": "json",
                        "metadata": json_data.get('metadata', {}),
                        "content": json_data.get('data', json_data)
                    }, indent=2)
                else:
                    # Return just the data content
                    return json.dumps({
                        "success": True,
                        "filepath": str(full_path),
                        "file_type": "json",
                        "content": json_data.get('data', json_data)
                    }, indent=2)
                    
            except json.JSONDecodeError as e:
                return json.dumps({
                    "error": f"Invalid JSON file: {str(e)}",
                    "filepath": str(full_path)
                }, indent=2)
        
        elif full_path.suffix.lower() == '.md':
            # Markdown file - extract content after frontmatter
            try:
                # Split content by frontmatter delimiter
                parts = content.split('---')
                if len(parts) >= 3:
                    # Extract frontmatter and content
                    frontmatter_text = parts[1].strip()
                    markdown_content = '---'.join(parts[2:]).strip()
                    
                    if include_metadata:
                        import yaml
                        try:
                            metadata = yaml.safe_load(frontmatter_text) or {}
                        except yaml.YAMLError:
                            # If YAML parsing fails, try to extract basic metadata manually
                            metadata = {}
                            for line in frontmatter_text.split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    key = key.strip()
                                    value = value.strip()
                                    metadata[key] = value
                        return json.dumps({
                            "success": True,
                            "filepath": str(full_path),
                            "file_type": "markdown",
                            "metadata": metadata,
                            "content": markdown_content
                        }, indent=2)
                    else:
                        return json.dumps({
                            "success": True,
                            "filepath": str(full_path),
                            "file_type": "markdown",
                            "content": markdown_content
                        }, indent=2)
                else:
                    # No frontmatter, return full content
                    return json.dumps({
                        "success": True,
                        "filepath": str(full_path),
                        "file_type": "markdown",
                        "content": content
                    }, indent=2)
                    
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to parse markdown file: {str(e)}",
                    "filepath": str(full_path)
                }, indent=2)
        
        else:
            return json.dumps({
                "error": "Unsupported file type. Only .md and .json files are supported",
                "filepath": str(full_path),
                "file_extension": full_path.suffix
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Failed to read file contents: {str(e)}",
            "filepath": filepath
        }, indent=2) 