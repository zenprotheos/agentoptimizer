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

# Import MCP-related classes
from app.mcp_config import MCPConfigManager, MCPServerConfig

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


class SimplifiedAgentRunner:
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
        
        # Initialize Jinja2 environment for template rendering
        self._setup_template_engine()
    
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
    
    def _setup_template_engine(self):
        """Setup Jinja2 template engine for includes"""
        template_config = self.config.get('template_engine', {})
        
        # Get base path for includes, default to ./snippets
        base_path = template_config.get('base_path', './snippets')
        if not Path(base_path).is_absolute():
            base_path = Path(__file__).parent.parent / base_path
        else:
            base_path = Path(base_path)
        
        # Create the snippets directory if it doesn't exist
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.enable_async = template_config.get('enable_async', True)
        self.jinja_env = Environment(
            loader=FileSystemLoader([
                str(base_path),  # Primary snippets directory
                '/',  # Allow absolute paths
            ]),
            autoescape=template_config.get('autoescape', False),
            enable_async=self.enable_async
        )
        
        print(f"Template engine initialized with base path: {base_path}")
    
    async def _render_template(self, content: str) -> str:
        """Render Jinja2 template content with includes"""
        try:
            template = self.jinja_env.from_string(content)
            if self.enable_async:
                return await template.render_async()
            else:
                return template.render()
        except TemplateNotFound as e:
            raise ValueError(f"Template include file not found: {e}")
        except Exception as e:
            raise ValueError(f"Template rendering error: {e}")
    
    async def _parse_agent_config(self, agent_file: Path) -> AgentConfig:
        """Parse agent configuration from markdown file"""
        content = agent_file.read_text()
        
        # Split on the first --- to get the YAML frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid agent file format: {agent_file}")
        
        # Parse YAML frontmatter
        yaml_content = parts[1].strip()
        config_data = yaml.safe_load(yaml_content)
        
        # Extract system prompt (everything after the second ---)
        system_prompt = parts[2].strip()
        
        # Render system prompt with Jinja2 template engine for includes
        try:
            system_prompt = await self._render_template(system_prompt)
        except Exception as e:
            raise ValueError(f"Error rendering template for {agent_file}: {e}")
        
        config_data['system_prompt'] = system_prompt
        
        # Apply defaults from config file
        model_defaults = self.config.get('model_settings', {})
        for key, default_value in model_defaults.items():
            if key not in config_data:
                config_data[key] = default_value
        
        return AgentConfig(config_data)
    
    def _create_tool_functions(self, tool_names: List[str]) -> List[Any]:
        """Create tool functions for Pydantic AI from loaded tools"""
        tool_functions = []
        
        for tool_name in tool_names:
            if tool_name in self.loaded_tools:
                tool_info = self.loaded_tools[tool_name]
                tool_func = tool_info['function']
                
                if tool_func:
                    tool_functions.append(tool_func)
                else:
                    print(f"ERROR: Tool '{tool_name}' has no main function")
            else:
                available_tools = list(self.loaded_tools.keys())
                print(f"ERROR: Tool '{tool_name}' not found in loaded tools.")
                print(f"Available tools: {available_tools}")
                print(f"Check agent configuration file for typos or ensure the tool file exists in the tools directory.")
        
        return tool_functions
    
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
                    print(f"ERROR: MCP server '{server_name}' not found in configuration.")
                    print(f"Available MCP servers: {available_servers}")
                    print(f"Check agent configuration file for typos. Server names are case-sensitive unless case_insensitive_matching is enabled.")
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
    
    async def run_agent_async(self, agent_name: str, message: str):
        """Run an agent asynchronously - leverages Pydantic AI's built-in capabilities"""
        
        # Load agent configuration
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            return {
                "output": "",
                "success": False,
                "error": f"Agent {agent_name} not found at {agent_file}"
            }
        
        try:
            config = await self._parse_agent_config(agent_file)
        except Exception as e:
            return {
                "output": "",
                "success": False,
                "error": f"Error parsing agent config: {e}"
            }
        
        # Set up OpenRouter API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return {
                "output": "",
                "success": False,
                "error": "OPENROUTER_API_KEY environment variable not set"
            }
        
        # Create OpenRouter model
        model = OpenAIModel(
            model_name=config.model,
            provider=OpenAIProvider(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
        )
        
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
                tools=tool_functions if tool_functions else None,
                model_settings=model_settings,
                mcp_servers=mcp_servers
            )
        else:
            agent = Agent(
                model=model,
                system_prompt=config.system_prompt,
                tools=tool_functions if tool_functions else None,
                model_settings=model_settings
            )
        
        try:
            # Run the agent - Pydantic AI handles everything
            if mcp_servers:
                async with agent.run_mcp_servers():
                    result = await agent.run(message, usage_limits=usage_limits)
            else:
                result = await agent.run(message, usage_limits=usage_limits)
            
            # Return simplified response - let Pydantic AI handle the complexity
            return {
                "output": str(result.output),
                "success": True,
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
            
        except Exception as e:
            # Handle common MCP server errors with helpful messages
            error_message = str(e)
            
            if "401 Unauthorized" in error_message:
                return {
                    "output": "",
                    "success": False,
                    "error": f"MCP server authentication failed: {e}\n"
                            f"This usually means the MCP server requires authentication credentials.\n"
                            f"Check your MCP server configuration for missing API keys or tokens."
                }
            elif "Connection" in error_message or "timeout" in error_message.lower():
                return {
                    "output": "",
                    "success": False,
                    "error": f"MCP server connection failed: {e}\n"
                            f"Check that the MCP server is running and accessible."
                }
            else:
                return {
                    "output": "",
                    "success": False,
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
    
    def run_agent(self, agent_name: str, message: str):
        """Synchronous wrapper"""
        return asyncio.run(self.run_agent_async(agent_name, message))
    
    def run_agent_clean(self, agent_name: str, message: str) -> str:
        """Clean formatted response for MCP server"""
        result = self.run_agent(agent_name, message)
        
        if result["success"]:
            output = result["output"]
            
            # Add usage stats
            usage = result["usage"]
            output += f"\n\n---\n"
            output += f"**Usage:** {usage['requests']} requests"
            if usage["total_tokens"]:
                output += f", {usage['total_tokens']:,} tokens"
            if result["tool_calls_summary"]:
                output += f"\n**Tools used:** {', '.join(result['tool_calls_summary'])}"
            
            return output
        else:
            return f"ERROR: {result['error']}"


def main():
    """CLI interface"""
    if len(sys.argv) < 3:
        print("Usage: python agent_runner_simplified.py <agent_name> <message> [--json]")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    message = sys.argv[2]
    json_output = "--json" in sys.argv[3:]
    
    runner = SimplifiedAgentRunner()
    
    if json_output:
        result = runner.run_agent(agent_name, message)
        print(json.dumps(result, indent=2))
    else:
        result = runner.run_agent_clean(agent_name, message)
        print(result)


if __name__ == "__main__":
    main()