#!/usr/bin/env python3

"""
Simple Agent MCP Server
A basic MCP server that provides agent calling functionality.
"""

import subprocess
import json
from pathlib import Path
from fastmcp import FastMCP

# Import MCP functions from modular files
from mcp_modules.agents import list_agents as list_agents_impl
from mcp_modules.tools import list_tools as list_tools_impl
from mcp_modules.docs import how_to_create_agent as how_to_create_agent_impl

# Create the MCP server
mcp = FastMCP("Agent Team")

# Get project root
project_root = Path(__file__).parent

@mcp.tool()
def list_agents() -> str:
    """List all available agents in the core agents directory. Returns agent names and descriptions to help you choose which agent to use for a specific task.
    
    Returns:
        str: JSON formatted list of available agents with their descriptions
    """
    return list_agents_impl(project_root)

@mcp.tool()
def how_to_create_agents() -> str:
    """Returns comprehensive instructions and examples for creating new agents dynamically. This guide covers agent architecture, configuration requirements, tool selection, system prompt design, and best practices for agent creation.
    
    Returns:
        str: Complete agent creation guide with examples and best practices
    """
    return how_to_create_agent_impl()

@mcp.tool()
def list_tools() -> str:
    """Lists all available tools and MCP servers with their complete metadata including descriptions, parameters, and capabilities. This provides the complete catalog of tools that can be assigned to agents.
    
    Returns:
        str: JSON formatted list of all native tools and MCP servers with full metadata
    """
    return list_tools_impl(project_root)

@mcp.tool()
def call_agent(agent_name: str, message: str, debug: bool = False) -> str:
    """
    Call an agent by name with a message.
    
    Args:
        agent_name: Name of the agent (e.g., 'web_agent')
        message: Message to send to the agent
        debug: If True, returns detailed debug output including tool calls
        
    Returns:
        str: Agent response in clean markdown format (or detailed debug format if debug=True)
    """
    try:
        # Build command with appropriate flags
        cmd = [str(project_root / "agent"), agent_name, message]
        if debug:
            cmd.append("--debug")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: Agent execution failed: {result.stderr.strip()}"
            
    except Exception as e:
        return f"ERROR: Failed to call agent {agent_name}: {e}"

if __name__ == "__main__":
    mcp.run() 