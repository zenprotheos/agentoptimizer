#!/usr/bin/env python3
"""
Simplified AI Agent Framework using Pydantic AI - removes unnecessary duplications
"""

import os
import sys
import yaml
import json
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits
from dotenv import load_dotenv
import logfire
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Add the parent directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import MCP-related classes and run persistence
from app.mcp_config import MCPConfigManager, MCPServerConfig
from app.run_persistence import RunPersistence
from app.tool_services import helper as tool_services
from app.agent_template_processor import AgentTemplateProcessor
from app.agent_validation import AgentConfigValidator
from app.agent_errors import AgentConfigError

# Load environment variables from .env file
load_dotenv()


class AgentConfig:
    """Simplified agent configuration - just parse what we need"""
    def __init__(self, config_data: Dict[str, Any]):
        self.name = config_data['name']
        self.description = config_data['description']
        self.model = config_data['model']
        self.temperature = config_data.get('temperature', 0.7)
        self.max_tokens = config_data.get('max_tokens', 2048)
        self.top_p = config_data.get('top_p')
        self.presence_penalty = config_data.get('presence_penalty')
        self.frequency_penalty = config_data.get('frequency_penalty')
        self.timeout = config_data.get('timeout', 30.0)
        self.stream = config_data.get('stream', False)
        self.tools = config_data.get('tools', [])
        self.mcp = config_data.get('mcp', [])
        self.system_prompt = config_data['system_prompt']


