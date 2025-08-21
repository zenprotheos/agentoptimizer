"""
Agent tool management module.
Handles loading, validation, and creation of tools and MCP servers for agents.
"""

import os
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Union
from app.mcp_config import MCPConfigManager, MCPServerConfig


class AgentToolManager:
    """Manages tool loading and MCP server creation for agents"""
    
    def __init__(self, tools_dir: Path, mcp_config_manager: MCPConfigManager, debug: bool = False):
        self.tools_dir = tools_dir
        self.mcp_config_manager = mcp_config_manager
        self.debug = debug
        self.loaded_tools = {}
        self._load_tools()
    
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
                    if self.debug:
                        print(f"Loaded tool: {tool_name}")
                    
            except Exception as e:
                if self.debug:
                    print(f"Error loading tool {tool_file}: {e}")
    
    def create_tool_functions(self, tool_names: List[str], config: Dict[str, Any] = None) -> List[Any]:
        """Create tool functions for Pydantic AI from loaded tools with enhanced error handling and usage tracking"""
        tool_functions = []
        errors = []
        
        # Get usage tracking settings from config
        usage_limits_config = config.get('usage_limits', {}) if config else {}
        show_usage_stats = usage_limits_config.get('show_usage_stats', False)
        
        for tool_name in tool_names:
            if tool_name in self.loaded_tools:
                tool_info = self.loaded_tools[tool_name]
                tool_func = tool_info['function']
                
                if tool_func:
                    if show_usage_stats:
                        # Wrap the tool function with usage tracking
                        wrapped_func = self._wrap_tool_with_usage_tracking(tool_func, tool_name)
                        tool_functions.append(wrapped_func)
                    else:
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
    
    def _wrap_tool_with_usage_tracking(self, tool_func, tool_name):
        """Wrap a tool function to track usage and append usage stats to responses"""
        import functools
        import os
        
        @functools.wraps(tool_func)
        def wrapped_tool(*args, **kwargs):
            # Call the original tool function
            result = tool_func(*args, **kwargs)
            
            # Get current usage context from environment variables
            try:
                current_requests = int(os.getenv('ONESHOT_CURRENT_REQUESTS', 0))
                request_limit = int(os.getenv('ONESHOT_REQUEST_LIMIT', 30))
                
                # Increment the request count (this is a rough approximation)
                # Note: This tracks tool calls, not actual LLM requests
                current_requests += 1
                os.environ['ONESHOT_CURRENT_REQUESTS'] = str(current_requests)
                
                # Calculate usage statistics
                remaining_requests = max(0, request_limit - current_requests)
                usage_percentage = int((current_requests / request_limit) * 100) if request_limit > 0 else 0
                
                # Create usage footer
                if usage_percentage < 50:
                    status_emoji = "🟢"
                elif usage_percentage < 75:
                    status_emoji = "🟡"
                elif usage_percentage < 90:
                    status_emoji = "🟠"
                else:
                    status_emoji = "🔴"
                
                usage_footer = f"\n\n---\n{status_emoji} *Tool usage: {current_requests}/{request_limit} calls ({usage_percentage}%) - {remaining_requests} remaining*"
                
                # Append usage footer to result if it's a string
                if isinstance(result, str):
                    result = result + usage_footer
                
            except Exception as e:
                # If usage tracking fails, don't break the tool
                if self.debug:
                    print(f"Warning: Usage tracking failed for {tool_name}: {e}")
            
            return result
        
        return wrapped_tool
    
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
    
    async def create_mcp_servers(self, mcp_configs: List[Union[str, MCPServerConfig]]) -> List[Any]:
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
                    
                    if self.debug:
                        print(f"WARNING: {error_msg}")
                    continue
                
                mcp_server = self.mcp_config_manager.create_mcp_server(
                    server_name, 
                    server_json_config, 
                    tool_prefix=server_config.prefix
                )
                
                mcp_servers.append(mcp_server)
                if self.debug:
                    print(f"Loaded MCP server: {server_name}")
                
            except Exception as e:
                if self.debug:
                    print(f"ERROR: Failed to load MCP server '{server_name}': {e}")
                continue
        
        return mcp_servers
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.loaded_tools.keys()) 