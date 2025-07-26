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
from app.oneshot_mcp_tools.agents import list_agents as list_agents_impl
from app.oneshot_mcp_tools.tools import list_tools as list_tools_impl
from app.oneshot_mcp_tools.read_doc import read_doc, get_available_docs

# Create the MCP server
mcp = FastMCP(
    name="oneshot",
    instructions="You are a helpful assistant that can call agents to help you with tasks. You can call agents by name with a message. You can also list all available agents and tools."
)

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
def read_instructions_for(guide_name: str) -> str:
    """Use this tool to read comprehensive instructions and examples for how to perform specific tasks in this project like creating agents, tools, and more.
    
    Args:
        guide_name: Name of the guide to read. Available guides:
            - "how_to_create_agents": Instructions for creating new agents
            - "how_to_create_tools": Instructions for creating new tools  
            - "how_oneshot_works": Technical details of how the system works
    
    Returns:
        str: Contents of the requested documentation guide
    """
    try:
        return read_doc(guide_name, project_root)
    except Exception as e:
        available_docs = get_available_docs(project_root)
        return f"Error reading guide '{guide_name}': {str(e)}\n\nAvailable guides: {', '.join(available_docs)}"

@mcp.tool()
def list_tools() -> str:
    """Lists all available tools and MCP servers with their complete metadata including descriptions, parameters, and capabilities. This provides the complete catalog of tools that can be assigned to agents.
    
    Returns:
        str: JSON formatted list of all native tools and MCP servers with full metadata
    """
    return list_tools_impl(project_root)

@mcp.tool()
def call_agent(agent_name: str, message: str, files: str = "", run_id: str = "", debug: bool = False) -> str:
    """
    Call an agent by name with a message using the `oneshot` bash script. Use this tool to delegate tasks to specialist agents. Call an agent by name, eg `web_agent` and provide an instruction via `message`. Use the `files` argument to pass the content outputs from previous steps to a specialist agent rather than paraphrasing or repeating that content (must be full absolute paths to the files). Use the `run_id` argument to continue an existing conversation with an agent - eg to ask follow-up questions or to continue a multi-step task.

    **File Link Requirements:**
    - When an agent generates or saves files, ALWAYS provide clickable file:// links at the end of your response
    - Parse the agent's response for any file paths mentioned (look for patterns like `/artifacts/`, `.md`, `.json`, etc.)
    - Convert absolute file paths to clickable file:// URLs (e.g., `file:///Users/chrisboden/Dropbox/AI/oneshot/artifacts/...`)
    - Present file links in a clear "Generated Files" section with descriptive labels
    - This prevents users from having to search through the artifacts directory manually

    Use the `list_agents` tool first to see what agents are available and their descriptions to help you choose the right agent for your task.
    
    Args:
        agent_name: Name of the agent (e.g., 'web_agent')
        message: Message to send to the agent
        files: Pipe-separated list of file paths (e.g. "file1.md|file2.md"). Default empty string.
        run_id: Optional run ID to continue an existing conversation (if None, starts new conversation)
        debug: If True, returns detailed debug output including tool calls
        
    Returns:
        str: Agent response in clean markdown format (or detailed debug format if debug=True)
    """
    try:
        # Build command with appropriate flags
        cmd = ["bash", str(project_root / "oneshot"), agent_name, message]
        
        # Add files if provided
        if files:
            cmd.extend(["--files", files])
        
        if run_id:
            cmd.extend(["--run-id", run_id])
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
            # Parse error for better formatting
            error_output = result.stderr.strip()
            
            # Check if it's a structured error from our agent runner
            if "Agent Configuration Error:" in error_output:
                return f"❌ **Configuration Error**\n\n{error_output}\n\n💡 **How to fix:**\n- Check your agent's YAML frontmatter syntax\n- Verify all tool and MCP server names are correct\n- Ensure required fields (name, description, model) are present"
            elif "Agent execution failed:" in error_output:
                return f"❌ **Execution Error**\n\n{error_output}\n\n💡 **Troubleshooting:**\n- Check if the specified model exists on OpenRouter\n- Verify your OPENROUTER_API_KEY is valid\n- Ensure all tools and MCP servers are properly configured"
            else:
                return f"❌ **Agent Error**\n\n{error_output}"
            
    except Exception as e:
        return f"ERROR: Failed to call agent {agent_name}: {e}"



if __name__ == "__main__":
    mcp.run()