class AgentRunner:
    """Simplified agent runner that leverages Pydantic AI's built-in capabilities"""
    
    def __init__(self, agents_dir: str = "agents", tools_dir: str = "tools", config_file: str = "config.yaml"):
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        self.agents_dir = project_root / agents_dir
        self.tools_dir = project_root / tools_dir
        self.config_file = project_root / config_file
        self.config = self._load_config()
        self.loaded_tools = {}
        self._load_tools()
        self._setup_logfire()
        
        # Initialize MCP configuration manager
        self.mcp_config_manager = MCPConfigManager(project_root, self.config)
        
        # Initialize run persistence
        self.run_persistence = RunPersistence(project_root / "runs")
        
        # Initialize template processor
        template_config = self.config.get('template_engine', {})
        self.template_processor = AgentTemplateProcessor(
            project_root=project_root,
            template_config=template_config,
            tool_services=tool_services
        )
        
        # Initialize validator
        available_tools = list(self.loaded_tools.keys())
        available_mcp_servers = list(self.mcp_config_manager.get_available_servers().keys())
        self.validator = AgentConfigValidator(
            tools_dir=self.tools_dir,
            available_tools=available_tools,
            available_mcp_servers=available_mcp_servers
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
    
    def _load_tools(self):
        """Load all tools from the tools directory"""
        if not self.tools_dir.exists():
            return
            
        for tool_file in self.tools_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(tool_file.stem, tool_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'TOOL_METADATA'):
                    tool_name = tool_file.stem
                    function_name = tool_name
                    self.loaded_tools[tool_name] = {
                        'module': module,
                        'metadata': module.TOOL_METADATA,
                        'function': getattr(module, function_name, None)
                    }
                    print(f"Loaded tool: {tool_name}")
                    
            except Exception as e:
                print(f"Error loading tool {tool_file}: {e}")
    
    def _setup_logfire(self):
        """Setup Logfire logging"""
        logfire_config = self.config.get('logfire', {})
        
        if not logfire_config.get('enabled', True) or not os.getenv('LOGFIRE_WRITE_TOKEN'):
            return
        
        try:
            logfire.configure(
                service_name=logfire_config.get('service_name', 'ai-agent-framework'),
                service_version='1.0.0',
                environment=os.getenv('ENVIRONMENT', 'development'),
            )
            
            # Enable Pydantic AI instrumentation for automatic LLM call tracking
            if logfire_config.get('instrument_pydantic_ai', True):
                logfire.instrument_pydantic_ai()
            
        except Exception as e:
            print(f"Warning: Failed to initialize Logfire: {e}")
    
    async def _parse_agent_config(self, agent_file: Path, files: List[str] = None) -> AgentConfig:
        """Parse agent configuration using template processor with comprehensive validation"""
        try:
            # Process template first (includes basic validation)
            template_result = await self.template_processor.process_agent_template(
                agent_file=agent_file,
                files=files,
                additional_context={}
            )
            
            config_data = template_result['config_data']
            
            # Then perform additional validations (tools, MCP servers, etc.)
            if "tools" in config_data:
                self.validator.validate_tools(config_data["tools"], agent_file)
            
            if "mcp" in config_data:
                self.validator.validate_mcp_servers(config_data["mcp"], agent_file)
            
            if "model" in config_data:
                self.validator.validate_model_name(config_data["model"], agent_file)
            
            # Validate numeric ranges
            self.validator.validate_numeric_ranges(config_data, agent_file)
            
            # Add system prompt
            config_data['system_prompt'] = template_result['system_prompt']
            
            # Apply defaults from config file
            model_defaults = self.config.get('model_settings', {})
            for key, default_value in model_defaults.items():
                if key not in config_data:
                    config_data[key] = default_value
            
            return AgentConfig(config_data)
        except AgentConfigError:
            # Re-raise agent config errors as-is (they have helpful messages)
            raise
        except Exception as e:
            raise AgentConfigError(f"Unexpected error processing agent template for {agent_file}: {e}", agent_file)
    
    def _create_tool_functions(self, tool_names: List[str]) -> List[Any]:
        """Create tool functions for Pydantic AI from loaded tools with enhanced error handling"""
        tool_functions = []
        errors = []
        
        for tool_name in tool_names:
            if tool_name in self.loaded_tools:
                tool_info = self.loaded_tools[tool_name]
                tool_func = tool_info['function']
                
                if tool_func:
                    tool_functions.append(tool_func)
                else:
                    errors.append(f"Tool '{tool_name}' has no main function - check tool file structure")
            else:
                available_tools = list(self.loaded_tools.keys())
                # Simple fuzzy matching for suggestions
                close_matches = [t for t in available_tools if self._is_similar_tool_name(tool_name, t)]
                
                error_msg = f"Tool '{tool_name}' not found in loaded tools."
                if close_matches:
                    error_msg += f" Did you mean: {', '.join(close_matches[:3])}?"
                error_msg += f" Available tools: {', '.join(sorted(available_tools))}"
                errors.append(error_msg)
        
        if errors:
            # Log errors but don't fail - let the agent run with available tools
            for error in errors:
                print(f"WARNING: {error}")
        
        return tool_functions
    
    def _is_similar_tool_name(self, name1: str, name2: str) -> bool:
        """Conservative similarity check for tool name suggestions"""
        # Only suggest if one is a substring of the other (for obvious typos)
        if len(name1) >= 4 and len(name2) >= 4:
            if name1.lower() in name2.lower() or name2.lower() in name1.lower():
                return True
        
        # Only suggest for single character differences in same-length names
        if len(name1) == len(name2) and len(name1) >= 5:
            diff_count = sum(c1 != c2 for c1, c2 in zip(name1.lower(), name2.lower()))
            return diff_count == 1  # Only single character differences
        
        return False
    
    async def _create_mcp_servers(self, mcp_configs: List[Union[str, MCPServerConfig]]) -> List[Any]:
        """Create and initialize MCP servers for an agent"""
        mcp_servers = []
        
        for mcp_config in mcp_configs:
            try:
                if isinstance(mcp_config, str):
                    server_name = mcp_config
                    server_config = MCPServerConfig(name=server_name)
                else:
                    server_name = mcp_config.name
                    server_config = mcp_config
                
                server_json_config = self.mcp_config_manager.get_server_config(server_name)
                if not server_json_config:
                    available_servers = list(self.mcp_config_manager.get_available_servers().keys())
                    # Simple fuzzy matching for suggestions
                    close_matches = [s for s in available_servers if self._is_similar_tool_name(server_name, s)]
                    
                    error_msg = f"MCP server '{server_name}' not found in configuration."
                    if close_matches:
                        error_msg += f" Did you mean: {', '.join(close_matches[:3])}?"
                    error_msg += f" Available MCP servers: {', '.join(sorted(available_servers))}"
                    error_msg += " Check your MCP server configuration in .cursor/mcp.json"
                    
                    print(f"WARNING: {error_msg}")
                    continue
                
                mcp_server = self.mcp_config_manager.create_mcp_server(
                    server_name, 
                    server_json_config, 
                    tool_prefix=server_config.prefix
                )
                
                mcp_servers.append(mcp_server)
                print(f"Loaded MCP server: {server_name}")
                
            except Exception as e:
                print(f"ERROR: Failed to load MCP server '{server_name}': {e}")
                continue
        
        return mcp_servers
    
    async def run_agent_async(self, agent_name: str, message: str, files: List[str] = None, run_id: Optional[str] = None):
        """Run an agent asynchronously with optional run continuation and file context
        
        Args:
            agent_name: Name of the agent to run
            message: Message to send to the agent
            files: Optional list of file paths to provide as context to the agent
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
        
        try:
            config = await self._parse_agent_config(agent_file, files)
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
        
        # Set up OpenRouter API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return {
                "output": "",
                "success": False,
                "error": "OPENROUTER_API_KEY environment variable not set"
            }
        
        # Create OpenRouter model with validation
        try:
            model = OpenAIModel(
                model_name=config.model,
                provider=OpenAIProvider(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
            )
        except Exception as e:
            # Check for common model name issues
            model_error = str(e)
            if "404" in model_error or "not found" in model_error.lower():
                return {
                    "output": "",
                    "success": False,
                    "error": f"Model '{config.model}' not found on OpenRouter. Check https://openrouter.ai/models for available models.",
                    "error_type": "model_not_found",
                    "model_name": config.model
                }
            elif "401" in model_error or "unauthorized" in model_error.lower():
                return {
                    "output": "",
                    "success": False,
                    "error": "OpenRouter API authentication failed. Check your OPENROUTER_API_KEY.",
                    "error_type": "auth_failed"
                }
            else:
                return {
                    "output": "",
                    "success": False,
                    "error": f"Failed to initialize model '{config.model}': {e}",
                    "error_type": "model_init_failed",
                    "model_name": config.model
                }
        
        # Create model settings
        model_settings = ModelSettings(
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            top_p=config.top_p,
            presence_penalty=config.presence_penalty,
            frequency_penalty=config.frequency_penalty,
            timeout=config.timeout,
            stream=config.stream,
            parallel_tool_calls=True
        )
        
        # Load tools and MCP servers
        tool_functions = self._create_tool_functions(config.tools)
        mcp_servers = []
        if config.mcp:
            mcp_servers = await self._create_mcp_servers(config.mcp)
        
        # Create usage limits
        usage_limits = UsageLimits(
            request_limit=self.config.get('usage_limits', {}).get('request_limit', 50),
            request_tokens_limit=self.config.get('usage_limits', {}).get('request_tokens_limit'),
            response_tokens_limit=self.config.get('usage_limits', {}).get('response_tokens_limit'),
            total_tokens_limit=self.config.get('usage_limits', {}).get('total_tokens_limit')
        )
        
        # Create agent
        if mcp_servers:
            agent = Agent(
                model=model,
                system_prompt=config.system_prompt,
                tools=tool_functions if tool_functions else [],
                model_settings=model_settings,
                mcp_servers=mcp_servers
            )
        else:
            agent = Agent(
                model=model,
                system_prompt=config.system_prompt,
                tools=tool_functions if tool_functions else [],
                model_settings=model_settings
            )
        
        try:
            # Create or update run in persistence
            if is_new_run:
                self.run_persistence.create_run(run_id, agent_name, message)
            
            # Set run ID in tool helper for file organization
            tool_services.set_run_id(run_id)
            
            # Run the agent with message history - Pydantic AI handles everything
            if mcp_servers:
                async with agent.run_mcp_servers():
                    result = await agent.run(message, message_history=message_history, usage_limits=usage_limits)
            else:
                result = await agent.run(message, message_history=message_history, usage_limits=usage_limits)
            
            # Prepare response data
            response_data = {
                "output": str(result.output),
                "success": True,
                "run_id": run_id,
                "is_new_run": is_new_run,
                "usage": {
                    "requests": result.usage().requests,
                    "request_tokens": result.usage().request_tokens,
                    "response_tokens": result.usage().response_tokens,
                    "total_tokens": result.usage().total_tokens,
                },
                # Optionally include message history for debugging
                "messages": result.all_messages() if self.config.get('debug', {}).get('include_message_history', False) else None,
                # Tool calls are available in messages if needed
                "tool_calls_summary": self._extract_tool_call_summary(result.all_messages())
            }
            
            # Update run persistence with new messages
            self.run_persistence.update_run(run_id, response_data, result.new_messages())
            
            return response_data
            
        except Exception as e:
            # Handle common MCP server errors with helpful messages
            error_message = str(e)
            
            if "401 Unauthorized" in error_message:
                return {
                    "output": "",
                    "success": False,
                    "run_id": run_id if 'run_id' in locals() else None,
                    "error": f"MCP server authentication failed: {e}\n"
                            f"This usually means the MCP server requires authentication credentials.\n"
                            f"Check your MCP server configuration for missing API keys or tokens."
                }
            elif "Connection" in error_message or "timeout" in error_message.lower():
                return {
                    "output": "",
                    "success": False,
                    "run_id": run_id if 'run_id' in locals() else None,
                    "error": f"MCP server connection failed: {e}\n"
                            f"Check that the MCP server is running and accessible."
                }
            else:
                return {
                    "output": "",
                    "success": False,
                    "run_id": run_id if 'run_id' in locals() else None,
                    "error": f"Agent execution failed: {e}"
                }
    
    def _extract_tool_call_summary(self, messages) -> List[str]:
        """Simple tool call summary - much lighter than full extraction"""
        from pydantic_ai.messages import ToolCallPart
        
        tool_calls = []
        for message in messages:
            if hasattr(message, 'parts') and message.parts:
                for part in message.parts:
                    if isinstance(part, ToolCallPart):
                        tool_calls.append(part.tool_name)
        
        return list(set(tool_calls))  # Unique tool names used
    
    def run_agent(self, agent_name: str, message: str, files: List[str] = None, run_id: Optional[str] = None):
        """Synchronous wrapper"""
        return asyncio.run(self.run_agent_async(agent_name, message, files, run_id))
    
    def run_agent_clean(self, agent_name: str, message: str, files: List[str] = None, run_id: Optional[str] = None) -> str:
        """Clean formatted response for MCP server"""
        result = self.run_agent(agent_name, message, files, run_id)
        
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
        print("Usage: python agent_runner.py <agent_name> <message> [--files <file1|file2|...>] [--run-id <run_id>] [--json] [--debug]")
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
    
    runner = AgentRunner()
    
    if json_output:
        result = runner.run_agent(agent_name, message, files, run_id)
        print(json.dumps(result, indent=2))
    else:
        result = runner.run_agent_clean(agent_name, message, files, run_id)
        print(result)


if __name__ == "__main__":
    main()