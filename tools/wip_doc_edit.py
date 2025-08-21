# tools/wip_doc_edit.py
# Tool for editing WIP (Work In Progress) documents using filepath
# Supports both markdown and XML-based documents

from app.tool_services import *
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "wip_doc_edit",
        "description": """Edit Work-In-Progress (WIP) documents. 
        
For XML documents: Use 'target_id' to edit specific sections. Note that section id naming convention is lowercase with hyphens.
For markdown documents: Use 'section' to target by heading.
        
All edits are tracked in the audit log.""",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the WIP document file"
                },
                "content": {
                    "type": "string",
                    "description": "The content to add or replace"
                },
                "edit_type": {
                    "type": "string",
                    "description": "Type of edit: 'replace' (default), 'append', or 'update_status'",
                    "enum": ["replace", "append", "update_status"],
                    "default": "replace"
                },
                "target_id": {
                    "type": "string",
                    "description": "For XML: ID of the section to edit (e.g., 'key-drivers')"
                },
                "section": {
                    "type": "string",
                    "description": "For markdown: Section heading to target. Section id is lowercase with hyphens."
                },
                "status": {
                    "type": "string",
                    "description": "Update section status",
                    "enum": ["empty", "draft", "in_progress", "review", "complete"]
                },
                "notes": {
                    "type": "string",
                    "description": "Notes for audit trail",
                    "default": "Document edited"
                }
            },
            "required": ["file_path", "content"]
        }
    }
}

def wip_doc_edit(file_path: str, content: str, edit_type: str = "replace", 
                 target_id: str = None, section: str = None, status: str = None, 
                 notes: str = "Document edited") -> str:
    """Edit a WIP document"""
    
    try:
        doc_path = Path(file_path)
        
        if not doc_path.exists():
            return json.dumps({
                "error": f"Document not found at '{file_path}'"
            }, indent=2)
        
        # Read document
        current_content = read(str(doc_path))
        
        # Route based on file type
        if doc_path.suffix.lower() == '.xml':
            new_content = _edit_xml(current_content, content, edit_type, target_id, status)
        else:
            new_content = _edit_markdown(current_content, content, edit_type, section)
        
        if new_content is None:
            return json.dumps({
                "error": f"Edit failed - section not found"
            }, indent=2)
        
        # Save document
        document_name = doc_path.stem
        saved_file = save(new_content, f"WIP edit: {document_name}", 
                         f"{document_name}{doc_path.suffix}", add_frontmatter=False)
        
        # Update audit log
        _update_audit_log(doc_path.parent / f"{document_name}.json", 
                         document_name, edit_type, target_id or section, notes)
        
        return json.dumps({
            "success": True,
            "file_path": saved_file["filepath"],
            "edit_type": edit_type,
            "target": target_id or section,
            "notes": notes
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Edit failed: {str(e)}"
        }, indent=2)

def _edit_xml(content: str, new_content: str, edit_type: str, 
              target_id: str = None, status: str = None) -> str:
    """Edit XML document"""
    try:
        # Fix common XML encoding issues before parsing
        fixed_content = content.replace('&', '&amp;').replace('&amp;amp;', '&amp;')
        root = ET.fromstring(fixed_content)
        
        # Find target section
        if target_id:
            section = root.find(f".//*[@id='{target_id}']")
            if section is None:
                return None
        else:
            section = root  # Default to root
        
        if edit_type == "replace":
            # Replace content in the section
            content_elem = section.find("content")
            if content_elem is None:
                content_elem = ET.SubElement(section, "content")
            content_elem.text = new_content
            
        elif edit_type == "append":
            # Append to existing content
            content_elem = section.find("content")
            if content_elem is None:
                content_elem = ET.SubElement(section, "content")
            current = content_elem.text or ""
            content_elem.text = current + "\n\n" + new_content if current else new_content
            
        elif edit_type == "update_status":
            # Just update the status
            if status and section is not None:
                section.set("status", status)
        
        # Update section status if provided
        if status and section is not None:
            section.set("status", status)
        
        # Return pretty-printed XML
        return ET.tostring(root, encoding='unicode')
        
    except:
        return None

def _edit_markdown(content: str, new_content: str, edit_type: str, 
                  section: str = None) -> str:
    """Edit markdown document"""
    
    if edit_type == "append":
        return content + "\n\n" + new_content
        
    elif edit_type == "replace" and section:
        # Find and replace section
        lines = content.split('\n')
        start_idx = None
        end_idx = len(lines)
        
        # Find section start
        for i, line in enumerate(lines):
            if line.strip().startswith('#') and section.lower() in line.lower():
                start_idx = i
                break
        
        if start_idx is None:
            return None
        
        # Find section end
        level = len(lines[start_idx]) - len(lines[start_idx].lstrip('#'))
        for i in range(start_idx + 1, len(lines)):
            if lines[i].strip().startswith('#'):
                if len(lines[i]) - len(lines[i].lstrip('#')) <= level:
                    end_idx = i
                    break
        
        # Replace section
        new_lines = (lines[:start_idx] + 
                    [lines[start_idx], "", new_content, ""] + 
                    lines[end_idx:])
        return '\n'.join(new_lines)
    
    return content

def _update_audit_log(audit_path: Path, document_name: str, 
                     edit_type: str, target: str, notes: str):
    """Simple audit log update"""
    timestamp = datetime.now().isoformat()
    
    # Load or create audit log
    if audit_path.exists():
        audit_data = json.loads(read(str(audit_path))).get("data", {})
    else:
        audit_data = {
            "document_name": document_name,
            "created_at": timestamp,
            "audit_log": []
        }
    
    # Add entry
    audit_data["audit_log"].append({
        "timestamp": timestamp,
        "edit_type": edit_type,
        "target": target,
        "notes": notes
    })
    
    save_json(audit_data, f"Audit: {document_name}", f"{document_name}.json")

# Test
if __name__ == "__main__":
    # Test XML
    test_xml = """<research-plan>
  <section id="intro" status="empty">
    <brief>Introduction section</brief>
    <content></content>
  </section>
</research-plan>"""
    
    Path("test.xml").write_text(test_xml)
    
    result = wip_doc_edit(
        "test.xml",
        "## Introduction\n\nThis is the intro.",
        target_id="intro",
        status="complete"
    )
    print(result)
    
    Path("test.xml").unlink()
    Path("test.json").unlink(missing_ok=True)