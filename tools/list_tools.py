# tools/list_tools.py
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "list_tools",
        "description": "Lists all available tools with their complete metadata including descriptions, parameters, and capabilities. This provides the complete catalog of tools that can be assigned to agents.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

def list_tools() -> str:
    """Lists all available tools with their complete metadata including descriptions, parameters, and capabilities. This provides the complete catalog of tools that can be assigned to agents."""
    
    try:
        # Get project root from tool_services
        project_root = Path(__file__).parent.parent
        tools_dir = project_root / "tools"
        tools = []
        
        if not tools_dir.exists():
            return json.dumps({"error": "Tools directory not found"}, indent=2)
        
        for tool_file in tools_dir.glob("*.py"):
            try:
                # Use tool_services read function
                content = read(str(tool_file))
                
                # Extract TOOL_METADATA using regex to find the dictionary
                metadata_match = re.search(r'TOOL_METADATA\s*=\s*({.*?})\s*(?=\n\w|\nTOOL_|\n$)', content, re.DOTALL)
                
                if metadata_match:
                    try:
                        # Safely evaluate the metadata dictionary
                        metadata_str = metadata_match.group(1)
                        metadata = ast.literal_eval(metadata_str)
                        
                        tool_info = {
                            "name": tool_file.stem,
                            "file": str(tool_file),
                            "metadata": metadata
                        }
                        
                        # Extract key info from metadata
                        if "function" in metadata:
                            func_info = metadata["function"]
                            tool_info.update({
                                "function_name": func_info.get("name", tool_file.stem),
                                "description": func_info.get("description", "No description"),
                                "parameters": func_info.get("parameters", {})
                            })
                        
                        tools.append(tool_info)
                    except (ValueError, SyntaxError) as e:
                        tools.append({
                            "name": tool_file.stem,
                            "file": str(tool_file),
                            "error": f"Invalid TOOL_METADATA format: {e}"
                        })
                else:
                    tools.append({
                        "name": tool_file.stem,
                        "file": str(tool_file),
                        "error": "No TOOL_METADATA found"
                    })
            except Exception as e:
                tools.append({
                    "name": tool_file.stem,
                    "file": str(tool_file),
                    "error": f"Failed to load tool: {e}"
                })
        
        # Save results using tool_services
        result_data = {
            "tools": tools,
            "total": len(tools)
        }
        
        saved_file = save_json(result_data, "Available tools catalog")
        
        return json.dumps({
            "success": True,
            "tools": tools,
            "total": len(tools),
            "filepath": saved_file["filepath"],
            "run_id": saved_file["run_id"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to list tools: {e}"}, indent=2) 