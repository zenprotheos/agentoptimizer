#!/usr/bin/env python3
"""
Meta tool for Orchestration agents
"""

import os
from pathlib import Path

def read_doc(doc_name: str, project_root: str = ".") -> str:
    """Read a documentation file from the app/docs directory
    
    Args:
        doc_name: Name of the documentation file (without .md extension)
        project_root: Root directory of the project
        
    Returns:
        str: Contents of the documentation file
        
    Raises:
        FileNotFoundError: If the documentation file doesn't exist
    """
    docs_dir = Path(project_root) / "app" / "docs"
    doc_path = docs_dir / f"{doc_name}.md"
    
    if not doc_path.exists():
        available_docs = [f.stem for f in docs_dir.glob("*.md")]
        raise FileNotFoundError(f"Documentation '{doc_name}' not found. Available docs: {', '.join(available_docs)}")
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading documentation '{doc_name}': {str(e)}")

def get_available_docs(project_root: str = ".") -> list[str]:
    """Get list of available documentation files
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        list[str]: List of available documentation file names (without .md extension)
    """
    docs_dir = Path(project_root) / "app" / "docs"
    if not docs_dir.exists():
        return []
    
    return [f.stem for f in docs_dir.glob("*.md")] 