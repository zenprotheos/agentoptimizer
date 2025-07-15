#!/usr/bin/env python3
"""
Simple AI Agent Framework using Pydantic AI and OpenRouter
"""

import os
import sys
import yaml
import json
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits
from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ToolCallInfo(BaseModel):
    """Information about a tool call made during agent execution"""
    tool_name: str
    call_id: str
    arguments: Dict[str, Any]
    result: Optional[str] = None


class UsageInfo(BaseModel):
    """Usage statistics for an agent run"""
    requests: int
    request_tokens: Optional[int] = None
    response_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Structured response from agent execution"""
    output: str
    usage: UsageInfo
    tool_calls: List[ToolCallInfo]
    success: bool
    error: Optional[str] = None


class AgentConfig(BaseModel):
    """Configuration for an AI agent parsed from markdown"""
    name: str
    description: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    parallel_tool_calls: bool = True
    seed: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    timeout: float = 30.0
    stream: bool = False
    return_tool_output_only: bool = False
    tools: List[str] = []
    system_prompt: str = ""


class AgentRunner:
    """Main agent runner that loads and executes agents"""
    
    def __init__(self, agents_dir: str = "agents", tools_dir: str = "tools", config_file: str = "config.yaml"):
        # Get the project root directory (parent of the app directory)
        project_root = Path(__file__).parent.parent
        self.agents_dir = project_root / agents_dir
        self.tools_dir = project_root / tools_dir
        self.config_file = project_root / config_file
        self.config = self._load_config()
        self.loaded_tools = {}
        self._load_tools()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            print(f"Warning: Config file {self.config_file} not found, using defaults")
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
            print(f"Tools directory {self.tools_dir} does not exist")
            return
            
        for tool_file in self.tools_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(tool_file.stem, tool_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Each tool should have a TOOL_METADATA dict and a function with the same name as the file
                if hasattr(module, 'TOOL_METADATA'):
                    tool_name = tool_file.stem
                    function_name = tool_name  # Function name should match the file name
                    self.loaded_tools[tool_name] = {
                        'module': module,
                        'metadata': module.TOOL_METADATA,
                        'function': getattr(module, function_name, None)
                    }
                    print(f"Loaded tool: {tool_name}")
                else:
                    print(f"Warning: {tool_file} missing TOOL_METADATA")
                    
            except Exception as e:
                print(f"Error loading tool {tool_file}: {e}")
    
    def _parse_agent_config(self, agent_file: Path) -> AgentConfig:
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
        config_data['system_prompt'] = system_prompt
        
        # Get defaults from config file
        model_defaults = self.config.get('model_settings', {})
        
        # Apply defaults for missing values
        for key, default_value in model_defaults.items():
            if key not in config_data:
                config_data[key] = default_value
        
        return AgentConfig(**config_data)
    
    def _create_tool_functions(self, tool_names: List[str]) -> List[Any]:
        """Create tool functions for Pydantic AI from loaded tools"""
        tool_functions = []
        
        for tool_name in tool_names:
            if tool_name in self.loaded_tools:
                tool_info = self.loaded_tools[tool_name]
                tool_func = tool_info['function']
                tool_metadata = tool_info['metadata']
                
                if tool_func:
                    # For now, let's just pass the original function directly
                    # Pydantic AI should be able to handle it with proper type annotations
                    tool_functions.append(tool_func)
                else:
                    print(f"Warning: Tool {tool_name} has no main function")
            else:
                print(f"Warning: Tool {tool_name} not found in loaded tools")
        
        return tool_functions
    
    def _extract_tool_calls(self, messages: List[ModelMessage]) -> List[ToolCallInfo]:
        """Extract tool call information from message history"""
        tool_calls = []
        tool_results = {}
        
        for message in messages:
            if hasattr(message, 'parts') and message.parts:
                for part in message.parts:
                    # Handle tool calls
                    if isinstance(part, ToolCallPart):
                        # Get arguments as dict, handling both string and dict formats
                        if hasattr(part, 'args_as_dict'):
                            arguments = part.args_as_dict()
                        elif hasattr(part, 'args'):
                            arguments = part.args if isinstance(part.args, dict) else {}
                        else:
                            arguments = {}
                            
                        tool_calls.append(ToolCallInfo(
                            tool_name=part.tool_name,
                            call_id=part.tool_call_id,
                            arguments=arguments
                        ))
                    # Handle tool results
                    elif isinstance(part, ToolReturnPart):
                        tool_results[part.tool_call_id] = str(part.content)
        
        # Match results to calls
        for tool_call in tool_calls:
            if tool_call.call_id in tool_results:
                tool_call.result = tool_results[tool_call.call_id]
        
        return tool_calls
    
    def run_agent(self, agent_name: str, message: str) -> Union[str, AgentResponse]:
        """Run an agent with the given message and return structured response"""
        
        # Load agent configuration
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error=f"Agent {agent_name} not found at {agent_file}"
            )
        
        try:
            config = self._parse_agent_config(agent_file)
        except Exception as e:
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error=f"Error parsing agent config: {e}"
            )
        
        # Set up OpenRouter API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error="OPENROUTER_API_KEY environment variable not set"
            )
        
        # Create the model with OpenAI provider configured for OpenRouter
        provider = OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        model = OpenAIModel(
            model_name=config.model,
            provider=provider
        )
        
        # Create tool functions
        tool_functions = self._create_tool_functions(config.tools)
        
        # Create model settings
        model_settings = ModelSettings(
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            presence_penalty=config.presence_penalty,
            frequency_penalty=config.frequency_penalty,
            parallel_tool_calls=config.parallel_tool_calls,
            seed=config.seed,
            stop_sequences=config.stop_sequences,
            timeout=config.timeout
        )
        
        # Create usage limits
        usage_limits_config = self.config.get('usage_limits', {})
        usage_limits = UsageLimits(
            request_limit=usage_limits_config.get('request_limit', 50),
            request_tokens_limit=usage_limits_config.get('request_tokens_limit'),
            response_tokens_limit=usage_limits_config.get('response_tokens_limit'),
            total_tokens_limit=usage_limits_config.get('total_tokens_limit')
        )
        
        # Create the agent
        agent = Agent(
            model=model,
            system_prompt=config.system_prompt,
            tools=tool_functions if tool_functions else None,
            model_settings=model_settings
        )
        
        try:
            # Run the agent with usage limits
            result = agent.run_sync(message, usage_limits=usage_limits)
            
            # Extract tool calls and results from the result
            tool_calls = self._extract_tool_calls(result.all_messages())
            
            # Create AgentResponse object
            agent_response = AgentResponse(
                output=str(result.output),
                usage=UsageInfo(
                    requests=result.usage().requests,
                    request_tokens=result.usage().request_tokens,
                    response_tokens=result.usage().response_tokens,
                    total_tokens=result.usage().total_tokens,
                    details=result.usage().details
                ),
                tool_calls=tool_calls,
                success=True,
                error=None
            )
            return agent_response
        except Exception as e:
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error=f"Error running agent: {e}"
            )
    
    async def run_agent_async(self, agent_name: str, message: str) -> AgentResponse:
        """Run an agent asynchronously - for use in async contexts like MCP servers"""
        # Load agent configuration
        agent_file = self.agents_dir / f"{agent_name}.md"
        if not agent_file.exists():
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error=f"Agent {agent_name} not found at {agent_file}"
            )
        
        try:
            config = self._parse_agent_config(agent_file)
        except Exception as e:
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error=f"Error parsing agent config: {e}"
            )
        
        # Set up OpenRouter API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error="OPENROUTER_API_KEY environment variable not set"
            )
        
        # Create OpenRouter model
        model = OpenAIModel(
            model_name=config.model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
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
        
        # Load and prepare tools
        tool_functions = self._load_agent_tools(config.tools)
        
        # Create usage limits
        usage_limits = UsageLimits(
            request_limit=self.config.get('usage_limits', {}).get('request_limit', 50),
            request_tokens_limit=self.config.get('usage_limits', {}).get('request_tokens_limit'),
            response_tokens_limit=self.config.get('usage_limits', {}).get('response_tokens_limit'),
            total_tokens_limit=self.config.get('usage_limits', {}).get('total_tokens_limit')
        )
        
        # Create agent
        agent = Agent(
            model=model,
            system_prompt=config.system_prompt,
            tools=tool_functions if tool_functions else None,
            model_settings=model_settings
        )
        
        try:
            # Run the agent asynchronously
            result = await agent.run(message, usage_limits=usage_limits)
            
            # Extract tool calls and results from the result
            tool_calls = self._extract_tool_calls(result.all_messages())
            
            # Create AgentResponse object
            agent_response = AgentResponse(
                output=str(result.output),
                usage=UsageInfo(
                    requests=result.usage().requests,
                    request_tokens=result.usage().request_tokens,
                    response_tokens=result.usage().response_tokens,
                    total_tokens=result.usage().total_tokens,
                    details=result.usage().details
                ),
                tool_calls=tool_calls,
                success=True,
                error=None
            )
            return agent_response
        except Exception as e:
            return AgentResponse(
                output="",
                usage=UsageInfo(requests=0),
                tool_calls=[],
                success=False,
                error=f"Error running agent: {e}"
            )
    
    def run_agent_json(self, agent_name: str, message: str) -> str:
        """Run an agent and return JSON response"""
        result = self.run_agent(agent_name, message)
        if isinstance(result, AgentResponse):
            return result.model_dump_json(indent=2)
        else:
            # Fallback for any unexpected string returns
            return json.dumps({"output": str(result), "success": False, "error": "Unexpected response format"}, indent=2)
    
    def run_agent_clean(self, agent_name: str, message: str) -> str:
        """Run an agent and return clean formatted response for MCP server"""
        result = self.run_agent(agent_name, message)
        if isinstance(result, AgentResponse):
            if result.success:
                # Format clean response
                output = result.output
                
                # Add clean usage stats
                output += f"\n\n---\n"
                output += f"**Usage:** {result.usage.requests} requests"
                if result.usage.total_tokens:
                    output += f", {result.usage.total_tokens:,} tokens"
                if result.tool_calls:
                    tools_used = ', '.join(set(tc.tool_name for tc in result.tool_calls))
                    output += f"\n**Tools used:** {tools_used}"
                
                return output
            else:
                return f"ERROR: {result.error}"
        else:
            return str(result)


def main():
    """CLI interface for the agent runner"""
    if len(sys.argv) < 3:
        print("Usage: python agent_runner.py <agent_name> <message> [--json] [--debug]")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    message = sys.argv[2]
    
    # Parse flags
    json_output = "--json" in sys.argv[3:]
    debug_output = "--debug" in sys.argv[3:]
    
    runner = AgentRunner()
    
    if json_output:
        result = runner.run_agent_json(agent_name, message)
        print(result)
    else:
        result = runner.run_agent(agent_name, message)
        
        if isinstance(result, AgentResponse):
            if result.success:
                # Clean markdown output by default
                print(result.output)
                
                # Add clean usage stats
                print(f"\n---")
                print(f"**Usage:** {result.usage.requests} requests")
                if result.usage.total_tokens:
                    print(f"**Tokens:** {result.usage.total_tokens:,}")
                if result.tool_calls:
                    print(f"**Tools used:** {', '.join(set(tc.tool_name for tc in result.tool_calls))}")
                
                # Detailed debug output only if --debug flag is used
                if debug_output:
                    print("\n=== DEBUG: DETAILED OUTPUT ===")
                    print(f"Request Tokens: {result.usage.request_tokens}")
                    print(f"Response Tokens: {result.usage.response_tokens}")
                    if result.usage.details:
                        print(f"Details: {json.dumps(result.usage.details, indent=2)}")
                    
                    if result.tool_calls:
                        print("\n=== DEBUG: TOOL CALLS ===")
                        for i, tool_call in enumerate(result.tool_calls, 1):
                            print(f"{i}. Tool: {tool_call.tool_name}")
                            print(f"   Call ID: {tool_call.call_id}")
                            print(f"   Arguments: {json.dumps(tool_call.arguments, indent=2)}")
                            if tool_call.result:
                                print(f"   Result: {tool_call.result}")
                            print()
            else:
                print(f"ERROR: {result.error}")
        else:
            print(result)


if __name__ == "__main__":
    main() 