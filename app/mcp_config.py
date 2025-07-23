"""
MCP Configuration Manager
Handles loading and parsing MCP server configurations from mcp.json files
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel
from pydantic_ai.mcp import MCPServerStdio, MCPServerSSE, MCPServerStreamableHTTP


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server"""
    name: str
    prefix: Optional[str] = None
    allow_sampling: bool = True


class MCPConfigError(Exception):
    """Raised when there are issues with MCP configuration"""
    pass


class MCPConfigManager:
    """Manages MCP server configurations from mcp.json files"""
    
    def __init__(self, workspace_path: Path, config: Optional[Dict[str, Any]] = None):
        self.workspace_path = workspace_path
        self.config = config or {}
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def load_mcp_config(self) -> Dict[str, Any]:
        """
        Load MCP configuration from local and global mcp.json files.
        Local configuration takes precedence over global.
        """
        if self._config_cache is not None:
            return self._config_cache
        
        config = {}
        
        # Get configurable paths from config
        mcp_config = self.config.get('mcp_config', {})
        global_config_path = Path(mcp_config.get('global_config_path', '~/.cursor/mcp.json')).expanduser()
        local_config_path = self.workspace_path / mcp_config.get('local_config_path', '.cursor/mcp.json')
        
        # Load global configuration first (lower priority)
        if global_config_path.exists():
            try:
                with open(global_config_path, 'r') as f:
                    global_config = json.load(f)
                    config.update(global_config.get('mcpServers', {}))
                    print(f"Loaded global MCP config from {global_config_path}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load global MCP config from {global_config_path}: {e}")
        
        # Load local configuration (higher priority, overrides global)
        if local_config_path.exists():
            try:
                with open(local_config_path, 'r') as f:
                    local_config = json.load(f)
                    config.update(local_config.get('mcpServers', {}))
                    print(f"Loaded local MCP config from {local_config_path}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load local MCP config from {local_config_path}: {e}")
        
        self._config_cache = config
        return config
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific MCP server.
        Supports case-insensitive matching if enabled in config.
        """
        config = self.load_mcp_config()
        
        # First try exact match
        if server_name in config:
            return config[server_name]
        
        # If case-insensitive matching is enabled, try that
        mcp_config = self.config.get('mcp_config', {})
        if mcp_config.get('case_insensitive_matching', True):
            server_name_lower = server_name.lower()
            for key, value in config.items():
                if key.lower() == server_name_lower:
                    print(f"MCP server '{server_name}' matched '{key}' (case-insensitive)")
                    return value
        
        return None
    
    def get_available_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all available MCP servers for error reporting"""
        return self.load_mcp_config()
    
    def create_mcp_server(self, server_name: str, config: Dict[str, Any], tool_prefix: Optional[str] = None) -> Union[MCPServerStdio, MCPServerSSE, MCPServerStreamableHTTP]:
        """
        Create an MCP server instance based on configuration.
        Automatically detects transport type based on config.
        """
        try:
            # Use prefix from config if no explicit prefix provided
            if tool_prefix is None:
                tool_prefix = config.get('prefix')
            
            # Check if it's an HTTP server (has 'url' field)
            if 'url' in config:
                headers = config.get('headers', {})
                if 'sse' in config.get('url', '').lower() or config.get('type') == 'sse':
                    return MCPServerSSE(
                        url=config['url'],
                        headers=headers,
                        tool_prefix=tool_prefix
                    )
                else:
                    return MCPServerStreamableHTTP(
                        url=config['url'],
                        headers=headers,
                        tool_prefix=tool_prefix
                    )
            
            # Otherwise, it's a stdio server
            command = config.get('command')
            args = config.get('args', [])
            env = config.get('env', {})
            
            if not command:
                raise MCPConfigError(f"MCP server '{server_name}' missing required 'command' field")
            
            return MCPServerStdio(
                command=command,
                args=args,
                env=env,
                tool_prefix=tool_prefix
            )
        except Exception as e:
            # Provide helpful error message
            available_servers = list(self.get_available_servers().keys())
            raise MCPConfigError(
                f"Failed to create MCP server '{server_name}': {e}\n"
                f"Available servers: {available_servers}"
            ) from e
    
    def list_available_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all available MCP servers and their configurations"""
        return self.load_mcp_config() 