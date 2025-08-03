#!/usr/bin/env python3
"""
Meta tool for Orchestration agents
"""

import os
import yaml
import json
from pathlib import Path

def read_doc(doc_name: str, project_root: str = ".") -> str:
    """Read a documentation file from the app/guides directory
    
    Args:
        doc_name: Name of the documentation file (without .md extension)
        project_root: Root directory of the project
        
    Returns:
        str: Contents of the documentation file
        
    Raises:
        FileNotFoundError: If the documentation file doesn't exist
    """
    docs_dir = Path(project_root) / "app" / "guides"
    doc_path = docs_dir / f"{doc_name}.md"
    
    if not doc_path.exists():
        # Get available docs with their metadata
        available_docs_json = get_available_docs(project_root)
        available_docs_data = json.loads(available_docs_json)
        available_names = [doc["name"] for doc in available_docs_data["docs"]]
        
        raise FileNotFoundError(f"Documentation '{doc_name}' not found. Available docs: {', '.join(available_names)}")
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading documentation '{doc_name}': {str(e)}")

def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content
    
    Args:
        content: Markdown content with optional YAML frontmatter
        
    Returns:
        dict: Parsed frontmatter or empty dict if no frontmatter
    """
    lines = content.split('\n')
    
    # Check if content starts with frontmatter
    if not lines or not lines[0].strip() == '---':
        return {}
    
    frontmatter_lines = []
    in_frontmatter = False
    
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                # End of frontmatter
                break
        elif in_frontmatter:
            frontmatter_lines.append(line)
    
    if not frontmatter_lines:
        return {}
    
    try:
        frontmatter_content = '\n'.join(frontmatter_lines)
        return yaml.safe_load(frontmatter_content) or {}
    except yaml.YAMLError:
        return {}

def get_available_docs(project_root: str = ".") -> str:
    """Get list of available documentation files with their frontmatter metadata
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        str: JSON string containing list of docs with their metadata
    """
    docs_dir = Path(project_root) / "app" / "guides"
    if not docs_dir.exists():
        return json.dumps({"docs": []})
    
    docs_info = []
    
    for doc_file in docs_dir.glob("*.md"):
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter = parse_frontmatter(content)
            
            doc_info = {
                "filename": doc_file.name,
                "name": doc_file.stem,
                "frontmatter": frontmatter
            }
            
            docs_info.append(doc_info)
            
        except Exception as e:
            # If we can't read a file, include basic info
            doc_info = {
                "filename": doc_file.name,
                "name": doc_file.stem,
                "frontmatter": {},
                "error": f"Could not read file: {str(e)}"
            }
            docs_info.append(doc_info)
    
    return json.dumps({"docs": docs_info}, indent=2) 