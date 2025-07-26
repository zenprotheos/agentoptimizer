# tools/wip_doc_create.py
# Tool for creating WIP (Work In Progress) documents, including from existing files

import json

# Handle imports for both standalone testing and normal tool usage
try:
    from app.tool_services import *
except ImportError:
    # For standalone testing, add parent directory to path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.tool_services import *

from pathlib import Path
from datetime import datetime
import uuid

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "wip_doc_create",
        "description": "Create Work-In-Progress (WIP) documents either from scratch or by initializing from an existing file. This tool sets up the WIP document system with audit tracking for iterative document development.",
        "parameters": {
            "type": "object",
            "properties": {
                "document_name": {
                    "type": "string",
                    "description": "Unique identifier for the document (e.g., 'project_proposal', 'research_plan'). This becomes the filename and must be unique across all WIP documents. Use lowercase with underscores for consistency."
                },
                "title": {
                    "type": "string",
                    "description": "Human-readable title for the document (e.g., 'Digital Hub Expansion Strategy 2025'). Used as the main heading and for display purposes."
                },
                "content": {
                    "type": "string",
                    "description": "Initial content for the document. If not provided when using existing_file_path, the content will be read from the existing file."
                },
                "existing_file_path": {
                    "type": "string",
                    "description": "Optional path to an existing file to initialize the WIP document from. The content will be read from this file and used as the starting point, with frontmatter stripped if present."
                },
                "status": {
                    "type": "string",
                    "description": "Initial document workflow status for lifecycle management.",
                    "enum": ["draft", "in_progress", "review", "revision", "complete"],
                    "default": "draft"
                },
                "notes": {
                    "type": "string",
                    "description": "Initial notes about the document creation or purpose.",
                    "default": "Document created"
                }
            },
            "required": ["document_name", "title"]
        }
    }
}

def wip_doc_create(document_name: str, title: str, content: str = None, existing_file_path: str = None, status: str = "draft", notes: str = "Document created") -> str:
    """Create a WIP document either from scratch or from an existing file"""
    
    try:
        # Get run-aware artifacts directory (same as tool_services.py)
        current_run_id = get_run_id()
        if current_run_id:
            artifacts_dir = Path("artifacts") / current_run_id
        else:
            artifacts_dir = Path("artifacts") / "no_run_id"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = artifacts_dir / f"{document_name}.md"
        audit_path = artifacts_dir / f"{document_name}.json"
        
        # Check if document already exists
        if doc_path.exists():
            return json.dumps({
                "error": f"WIP document '{document_name}' already exists. Use wip_doc_edit to modify existing documents."
            }, indent=2)
        
        # Get content from existing file if specified
        if existing_file_path:
            try:
                file_content = read(existing_file_path)
                # Strip frontmatter if present
                content = _strip_frontmatter(file_content)
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to read existing file '{existing_file_path}': {str(e)}"
                }, indent=2)
        elif not content:
            content = f"# {title}\n\n*Document content will be added here.*"
        
        # Create document content with header
        timestamp = datetime.now().isoformat()
        document_content = f"""# {title}

*Created: {timestamp}*
*Status: {status}*

{content}"""
        
        # Write the document
        doc_path.write_text(document_content)
        
        # Create audit log
        audit_data = {
            "document_name": document_name,
            "title": title,
            "created_at": timestamp,
            "current_status": status,
            "file_path": str(doc_path),
            "audit_log": [
                {
                    "edit_id": str(uuid.uuid4()),
                    "timestamp": timestamp,
                    "action": "create",
                    "status": status,
                    "notes": notes,
                    "source_file": existing_file_path if existing_file_path else None,
                    "content_hash": _calculate_hash(document_content)
                }
            ]
        }
        
        # Write audit log
        with open(audit_path, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        return json.dumps({
            "success": True,
            "document_name": document_name,
            "title": title,
            "file_path": str(doc_path),
            "audit_path": str(audit_path),
            "status": status,
            "source_file": existing_file_path,
            "notes": notes,
            "summary": f"WIP document '{document_name}' created successfully"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to create WIP document: {str(e)}"
        }, indent=2)


def _strip_frontmatter(content: str) -> str:
    """Strip YAML frontmatter from content if present"""
    lines = content.split('\n')
    if lines and lines[0].strip() == '---':
        # Find the end of frontmatter
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                # Return content after frontmatter, skipping empty lines
                remaining_lines = lines[i+1:]
                while remaining_lines and not remaining_lines[0].strip():
                    remaining_lines.pop(0)
                return '\n'.join(remaining_lines)
    return content


def _calculate_hash(content: str) -> str:
    """Calculate hash of content for change tracking"""
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()


# Test the tool if run directly
if __name__ == "__main__":
    # Test creating a document from scratch
    result1 = wip_doc_create("test_doc", "Test Document", "This is test content.")
    print("Test Result 1 (new document):")
    print(result1)
    
    # Test creating from existing file (if available)
    if Path("test_research_brief.md").exists():
        result2 = wip_doc_create("test_from_file", "Test From File", existing_file_path="test_research_brief.md")
        print("\nTest Result 2 (from existing file):")
        print(result2) 