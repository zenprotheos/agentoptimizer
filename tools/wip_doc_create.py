# tools/wip_doc_create.py
# Tool for creating WIP (Work In Progress) documents

from app.tool_services import *
import uuid

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "wip_doc_create",
        "description": "Create Work-In-Progress (WIP) documents in markdown or XML format.",
        "parameters": {
            "type": "object",
            "properties": {
                "document_name": {
                    "type": "string",
                    "description": "Name for the document (e.g., 'research_plan')"
                },
                "content": {
                    "type": "string",
                    "description": "Initial content - markdown text or XML structure"
                },
                "file_extension": {
                    "type": "string",
                    "description": "File type: '.md' for markdown or '.xml' for XML",
                    "enum": [".md", ".xml"],
                    "default": ".md"
                },
                "existing_file_path": {
                    "type": "string",
                    "description": "Optional: Initialize from existing file"
                },
                "status": {
                    "type": "string",
                    "description": "Initial status",
                    "enum": ["draft", "in_progress", "review", "complete"],
                    "default": "draft"
                }
            },
            "required": ["document_name", "content"]
        }
    }
}

def wip_doc_create(document_name: str, content: str, file_extension: str = ".md",
                   existing_file_path: str = None, status: str = "draft") -> str:
    """Create a WIP document"""
    
    try:
        # Get artifacts directory
        current_run_id = get_run_id()
        if current_run_id:
            artifacts_dir = Path("artifacts") / current_run_id
        else:
            artifacts_dir = Path("artifacts") / "no_run_id"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up paths
        doc_path = artifacts_dir / f"{document_name}{file_extension}"
        audit_path = artifacts_dir / f"{document_name}.json"
        
        # Check if exists and create versioned filename if needed
        original_doc_path = doc_path
        version = 1
        while doc_path.exists():
            version += 1
            doc_path = artifacts_dir / f"{document_name}_v{version}{file_extension}"
        
        # If we created a versioned filename, update the audit path too
        if version > 1:
            audit_path = artifacts_dir / f"{document_name}_v{version}.json"
            version_message = f"Note: a document by that name already exists. I have not overwritten it but created a new version with filename: {doc_path.name}. You should probably check the existing doc as it may already have content from previous work, before proceeding with the new version."
        else:
            version_message = None
        
        # Get content from existing file if specified
        if existing_file_path:
            file_content = read(existing_file_path)
            # For XML, use as-is; for markdown, strip frontmatter
            if file_extension == ".xml":
                content = file_content
            else:
                content = strip_frontmatter(file_content)
        
        # Create document
        timestamp = datetime.now().isoformat()
        
        if file_extension == ".xml":
            # Ensure valid XML structure
            if not content.strip().startswith("<"):
                # Wrap in basic structure if just text provided
                content = f"""<document id="{document_name}" status="{status}">
  <content>
{content}
  </content>
</document>"""
        else:
            # Markdown format
            if not content.strip().startswith("#"):
                content = f"# {document_name.replace('_', ' ').title()}\n\n{content}"
            content = f"{content}\n\n*Created: {timestamp}*\n*Status: {status}*"
        
        # Save document
        saved_doc = save(content, f"WIP: {document_name}", 
                        f"{document_name}{file_extension}", add_frontmatter=False)
        
        # Create audit log
        audit_data = {
            "document_name": document_name,
            "created_at": timestamp,
            "current_status": status,
            "file_path": saved_doc["filepath"],
            "audit_log": [{
                "timestamp": timestamp,
                "action": "create",
                "status": status,
                "source": existing_file_path
            }]
        }
        
        # Use versioned filename for audit if version was created
        audit_filename = f"{document_name}.json"
        if version > 1:
            audit_filename = f"{document_name}_v{version}.json"
            
        save_json(audit_data, f"Audit: {document_name}", audit_filename)
        
        response_data = {
            "success": True,
            "document_name": document_name,
            "file_path": saved_doc["filepath"],
            "type": file_extension[1:],  # 'md' or 'xml'
            "status": status
        }
        
        if version_message:
            response_data["message"] = version_message
            
        return json.dumps(response_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to create: {str(e)}"
        }, indent=2)

# Test
if __name__ == "__main__":
    # Test markdown
    result = wip_doc_create(
        "test_doc",
        "This is test content."
    )
    print("Markdown:", result)
    
    # Test XML
    result = wip_doc_create(
        "test_xml",
        """<section id="intro" status="empty">
  <brief>Introduction section</brief>
  <content></content>
</section>""",
        file_extension=".xml"
    )
    print("\nXML:", result)