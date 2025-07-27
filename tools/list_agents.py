# tools/list_agents.py
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "list_agents",
        "description": "List all available agents in the core agents directory with their names, descriptions, models, and tools to help choose which agent to use for a specific task",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

def list_agents() -> str:
    """List all available agents in the core agents directory. Returns agent names and descriptions to help you choose which agent to use for a specific task."""
    
    try:
        # Get project root from tool_services
        project_root = Path(__file__).parent.parent
        agents_dir = project_root / "agents"
        agents = []
        
        if not agents_dir.exists():
            return json.dumps({"error": "Agents directory not found"}, indent=2)
        
        for agent_file in agents_dir.glob("*.md"):
            try:
                # Use tool_services read function
                content = read(str(agent_file))
                
                # Extract YAML frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 2:
                        frontmatter = yaml.safe_load(parts[1])
                        agents.append({
                            "name": frontmatter.get("name", agent_file.stem),
                            "description": frontmatter.get("description", "No description"),
                            "model": frontmatter.get("model", "default"),
                            "tools": frontmatter.get("tools", [])
                        })
                    else:
                        agents.append({
                            "name": agent_file.stem,
                            "description": "No description",
                            "model": "unknown",
                            "tools": []
                        })
                else:
                    agents.append({
                        "name": agent_file.stem,
                        "description": "No description",
                        "model": "unknown",
                        "tools": []
                    })
            except Exception as e:
                agents.append({
                    "name": agent_file.stem,
                    "description": f"Error parsing agent: {e}",
                    "model": "unknown",
                    "tools": []
                })
        
        # Save results using tool_services
        result_data = {
            "agents": agents,
            "total": len(agents)
        }
        
        saved_file = save_json(result_data, "Available agents list")
        
        return json.dumps({
            "success": True,
            "agents": agents,
            "total": len(agents),
            "filepath": saved_file["filepath"],
            "run_id": saved_file["run_id"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to list agents: {e}"}, indent=2) 