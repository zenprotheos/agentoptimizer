# tools/read_file_metadata.py
# Tool to read metadata from markdown or JSON files in the artifacts directory

from app.tool_services import *
import json
import yaml
from pathlib import Path

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "read_file_metadata",
        "description": "Use this tool to read metadata from markdown or JSON files in the artifacts directory. Metadata includes file description and token count which helps you understand whether you should read the full file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file in the artifacts directory (e.g., 'ec3aa3b5/20250725_083525_results.md' or '1910ea06/20250725_084543_results.json')"
                }
            },
            "required": ["filepath"]
        }
    }
}

def read_file_metadata(filepath: str) -> str:
    """Read metadata from markdown or JSON files in the artifacts directory"""
    
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
        
        # Determine file type and extract metadata
        if full_path.suffix.lower() == '.json':
            # JSON file - extract metadata from the metadata object
            try:
                json_data = json.loads(content)
                if 'metadata' in json_data:
                    metadata = json_data['metadata']
                    return json.dumps({
                        "success": True,
                        "filepath": str(full_path),
                        "file_type": "json",
                        "metadata": metadata
                    }, indent=2)
                else:
                    return json.dumps({
                        "error": "No metadata found in JSON file",
                        "filepath": str(full_path)
                    }, indent=2)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "error": f"Invalid JSON file: {str(e)}",
                    "filepath": str(full_path)
                }, indent=2)
        
        elif full_path.suffix.lower() == '.md':
            # Markdown file - extract YAML frontmatter
            try:
                # Split content by frontmatter delimiter
                parts = content.split('---')
                if len(parts) >= 3:
                    # Extract frontmatter (second part)
                    frontmatter_text = parts[1].strip()
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
                        "metadata": metadata
                    }, indent=2)
                else:
                    return json.dumps({
                        "error": "No YAML frontmatter found in markdown file",
                        "filepath": str(full_path)
                    }, indent=2)
            except yaml.YAMLError as e:
                return json.dumps({
                    "error": f"Invalid YAML frontmatter: {str(e)}",
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
            "error": f"Failed to read file metadata: {str(e)}",
            "filepath": filepath
        }, indent=2) 