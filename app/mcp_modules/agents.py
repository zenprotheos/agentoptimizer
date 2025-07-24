#!/usr/bin/env python3
"""
Agent-related MCP functions
"""

import json
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any, List

def list_agents(project_root) -> str:
    """List all available agents in the core agents directory. Returns agent names and descriptions to help you choose which agent to use for a specific task.
    
    Args:
        project_root: Path to the project root directory (can be string or Path object)
        
    Returns:
        str: JSON formatted list of available agents with their descriptions
    """
    try:
        # Convert to Path object if it's a string
        if isinstance(project_root, str):
            project_root = Path(project_root)
        
        agents_dir = project_root / "agents"
        agents = []
        
        if not agents_dir.exists():
            return json.dumps({"error": "Agents directory not found"}, indent=2)
        
        for agent_file in agents_dir.glob("*.md"):
            try:
                # Simple parsing of agent file to get basic info
                content = agent_file.read_text()
                
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
        
        return json.dumps({
            "agents": agents,
            "total": len(agents)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to list agents: {e}"}, indent=2)

 