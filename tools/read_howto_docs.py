# tools/read_howto_docs.py
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "read_howto_docs",
        "description": "Read comprehensive instructions and examples for how to perform specific tasks in this project like creating agents, tools, and more",
        "parameters": {
            "type": "object",
            "properties": {
                "guide_name": {
                    "type": "string", 
                    "description": "Name of the guide to read. Available guides: how_to_create_agents, how_to_create_tools, how_to_use_tool_services, how_oneshot_works, onboarding, how_to_setup"
                }
            },
            "required": ["guide_name"]
        }
    }
}

def read_howto_docs(guide_name: str) -> str:
    """Read comprehensive instructions and examples for how to perform specific tasks in this project like creating agents, tools, and more."""
    
    try:
        # Get project root from tool_services
        project_root = Path(__file__).parent.parent
        docs_dir = project_root / "app" / "docs"
        doc_path = docs_dir / f"{guide_name}.md"
        
        if not doc_path.exists():
            # Get available docs
            available_docs = [f.stem for f in docs_dir.glob("*.md")] if docs_dir.exists() else []
            return json.dumps({
                "error": f"Documentation '{guide_name}' not found. Available docs: {', '.join(available_docs)}",
                "available_guides": available_docs
            }, indent=2)
        
        # Use tool_services read function
        doc_content = read(str(doc_path))
        
        # Save the documentation content for reference
        saved_file = save(doc_content, f"Documentation: {guide_name}")
        
        return json.dumps({
            "success": True,
            "guide_name": guide_name,
            "content": doc_content,
            "filepath": saved_file["filepath"],
            "tokens": saved_file["frontmatter"]["tokens"],
            "run_id": saved_file["run_id"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error reading documentation '{guide_name}': {str(e)}"}, indent=2)

def get_available_docs() -> list[str]:
    """Get list of available documentation files
    
    Returns:
        list[str]: List of available documentation file names (without .md extension)
    """
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "app" / "docs"
    if not docs_dir.exists():
        return []
    
    return [f.stem for f in docs_dir.glob("*.md")] 