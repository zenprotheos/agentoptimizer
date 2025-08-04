#!/usr/bin/env python3

"""
This is the oneshot MCP Server which provides the entry point for coding agents like cursor and claude code to orchestrate specialised agents (when in `orchestrator` role) and learn how tocreate agents and tools (when in `developer` role).
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from fastmcp import FastMCP

# Add the parent directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import MCP functions from modular files
from app.oneshot_mcp_tools.list_agents import list_agents as list_agents_impl
from app.oneshot_mcp_tools.list_tools import list_tools as list_tools_impl
from app.oneshot_mcp_tools.read_howto_docs import read_doc, get_available_docs

# Create the MCP server
mcp = FastMCP(
    name="oneshot",
    instructions="You are a helpful assistant that can call agents to help you with tasks. You can call agents by name with a message. You can also list all available agents and tools. You can read howto guides for creating agents & tools"
)

# Get project root
project_root = Path(__file__).parent.parent

@mcp.tool()
def list_agents() -> str:
    """When in `Orchestrator` modese this to list the agents that you have available, to orchestrate. Returns agent names and descriptions to help you choose which agent to use for a specific task.
    
    Returns:
        str: JSON formatted list of available agents with their descriptions
    """
    return list_agents_impl(project_root)

@mcp.tool()
def read_instructions_for(guide_name: str) -> str:
    """When in `Designer` mode, use this tool to read comprehensive instructions and examples for how to perform specific tasks in this project like creating agents, tools, and more.
    
    Args:
        guide_name: Name of the guide to read. Available guides:
            - "how_oneshot_works": Technical details of how the oneshot system works
            - "how_to_create_agents": Use this guide for creating new agents
            - "how_to_create_tools": Use this guide for creating new tools
            - "how_to_use_tool_services": Guide for understanding how to use the tool_services in new tools

    
    Returns:
        str: Contents of the requested documentation guide
    """
    try:
        return read_doc(guide_name, project_root)
    except Exception as e:
        available_docs_json = get_available_docs(project_root)
        available_docs_data = json.loads(available_docs_json)
        available_names = [doc["name"] for doc in available_docs_data["docs"]]
        return f"Error reading guide '{guide_name}': {str(e)}\n\nAvailable guides: {', '.join(available_names)}"

@mcp.tool()
def list_tools() -> str:
    """When in `Designer` mode, use this to tool to list all available agent tools, with their complete metadata including descriptions, parameters, and capabilities. This provides you with a complete catalog of tools that can be assigned to agents and helps you avoid creating duplicate tools.
    
    Returns:
        str: JSON formatted list of all native tools and MCP servers with full metadata
    """
    return list_tools_impl(project_root)

@mcp.tool()
def call_agent(agent_name: str, message: str, files: str = "", urls: str = "", run_id: str = "", debug: bool = False) -> str:
    """
    When in `Orchestrator` mode, use this tool to delegate a task to a specific agent on your team. Call an agent by name, eg `web_agent` and provide an instruction via `message`. Use the `files` argument to pass the content outputs from previous steps or agent runs, to a specialist agent rather than paraphrasing or repeating that content (must be full absolute paths to the files). Use the `urls` argument to provide web-based media content (images, documents, etc.) for multimodal processing. Use the `run_id` argument to continue an existing conversation with an agent - eg to ask follow-up questions or to continue a multi-step task.

    **File Link Requirements:**
    - Your agent team generally produce artifacts in the form of files and will return those in their final response to the `call_agent` tool. Help the end user access those files by ALWAYS providing a clickable file:// links at the end of your response to the user.
    - Present file links in a clear "Generated Files" section with descriptive labels
    - This prevents users from having to search through the artifacts directory manually

    **Multimodal Support:**
    - Use `files` for local media files (images, PDFs, audio, video) and text files
    - Use `urls` for web-based media content (e.g., "https://example.com/image.jpg|https://example.com/doc.pdf")

    Use the `list_agents` tool to see what agents are available and their descriptions to help you choose the right agent for your task.
    
    Args:
        agent_name: Name of the agent (e.g., 'web_agent')
        message: Message to send to the agent
        files: Pipe-separated list of file paths (e.g. "file1.md|file2.md"). Default empty string.
        urls: Pipe-separated list of URLs for media content (e.g. "https://example.com/image.jpg|https://example.com/doc.pdf"). Default empty string.
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
        
        # Add URLs if provided
        if urls:
            cmd.extend(["--urls", urls])
        
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