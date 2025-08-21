# tools/wip_doc_read.py
# Tool for reading WIP (Work In Progress) documents

from app.tool_services import *
import xml.etree.ElementTree as ET

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "wip_doc_read",
        "description": "Read Work-In-Progress (WIP) documents. Supports reading content, listing documents, and viewing history.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'read', 'list', or 'history'",
                    "enum": ["read", "list", "history"],
                    "default": "read"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the WIP document file"
                },
                "section_id": {
                    "type": "string",
                    "description": "For XML docs: read only a specific section by ID"
                },
                "content_only": {
                    "type": "boolean",
                    "description": "For XML: return only the content without structure",
                    "default": False
                }
            },
            "required": ["action"]
        }
    }
}

def wip_doc_read(action: str, file_path: str = None, section_id: str = None, 
                 content_only: bool = False) -> str:
    """Read WIP documents"""
    
    try:
        # Get artifacts directory
        current_run_id = get_run_id()
        if current_run_id:
            artifacts_dir = Path("artifacts") / current_run_id
        else:
            artifacts_dir = Path("artifacts") / "no_run_id"
        
        if action == "read":
            if not file_path:
                return json.dumps({"error": "file_path required for read"}, indent=2)
            
            doc_path = Path(file_path)
            if not doc_path.exists():
                return json.dumps({"error": f"Document not found: {file_path}"}, indent=2)
            
            # Read document
            content = read(str(doc_path))
            
            # Handle XML documents
            if doc_path.suffix.lower() == '.xml':
                content = _process_xml_read(content, section_id, content_only)
                if content is None:
                    return json.dumps({"error": f"Section '{section_id}' not found"}, indent=2)
            
            # Get status from audit log
            document_name = doc_path.stem
            status = _get_document_status(doc_path.parent / f"{document_name}.json")
            
            return json.dumps({
                "success": True,
                "document_name": document_name,
                "file_path": str(doc_path),
                "status": status,
                "content": content,
                "section_id": section_id
            }, indent=2)
        
        elif action == "list":
            documents = []
            
            # Find all .md and .xml files
            for doc_file in artifacts_dir.glob("*.[mx][dm]l"):
                if doc_file.suffix in ['.md', '.xml']:
                    document_name = doc_file.stem
                    status = _get_document_status(artifacts_dir / f"{document_name}.json")
                    
                    documents.append({
                        "name": document_name,
                        "path": str(doc_file),
                        "type": doc_file.suffix[1:],  # 'md' or 'xml'
                        "status": status,
                        "modified": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
                    })
            
            documents.sort(key=lambda x: x["modified"], reverse=True)
            
            return json.dumps({
                "success": True,
                "documents": documents,
                "count": len(documents)
            }, indent=2)
        
        elif action == "history":
            if not file_path:
                return json.dumps({"error": "file_path required for history"}, indent=2)
            
            doc_path = Path(file_path)
            document_name = doc_path.stem
            audit_path = doc_path.parent / f"{document_name}.json"
            
            if not audit_path.exists():
                return json.dumps({"error": f"No history for '{document_name}'"}, indent=2)
            
            # Read audit log
            audit_content = read(str(audit_path))
            audit_data = json.loads(audit_content).get("data", {})
            
            # Simplify audit entries
            history = []
            for entry in audit_data.get("audit_log", []):
                history.append({
                    "timestamp": entry.get("timestamp"),
                    "action": entry.get("action", entry.get("edit_type")),
                    "target": entry.get("target", entry.get("section")),
                    "notes": entry.get("notes")
                })
            
            return json.dumps({
                "success": True,
                "document_name": document_name,
                "status": audit_data.get("current_status", "unknown"),
                "created": audit_data.get("created_at"),
                "history": history,
                "edit_count": len(history)
            }, indent=2)
        
        else:
            return json.dumps({"error": f"Invalid action: {action}"}, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Read failed: {str(e)}"}, indent=2)

def _process_xml_read(content: str, section_id: str = None, content_only: bool = False) -> str:
    """Process XML document for reading"""
    try:
        # Fix common XML encoding issues before parsing
        fixed_content = content.replace('&', '&amp;').replace('&amp;amp;', '&amp;')
        root = ET.fromstring(fixed_content)
        
        # If section_id specified, find that section
        if section_id:
            section = root.find(f".//*[@id='{section_id}']")
            if section is None:
                return None
            
            if content_only:
                # Return just the content text
                content_elem = section.find("content")
                return content_elem.text if content_elem is not None else ""
            else:
                # Return the whole section as XML
                return ET.tostring(section, encoding='unicode')
        
        # Return full document
        if content_only:
            # Extract all content texts
            contents = []
            for elem in root.findall(".//content"):
                if elem.text:
                    contents.append(elem.text)
            return "\n\n".join(contents)
        
        return content
        
    except:
        # If XML parsing fails, return as-is
        return content

def _get_document_status(audit_path: Path) -> str:
    """Get document status from audit log"""
    if audit_path.exists():
        try:
            audit_content = read(str(audit_path))
            audit_data = json.loads(audit_content).get("data", {})
            return audit_data.get("current_status", "unknown")
        except:
            pass
    return "unknown"

# Test
if __name__ == "__main__":
    # Test listing
    print("=== List Documents ===")
    result = wip_doc_read("list")
    print(result)
    
    # Test reading if documents exist
    docs = json.loads(result).get("documents", [])
    if docs:
        print("\n=== Read First Document ===")
        result = wip_doc_read("read", file_path=docs[0]["path"])
        print(result)