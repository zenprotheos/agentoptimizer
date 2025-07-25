#!/usr/bin/env python3
"""
Agent Configuration Validation Utilities
Provides comprehensive validation for agent configurations with specific error reporting.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from yaml.scanner import ScannerError
from yaml.parser import ParserError

from .agent_errors import (
    AgentConfigError, YAMLFrontmatterError, MissingRequiredFieldError,
    InvalidModelError, InvalidToolError, InvalidMCPServerError,
    TemplateProcessingError, InvalidFieldTypeError, AgentFileFormatError
)


class AgentConfigValidator:
    """Validates agent configuration files and provides detailed error reporting"""
    
    def __init__(self, tools_dir: Path, available_tools: List[str], available_mcp_servers: List[str]):
        self.tools_dir = tools_dir
        self.available_tools = available_tools
        self.available_mcp_servers = available_mcp_servers
        
        # Common valid models (can be extended)
        self.common_models = [
            "openai/gpt-4o",
            "openai/gpt-4o-mini", 
            "openai/gpt-4.1-mini",
            "openai/gpt-4.1",
            "anthropic/claude-sonnet-4",
            "anthropic/claude-3.5-haiku",
            "google/gemini-2.5-flash-lite",
            "google/gemini-2.5-flash", 
            "google/gemini-2.5-pro"
        ]
        
        # Required fields in agent configuration
        self.required_fields = ["name", "description", "model"]
        
        # Field type validation
        self.field_types = {
            "name": str,
            "description": str,
            "model": str,
            "tools": list,
            "mcp": list,
            "temperature": (int, float),
            "max_tokens": int,
            "top_p": (int, float),
            "presence_penalty": (int, float),
            "frequency_penalty": (int, float),
            "timeout": (int, float),
            "stream": bool
        }
    
    def validate_agent_file_format(self, agent_file: Path) -> Tuple[str, str]:
        """
        Validate basic agent file format and extract YAML and content sections.
        
        Returns:
            Tuple of (yaml_content, system_prompt_content)
        
        Raises:
            AgentFileFormatError: If file format is invalid
        """
        try:
            content = agent_file.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            raise AgentFileFormatError(
                f"File encoding error: {e}. Ensure file is saved as UTF-8.",
                agent_file
            )
        except FileNotFoundError:
            raise AgentFileFormatError(f"Agent file not found: {agent_file}", agent_file)
        
        # Check for frontmatter delimiters
        if not content.startswith('---'):
            raise AgentFileFormatError(
                "Agent file must start with YAML frontmatter delimiter '---'",
                agent_file
            )
        
        # Split on --- delimiters
        parts = content.split('---', 2)
        
        if len(parts) < 3:
            raise AgentFileFormatError(
                "Agent file must have YAML frontmatter enclosed in '---' delimiters",
                agent_file
            )
        
        yaml_content = parts[1].strip()
        system_prompt = parts[2].strip()
        
        if not yaml_content:
            raise AgentFileFormatError(
                "YAML frontmatter section is empty",
                agent_file
            )
        
        if not system_prompt:
            raise AgentFileFormatError(
                "System prompt section is empty",
                agent_file
            )
        
        return yaml_content, system_prompt
    
    def validate_yaml_frontmatter(self, yaml_content: str, agent_file: Path) -> Dict[str, Any]:
        """
        Validate and parse YAML frontmatter.
        
        Returns:
            Parsed configuration dictionary
        
        Raises:
            YAMLFrontmatterError: If YAML is invalid
        """
        try:
            config_data = yaml.safe_load(yaml_content)
        except ScannerError as e:
            # Extract line number from error
            line_number = getattr(e, 'problem_mark', None)
            line_num = line_number.line + 1 if line_number else None
            
            raise YAMLFrontmatterError(
                f"YAML syntax error: {e.problem}",
                agent_file,
                yaml_content,
                line_num
            )
        except ParserError as e:
            line_number = getattr(e, 'problem_mark', None)
            line_num = line_number.line + 1 if line_number else None
            
            raise YAMLFrontmatterError(
                f"YAML parsing error: {e.problem}",
                agent_file,
                yaml_content,
                line_num
            )
        except Exception as e:
            raise YAMLFrontmatterError(
                f"Unexpected YAML error: {e}",
                agent_file,
                yaml_content
            )
        
        if not isinstance(config_data, dict):
            raise YAMLFrontmatterError(
                f"YAML frontmatter must be a dictionary/object, got {type(config_data).__name__}",
                agent_file,
                yaml_content
            )
        
        return config_data
    
    def validate_required_fields(self, config_data: Dict[str, Any], agent_file: Path):
        """
        Validate that all required fields are present.
        
        Raises:
            MissingRequiredFieldError: If required field is missing
        """
        for field in self.required_fields:
            if field not in config_data:
                examples = None
                if field == "model":
                    examples = self.common_models[:3]
                
                raise MissingRequiredFieldError(field, agent_file, examples)
    
    def validate_field_types(self, config_data: Dict[str, Any], agent_file: Path):
        """
        Validate field data types.
        
        Raises:
            InvalidFieldTypeError: If field has wrong type
        """
        for field, expected_type in self.field_types.items():
            if field in config_data:
                value = config_data[field]
                
                # Handle None values for optional fields
                if value is None and field not in self.required_fields:
                    continue
                
                # Check type
                if not isinstance(value, expected_type):
                    type_name = expected_type.__name__ if hasattr(expected_type, '__name__') else str(expected_type)
                    raise InvalidFieldTypeError(field, type_name, value, agent_file)
    
    def validate_model_name(self, model_name: str, agent_file: Path):
        """
        Validate model name format and suggest corrections.
        
        Raises:
            InvalidModelError: If model name appears invalid
        """
        # Basic format validation
        if not model_name or not isinstance(model_name, str):
            raise InvalidModelError("Model name cannot be empty", agent_file)
        
        # Check for provider prefix
        if '/' not in model_name:
            raise InvalidModelError(
                f"'{model_name}' missing provider prefix",
                agent_file,
                self.common_models
            )
        
        # Check for common typos
        provider, model = model_name.split('/', 1)
        
        if provider.lower() == 'openai' and provider != 'openai':
            raise InvalidModelError(
                f"Provider should be 'openai' (lowercase), got '{provider}'",
                agent_file,
                self.common_models
            )
        
        if provider.lower() == 'anthropic' and provider != 'anthropic':
            raise InvalidModelError(
                f"Provider should be 'anthropic' (lowercase), got '{provider}'",
                agent_file,
                self.common_models
            )
        
        # Warn about uncommon models (but don't fail)
        if model_name not in self.common_models:
            # This is just a warning, not an error
            print(f"Warning: Using uncommon model '{model_name}'. Verify it exists on OpenRouter.")
    
    def validate_tools(self, tools: List[str], agent_file: Path):
        """
        Validate tool names and existence.
        
        Raises:
            InvalidToolError: If tool doesn't exist
        """
        if not tools:
            return  # Empty tools list is valid
        
        for tool_name in tools:
            if not isinstance(tool_name, str):
                raise InvalidFieldTypeError("tools", "list of strings", tools, agent_file)
            
            if tool_name not in self.available_tools:
                raise InvalidToolError(tool_name, agent_file, self.available_tools)
            
            # Check if tool file actually exists and is valid
            tool_file = self.tools_dir / f"{tool_name}.py"
            if not tool_file.exists():
                raise InvalidToolError(
                    f"{tool_name} (file {tool_file} not found)",
                    agent_file,
                    self.available_tools
                )
    
    def validate_mcp_servers(self, mcp_servers: List[str], agent_file: Path):
        """
        Validate MCP server names.
        
        Raises:
            InvalidMCPServerError: If MCP server doesn't exist
        """
        if not mcp_servers:
            return  # Empty MCP list is valid
        
        for server_name in mcp_servers:
            if not isinstance(server_name, str):
                raise InvalidFieldTypeError("mcp", "list of strings", mcp_servers, agent_file)
            
            if server_name not in self.available_mcp_servers:
                raise InvalidMCPServerError(server_name, agent_file, self.available_mcp_servers)
    
    def validate_numeric_ranges(self, config_data: Dict[str, Any], agent_file: Path):
        """
        Validate numeric parameter ranges.
        
        Raises:
            InvalidFieldTypeError: If numeric values are out of valid range
        """
        validations = {
            "temperature": (0.0, 2.0, "Temperature must be between 0.0 and 2.0"),
            "top_p": (0.0, 1.0, "top_p must be between 0.0 and 1.0"),
            "presence_penalty": (-2.0, 2.0, "presence_penalty must be between -2.0 and 2.0"),
            "frequency_penalty": (-2.0, 2.0, "frequency_penalty must be between -2.0 and 2.0"),
            "max_tokens": (1, 100000, "max_tokens must be between 1 and 100000"),
            "timeout": (1.0, 300.0, "timeout must be between 1.0 and 300.0 seconds")
        }
        
        for field, (min_val, max_val, error_msg) in validations.items():
            if field in config_data and config_data[field] is not None:
                value = config_data[field]
                if not (min_val <= value <= max_val):
                    raise InvalidFieldTypeError(
                        field,
                        f"number between {min_val} and {max_val}",
                        value,
                        agent_file
                    )
    
    def validate_complete_config(self, agent_file: Path) -> Dict[str, Any]:
        """
        Perform complete validation of an agent configuration file.
        
        Returns:
            Validated configuration dictionary
        
        Raises:
            Various AgentConfigError subclasses for specific validation failures
        """
        # Step 1: Validate file format
        yaml_content, system_prompt = self.validate_agent_file_format(agent_file)
        
        # Step 2: Parse YAML
        config_data = self.validate_yaml_frontmatter(yaml_content, agent_file)
        
        # Step 3: Validate required fields
        self.validate_required_fields(config_data, agent_file)
        
        # Step 4: Validate field types
        self.validate_field_types(config_data, agent_file)
        
        # Step 5: Validate model name
        self.validate_model_name(config_data["model"], agent_file)
        
        # Step 6: Validate tools
        if "tools" in config_data:
            self.validate_tools(config_data["tools"], agent_file)
        
        # Step 7: Validate MCP servers
        if "mcp" in config_data:
            self.validate_mcp_servers(config_data["mcp"], agent_file)
        
        # Step 8: Validate numeric ranges
        self.validate_numeric_ranges(config_data, agent_file)
        
        # Step 9: Add system prompt to config
        config_data["system_prompt"] = system_prompt
        
        return config_data


def validate_template_includes(system_prompt: str, snippets_dir: Path, agent_file: Path):
    """
    Validate that all template includes exist and are accessible.
    
    Raises:
        TemplateProcessingError: If include files are missing or invalid
    """
    # Find all include statements
    include_pattern = r'{%\s*include\s+["\']([^"\']+)["\']\s*%}'
    includes = re.findall(include_pattern, system_prompt)
    
    for include_file in includes:
        include_path = snippets_dir / include_file
        
        if not include_path.exists():
            raise TemplateProcessingError(
                f"Include file '{include_file}' not found",
                agent_file,
                include_file=include_file
            )
        
        # Check if file is readable
        try:
            include_path.read_text(encoding='utf-8')
        except Exception as e:
            raise TemplateProcessingError(
                f"Cannot read include file '{include_file}': {e}",
                agent_file,
                include_file=include_file
            ) 