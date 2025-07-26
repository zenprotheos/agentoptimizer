# tools/wip_doc_edit.py
# Tool for editing WIP (Work In Progress) documents using filepath

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
import re

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "wip_doc_edit",
        "description": "Edit Work-In-Progress (WIP) documents using filepath. Supports manual editing operations like append, prepend, replace_section, and replace_all. All edits are tracked in the audit log.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the WIP document file to edit (e.g., 'wip_documents/research_plan.md')"
                },
                "content": {
                    "type": "string",
                    "description": "The content to add, replace, or use in the edit operation. Required for all edit operations."
                },
                "edit_type": {
                    "type": "string",
                    "description": "Type of edit to perform: 'append' to add content at the end, 'prepend' to add after the header, 'replace_section' to replace a specific section by title, or 'replace_all' to replace all content while keeping header.",
                    "enum": ["append", "prepend", "replace_section", "replace_all"],
                    "default": "append"
                },
                "section": {
                    "type": "string",
                    "description": "Section title to target when using 'replace_section' edit_type. Should match the exact heading text (without # symbols)."
                },
                "status": {
                    "type": "string",
                    "description": "Optional status update for the document workflow.",
                    "enum": ["draft", "in_progress", "review", "revision", "complete"]
                },
                "notes": {
                    "type": "string",
                    "description": "Notes about the edit being made for audit trail.",
                    "default": "Document edited"
                }
            },
            "required": ["file_path", "content"]
        }
    }
}

def wip_doc_edit(file_path: str, content: str, edit_type: str = "append", section: str = None, status: str = None, notes: str = "Document edited") -> str:
    """Edit a WIP document using filepath"""
    
    try:
        doc_path = Path(file_path)
        
        # Check if document exists
        if not doc_path.exists():
            return json.dumps({
                "error": f"WIP document not found at '{file_path}'. Use wip_doc_create to create new documents."
            }, indent=2)
        
        # Get document name from filepath for audit log
        document_name = doc_path.stem
        audit_path = doc_path.parent / f"{document_name}.json"
        
        # Read current content
        current_content = doc_path.read_text()
        
        # Perform the edit based on edit_type
        if edit_type == "append":
            new_content = current_content + "\n\n" + content
        
        elif edit_type == "prepend":
            # Add after the header (first line)
            lines = current_content.split('\n')
            header_end = 1
            # Skip metadata lines if present
            for i, line in enumerate(lines[1:], 1):
                if line.strip().startswith('*') and ('Created:' in line or 'Status:' in line):
                    header_end = i + 1
                else:
                    break
            
            new_lines = lines[:header_end] + ['', content, ''] + lines[header_end:]
            new_content = '\n'.join(new_lines)
        
        elif edit_type == "replace_section":
            if not section:
                return json.dumps({
                    "error": "Section title is required for replace_section edit_type"
                }, indent=2)
            
            new_content = _replace_section(current_content, section, content)
            if new_content == current_content:
                return json.dumps({
                    "error": f"Section '{section}' not found in document"
                }, indent=2)
        
        elif edit_type == "replace_all":
            # Keep the header but replace everything else
            lines = current_content.split('\n')
            header_end = 1
            # Skip metadata lines if present
            for i, line in enumerate(lines[1:], 1):
                if line.strip().startswith('*') and ('Created:' in line or 'Status:' in line):
                    header_end = i + 1
                else:
                    break
            
            header = '\n'.join(lines[:header_end])
            new_content = header + "\n\n" + content
        
        else:
            return json.dumps({
                "error": f"Invalid edit_type: {edit_type}"
            }, indent=2)
        
        # Update status in document if provided
        if status:
            new_content = _update_status_in_content(new_content, status)
        
        # Write updated content
        doc_path.write_text(new_content)
        
        # Update audit log
        _update_audit_log(audit_path, document_name, edit_type, section, status, notes, new_content)
        
        return json.dumps({
            "success": True,
            "document_name": document_name,
            "file_path": str(doc_path),
            "edit_type": edit_type,
            "section": section,
            "status": status,
            "notes": notes,
            "summary": f"WIP document edited successfully using {edit_type}"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to edit WIP document: {str(e)}"
        }, indent=2)


def _replace_section(content: str, section_title: str, new_content: str) -> str:
    """Replace a specific section in the document"""
    lines = content.split('\n')
    start_idx = None
    end_idx = len(lines)
    
    # Find the section
    for i, line in enumerate(lines):
        if line.strip().startswith('#') and section_title.lower() in line.lower():
            start_idx = i
            break
    
    if start_idx is None:
        return content  # Section not found
    
    # Find the end of the section (next heading of same or higher level)
    section_level = len(lines[start_idx]) - len(lines[start_idx].lstrip('#'))
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip().startswith('#'):
            current_level = len(line) - len(line.lstrip('#'))
            if current_level <= section_level:
                end_idx = i
                break
    
    # Replace the section
    new_lines = lines[:start_idx] + [f"{'#' * section_level} {section_title}", "", new_content, ""] + lines[end_idx:]
    return '\n'.join(new_lines)


def _update_status_in_content(content: str, new_status: str) -> str:
    """Update the status line in document content"""
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('*Status:'):
            lines[i] = f"*Status: {new_status}*"
            break
    return '\n'.join(lines)


def _update_audit_log(audit_path: Path, document_name: str, edit_type: str, section: str, status: str, notes: str, new_content: str):
    """Update the audit log with the edit"""
    timestamp = datetime.now().isoformat()
    
    # Load existing audit log or create new one
    if audit_path.exists():
        with open(audit_path, 'r') as f:
            audit_data = json.load(f)
    else:
        audit_data = {
            "document_name": document_name,
            "created_at": timestamp,
            "current_status": status or "draft",
            "file_path": str(audit_path.parent / f"{document_name}.md"),
            "audit_log": []
        }
    
    # Update current status if provided
    if status:
        audit_data["current_status"] = status
    
    # Add new audit entry
    audit_entry = {
        "edit_id": str(uuid.uuid4()),
        "timestamp": timestamp,
        "action": "edit",
        "edit_type": edit_type,
        "section": section,
        "status": status,
        "notes": notes,
        "content_hash": _calculate_hash(new_content)
    }
    
    audit_data["audit_log"].append(audit_entry)
    
    # Write updated audit log
    with open(audit_path, 'w') as f:
        json.dump(audit_data, f, indent=2)


def _calculate_hash(content: str) -> str:
    """Calculate hash of content for change tracking"""
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()


# Test the tool if run directly
if __name__ == "__main__":
    # Test editing (requires existing WIP document)
    test_file = "wip_documents/test_doc.md"
    if Path(test_file).exists():
        result = wip_doc_edit(test_file, "This is additional content.", edit_type="append", notes="Test edit")
        print("Test Result:")
        print(result)
    else:
        print(f"Test file {test_file} not found. Create a WIP document first to test editing.") 