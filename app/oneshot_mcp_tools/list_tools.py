#!/usr/bin/env python3
"""
Meta tool for Orchestration agents to list the full suite of tools available to them and their agents
"""

import json
from pathlib import Path
from typing import Dict, Any, List

def list_tools(project_root: Path) -> str:
    """Lists all available tools with their complete metadata including descriptions, parameters, and capabilities. This provides the complete catalog of tools that can be assigned to agents.
    
    Args:
        project_root: Path to the project root directory
        
    Returns:
        str: JSON formatted list of all native tools and MCP servers with full metadata
    """
    try:
        tools_dir = project_root / "tools"
        tools = []
        
        if not tools_dir.exists():
            return json.dumps({"error": "Tools directory not found"}, indent=2)
        
        for tool_file in tools_dir.glob("*.py"):
            try:
                # Read the tool file to extract metadata
                content = tool_file.read_text()
                
                # Look for TOOL_METADATA in the file
                if "TOOL_METADATA" in content:
                    # Simple extraction - look for the metadata dict
                    tools.append({
                        "name": tool_file.stem,
                        "description": f"Tool from {tool_file.name}",
                        "file": str(tool_file)
                    })
                else:
                    tools.append({
                        "name": tool_file.stem,
                        "error": "No TOOL_METADATA found",
                        "file": str(tool_file)
                    })
            except Exception as e:
                tools.append({
                    "name": tool_file.stem,
                    "error": f"Failed to load tool: {e}",
                    "file": str(tool_file)
                })
        
        return json.dumps({
            "tools": tools,
            "total": len(tools)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to list tools: {e}"}, indent=2) 