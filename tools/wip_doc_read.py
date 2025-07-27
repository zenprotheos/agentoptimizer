# tools/wip_doc_read.py
# Tool for reading WIP (Work In Progress) documents and related operations

from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "wip_doc_read",
        "description": "Read Work-In-Progress (WIP) documents and perform read-only operations. Supports reading document content, listing all documents, viewing edit history, and finding documents. Can strip frontmatter for clean content when used in LLM prompts.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The read action to perform: 'read' to view document content, 'list' to see all WIP documents, 'history' to view edit trail, or 'find' to search for documents by name pattern.",
                    "enum": ["read", "list", "history", "find"]
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the WIP document file for 'read' and 'history' actions (e.g., 'wip_documents/research_plan.md')"
                },
                "document_name": {
                    "type": "string",
                    "description": "Document name for 'history' action when file_path is not provided"
                },
                "search_pattern": {
                    "type": "string",
                    "description": "Search pattern for 'find' action to match document names (supports partial matches)"
                },
                "strip_frontmatter": {
                    "type": "boolean",
                    "description": "Whether to strip YAML frontmatter and metadata from document content when reading. Useful when content will be used in LLM prompts.",
                    "default": False
                }
            },
            "required": ["action"]
        }
    }
}

def wip_doc_read(action: str, file_path: str = None, document_name: str = None, search_pattern: str = None, strip_frontmatter: bool = False) -> str:
    """Read WIP documents and perform read-only operations"""
    
    try:
        # Get run-aware artifacts directory (same as tool_services.py)
        current_run_id = get_run_id()
        if current_run_id:
            artifacts_dir = Path("artifacts") / current_run_id
        else:
            artifacts_dir = Path("artifacts") / "no_run_id"
        
        if action == "read":
            if not file_path:
                return json.dumps({
                    "error": "file_path is required for read action"
                }, indent=2)
            
            doc_path = Path(file_path)
            if not doc_path.exists():
                return json.dumps({
                    "error": f"WIP document not found at '{file_path}'"
                }, indent=2)
            
            # Use tool_services read function
            content = read(str(doc_path))
            
            # Strip frontmatter and metadata if requested
            if strip_frontmatter:
                content = _strip_frontmatter_and_metadata(content)
            
            # Get document info from audit log if available
            document_name = doc_path.stem
            audit_path = doc_path.parent / f"{document_name}.json"
            status = "unknown"
            
            if audit_path.exists():
                # Use tool_services read function
                audit_content = read(str(audit_path))
                audit_wrapper = json.loads(audit_content)
                # Extract data from tool_services JSON wrapper
                audit_data = audit_wrapper.get("data", audit_wrapper)
                status = audit_data.get("current_status", "unknown")
            
            return json.dumps({
                "success": True,
                "document_name": document_name,
                "file_path": str(doc_path),
                "status": status,
                "content": content,
                "frontmatter_stripped": strip_frontmatter,
                "summary": f"Successfully read WIP document '{document_name}'"
            }, indent=2)
        
        elif action == "list":
            if not artifacts_dir.exists():
                return json.dumps({
                    "success": True,
                    "documents": [],
                    "count": 0,
                    "summary": "No WIP documents directory found"
                }, indent=2)
            
            documents = []
            for md_file in artifacts_dir.glob("*.md"):
                document_name = md_file.stem
                audit_path = artifacts_dir / f"{document_name}.json"
                
                doc_info = {
                    "document_name": document_name,
                    "file_path": str(md_file),
                    "status": "unknown",
                    "created_at": None,
                    "last_modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                }
                
                # Get additional info from audit log
                if audit_path.exists():
                    try:
                        # Use tool_services read function
                        audit_content = read(str(audit_path))
                        audit_wrapper = json.loads(audit_content)
                        # Extract data from tool_services JSON wrapper
                        audit_data = audit_wrapper.get("data", audit_wrapper)
                        doc_info["status"] = audit_data.get("current_status", "unknown")
                        doc_info["created_at"] = audit_data.get("created_at")
                        doc_info["title"] = audit_data.get("title", document_name)
                    except:
                        pass
                
                documents.append(doc_info)
            
            # Sort by creation date or last modified
            documents.sort(key=lambda x: x.get("created_at") or x["last_modified"], reverse=True)
            
            return json.dumps({
                "success": True,
                "documents": documents,
                "count": len(documents),
                "summary": f"Found {len(documents)} WIP documents"
            }, indent=2)
        
        elif action == "history":
            if file_path:
                doc_path = Path(file_path)
                document_name = doc_path.stem
            elif document_name:
                doc_path = artifacts_dir / f"{document_name}.md"
            else:
                return json.dumps({
                    "error": "Either file_path or document_name is required for history action"
                }, indent=2)
            
            audit_path = doc_path.parent / f"{document_name}.json"
            
            if not audit_path.exists():
                return json.dumps({
                    "error": f"No audit log found for document '{document_name}'"
                }, indent=2)
            
            # Use tool_services read function
            audit_content = read(str(audit_path))
            audit_wrapper = json.loads(audit_content)
            # Extract data from tool_services JSON wrapper
            audit_data = audit_wrapper.get("data", audit_wrapper)
            
            return json.dumps({
                "success": True,
                "document_name": document_name,
                "title": audit_data.get("title", document_name),
                "current_status": audit_data.get("current_status", "unknown"),
                "created_at": audit_data.get("created_at"),
                "audit_log": audit_data.get("audit_log", []),
                "total_edits": len(audit_data.get("audit_log", [])),
                "summary": f"Retrieved edit history for '{document_name}'"
            }, indent=2)
        
        elif action == "find":
            if not search_pattern:
                return json.dumps({
                    "error": "search_pattern is required for find action"
                }, indent=2)
            
            if not artifacts_dir.exists():
                return json.dumps({
                    "success": True,
                    "matches": [],
                    "count": 0,
                    "summary": "No WIP documents directory found"
                }, indent=2)
            
            matches = []
            pattern_lower = search_pattern.lower()
            
            for md_file in artifacts_dir.glob("*.md"):
                document_name = md_file.stem
                
                # Check if pattern matches document name
                if pattern_lower in document_name.lower():
                    audit_path = artifacts_dir / f"{document_name}.json"
                    
                    match_info = {
                        "document_name": document_name,
                        "file_path": str(md_file),
                        "status": "unknown",
                        "created_at": None
                    }
                    
                    # Get additional info from audit log
                    if audit_path.exists():
                        try:
                            # Use tool_services read function
                            audit_content = read(str(audit_path))
                            audit_wrapper = json.loads(audit_content)
                            # Extract data from tool_services JSON wrapper
                            audit_data = audit_wrapper.get("data", audit_wrapper)
                            match_info["status"] = audit_data.get("current_status", "unknown")
                            match_info["created_at"] = audit_data.get("created_at")
                            match_info["title"] = audit_data.get("title", document_name)
                        except:
                            pass
                    
                    matches.append(match_info)
            
            return json.dumps({
                "success": True,
                "search_pattern": search_pattern,
                "matches": matches,
                "count": len(matches),
                "summary": f"Found {len(matches)} documents matching '{search_pattern}'"
            }, indent=2)
        
        else:
            return json.dumps({
                "error": f"Invalid action: {action}. Use 'read', 'list', 'history', or 'find'"
            }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to perform {action} operation: {str(e)}"
        }, indent=2)


