#!/usr/bin/env python3
"""
The core module for the oneshot agent framework. It is used to run agents and tools. Changes to this module should be done with great caution and should trigger updates to the how_agent_runner_works.md guide.
"""

import os
import sys
import yaml
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import logfire

# Add the parent directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import refactored modules
from app.mcp_config import MCPConfigManager
from app.run_persistence import RunPersistence
from app.tool_services import helper as tool_services
from app.agent_template_processor import AgentTemplateProcessor
from app.agent_validation import AgentConfigValidator
from app.agent_errors import AgentConfigError
from app.agent_config import AgentConfigManager
from app.agent_tools import AgentToolManager
from app.agent_executor import AgentExecutor

# Load environment variables from .env file
load_dotenv()


class AgentRunner:
    """Simplified agent runner that leverages Pydantic AI's built-in capabilities"""
    
    def __init__(self, agents_dir: str = "agents", tools_dir: str = "tools", config_file: str = "config.yaml", debug: bool = False):
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        self.agents_dir = project_root / agents_dir
        self.tools_dir = project_root / tools_dir
        self.config_file = project_root / config_file
        self.debug = debug
        self.config = self._load_config()
        self._setup_logfire(debug=debug)
        
        # Initialize MCP configuration manager
        self.mcp_config_manager = MCPConfigManager(project_root, self.config, debug=debug)
        if debug:
            print(f"Template engine initialized with base path: {project_root / 'snippets'}")
            print(f"Loaded global MCP config from {Path.home() / '.cursor' / 'mcp.json'}")
            print(f"Loaded local MCP config from {project_root / '.cursor' / 'mcp.json'}")
        
        # Initialize run persistence
        self.run_persistence = RunPersistence(project_root / "runs")
        
        # Initialize template processor
        template_config = self.config.get('template_engine', {})
        self.template_processor = AgentTemplateProcessor(
            project_root=project_root,
            template_config=template_config,
            tool_services=tool_services,
            debug=debug
        )
        
        # Initialize tool manager
        self.tool_manager = AgentToolManager(
            tools_dir=self.tools_dir,
            mcp_config_manager=self.mcp_config_manager,
            debug=debug
        )
        
        # Initialize validator
        available_tools = self.tool_manager.get_available_tools()
        available_mcp_servers = list(self.mcp_config_manager.get_available_servers().keys())
        self.validator = AgentConfigValidator(
            tools_dir=self.tools_dir,
            available_tools=available_tools,
            available_mcp_servers=available_mcp_servers
        )
        
        # Initialize config manager
        self.config_manager = AgentConfigManager(
            project_root=project_root,
            config=self.config,
            template_processor=self.template_processor,
            validator=self.validator,
            debug=debug
        )
        
        # Initialize executor
        self.executor = AgentExecutor(
            config=self.config,
            run_persistence=self.run_persistence,
            debug=debug
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _setup_logfire(self, debug: bool = False):
        """Setup Logfire logging"""
        logfire_config = self.config.get('logfire', {})
        
        if not logfire_config.get('enabled', True) or not os.getenv('LOGFIRE_WRITE_TOKEN'):
            return
        
        try:
            # Configure Logfire with appropriate verbosity based on debug mode
            configure_kwargs = {
                'service_name': logfire_config.get('service_name', 'ai-agent-framework'),
                'service_version': '1.0.0',
                'environment': os.getenv('ENVIRONMENT', 'development'),
            }
            
            # Only add console logging in debug mode
            if debug:
                configure_kwargs['console'] = True
            else:
                configure_kwargs['console'] = False
            
            logfire.configure(**configure_kwargs)
            
            # Enable Pydantic AI instrumentation for automatic LLM call tracking
            # But configure it to be less verbose unless debug is enabled
            if logfire_config.get('instrument_pydantic_ai', True):
                if debug:
                    logfire.instrument_pydantic_ai()
                else:
                    # Still instrument but with minimal console output
                    logfire.instrument_pydantic_ai()
            
        except Exception as e:
            if debug:
                print(f"Warning: Failed to initialize Logfire: {e}")
    

    
    async def run_agent_async(self, agent_name: str, message: str, files: List[str] = None, urls: List[str] = None, run_id: Optional[str] = None):
        """Run an agent asynchronously with optional run continuation and file context
        
        Args:
            agent_name: Name of the agent to run
            message: Message to send to the agent
            files: Optional list of file paths to provide as context to the agent
            urls: Optional list of URLs to provide as context to the agent
            run_id: Optional run ID to continue an existing conversation
        """
        
        # Handle run continuation or creation
        message_history = []
        is_new_run = run_id is None
        
        if run_id is None:
            # Generate new run ID
            run_id = self.run_persistence.generate_run_id()
        else:
            # Load existing run history
            if self.run_persistence.run_exists(run_id):
                message_history = self.run_persistence.get_message_history(run_id)
            else:
                return {
                    "output": "",
                    "success": False,
                    "error": f"Run {run_id} not found"
                }
        
        # Load agent configuration
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            return {
                "output": "",
                "success": False,
                "error": f"Agent {agent_name} not found at {agent_file}"
            }
        
        # Parse agent configuration using the config manager
        try:
            config = await self.config_manager.parse_agent_config(agent_file, files)
        except AgentConfigError as e:
            return {
                "output": "",
                "success": False,
                "error": f"Agent Configuration Error: {e.get_formatted_message()}",
                "error_type": "configuration",
                "agent_file": str(agent_file)
            }
        except Exception as e:
            return {
                "output": "",
                "success": False,
                "error": f"Unexpected error parsing agent config: {e}",
                "error_type": "unexpected",
                "agent_file": str(agent_file)
            }
        
        # Create or update run in persistence
        if is_new_run:
            self.run_persistence.create_run(run_id, agent_name, message)
        
        # Execute the agent using the executor
        return await self.executor.execute_agent(
            config=config,
            tool_manager=self.tool_manager,
            message=message,
            files=files,
            urls=urls,
            run_id=run_id,
            message_history=message_history,
            is_new_run=is_new_run
        )
    
    def run_agent(self, agent_name: str, message: str, files: List[str] = None, urls: List[str] = None, run_id: Optional[str] = None):
        """Synchronous wrapper"""
        return asyncio.run(self.run_agent_async(agent_name, message, files, urls, run_id))
    
    def run_agent_clean(self, agent_name: str, message: str, files: List[str] = None, urls: List[str] = None, run_id: Optional[str] = None) -> str:
        """Clean formatted response for MCP server"""
        result = self.run_agent(agent_name, message, files, urls, run_id)
        
        if result["success"]:
            output = result["output"]
            
            # Add run and usage stats
            usage = result["usage"]
            output += f"\n\n---\n"
            output += f"**Run ID:** `{result['run_id']}`"
            if result.get("is_new_run"):
                output += " (new conversation)"
            else:
                output += " (continued conversation)"
            output += f"\n**Usage:** {usage['requests']} requests"
            if usage["total_tokens"]:
                output += f", {usage['total_tokens']:,} tokens"
            if result["tool_calls_summary"]:
                output += f"\n**Tools used:** {', '.join(result['tool_calls_summary'])}"
            
            return output
        else:
            error_output = f"ERROR: {result['error']}"
            if result.get("run_id"):
                error_output += f"\n**Run ID:** `{result['run_id']}`"
            return error_output


def main():
    """CLI interface"""
    if len(sys.argv) < 3:
        print("Usage: python agent_runner.py <agent_name> <message> [--files <file1|file2|...>] [--urls <url1|url2|...>] [--run-id <run_id>] [--json] [--debug]")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    message = sys.argv[2]
    
    # Parse optional arguments
    args = sys.argv[3:]
    json_output = "--json" in args
    debug_output = "--debug" in args
    
    # Parse files if provided
    files = None
    if "--files" in args:
        try:
            files_index = args.index("--files")
            if files_index + 1 < len(args):
                files_str = args[files_index + 1]
                files = [f.strip() for f in files_str.split('|') if f.strip()]
            else:
                print("ERROR: --files requires a pipe-separated list of file paths")
                sys.exit(1)
        except ValueError:
            pass
    
    # Parse URLs if provided
    urls = None
    if "--urls" in args:
        try:
            urls_index = args.index("--urls")
            if urls_index + 1 < len(args):
                urls_str = args[urls_index + 1]
                urls = [u.strip() for u in urls_str.split('|') if u.strip()]
            else:
                print("ERROR: --urls requires a pipe-separated list of URLs")
                sys.exit(1)
        except ValueError:
            pass
    
    # Parse run_id if provided
    run_id = None
    if "--run-id" in args:
        try:
            run_id_index = args.index("--run-id")
            if run_id_index + 1 < len(args):
                run_id = args[run_id_index + 1]
            else:
                print("ERROR: --run-id requires a value")
                sys.exit(1)
        except ValueError:
            pass
    
    runner = AgentRunner(debug=debug_output)
    
    if json_output:
        result = runner.run_agent(agent_name, message, files, urls, run_id)
        print(json.dumps(result, indent=2))
    else:
        result = runner.run_agent_clean(agent_name, message, files, urls, run_id)
        print(result)


if __name__ == "__main__":
    main()