def _strip_frontmatter_and_metadata(content: str) -> str:
    """Strip YAML frontmatter and document metadata from content"""
    lines = content.split('\n')
    
    # Strip YAML frontmatter if present
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                lines = lines[i+1:]
                break
    
    # Skip empty lines at the beginning
    while lines and not lines[0].strip():
        lines.pop(0)
    
    # Skip the title line (first # heading)
    if lines and lines[0].strip().startswith('#'):
        lines.pop(0)
    
    # Skip metadata lines (Created:, Status:, etc.)
    while lines and lines[0].strip().startswith('*') and (':' in lines[0]):
        lines.pop(0)
    
    # Skip empty lines after metadata
    while lines and not lines[0].strip():
        lines.pop(0)
    
    return '\n'.join(lines)


# Test the tool if run directly
if __name__ == "__main__":
    # Test listing documents
    result1 = wip_doc_read("list")
    print("Test Result 1 (list):")
    print(result1)
    
    # Test reading a document if any exist
    import json as json_lib
    list_result = json_lib.loads(result1)
    if list_result.get("success") and list_result.get("documents"):
        first_doc = list_result["documents"][0]
        result2 = wip_doc_read("read", file_path=first_doc["file_path"], strip_frontmatter=True)
        print(f"\nTest Result 2 (read with frontmatter stripped):")
        print(result2) 