#!/usr/bin/env python3
"""
Agent Configuration Error Classes
Provides specific, actionable error messages for common agent configuration mistakes.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path


class AgentConfigError(Exception):
    """Base class for agent configuration errors"""
    
    def __init__(self, message: str, agent_file: Optional[Path] = None, suggestions: Optional[List[str]] = None):
        self.message = message
        self.agent_file = agent_file
        self.suggestions = suggestions or []
        super().__init__(self.get_formatted_message())
    
    def get_formatted_message(self) -> str:
        """Get a formatted error message with suggestions"""
        msg = self.message
        
        if self.agent_file:
            msg = f"Agent '{self.agent_file.stem}': {msg}"
        
        if self.suggestions:
            msg += "\n\nSuggestions:"
            for suggestion in self.suggestions:
                msg += f"\n  • {suggestion}"
        
        return msg


class YAMLFrontmatterError(AgentConfigError):
    """Errors related to YAML frontmatter parsing"""
    
    def __init__(self, message: str, agent_file: Optional[Path] = None, yaml_content: Optional[str] = None, line_number: Optional[int] = None):
        self.yaml_content = yaml_content
        self.line_number = line_number
        
        # Add line number context if available
        if line_number and yaml_content:
            lines = yaml_content.split('\n')
            if 0 <= line_number - 1 < len(lines):
                message += f"\n  Problem line {line_number}: {lines[line_number - 1].strip()}"
        
        suggestions = [
            "Check that YAML frontmatter is enclosed in '---' lines",
            "Ensure proper YAML indentation (use spaces, not tabs)",
            "Validate YAML syntax using an online YAML validator",
            "Check for missing colons after field names",
            "Ensure list items start with '- ' (dash followed by space)"
        ]
        
        super().__init__(message, agent_file, suggestions)


class MissingRequiredFieldError(AgentConfigError):
    """Error for missing required fields in agent configuration"""
    
    def __init__(self, field_name: str, agent_file: Optional[Path] = None, valid_examples: Optional[List[str]] = None):
        message = f"Missing required field '{field_name}' in YAML frontmatter"
        
        suggestions = [f"Add '{field_name}' field to your agent's YAML frontmatter"]
        
        if valid_examples:
            suggestions.append(f"Valid {field_name} examples: {', '.join(valid_examples)}")
        
        if field_name == "name":
            suggestions.extend([
                "The 'name' field should match your agent filename (without .md extension)",
                "Example: name: web_agent"
            ])
        elif field_name == "description":
            suggestions.extend([
                "Provide a clear description of what your agent does",
                "Example: description: \"Searches the web and reads web pages\""
            ])
        elif field_name == "model":
            suggestions.extend([
                "Specify the LLM model to use",
                "Example: model: \"openai/gpt-4o-mini\""
            ])
        
        super().__init__(message, agent_file, suggestions)


class InvalidModelError(AgentConfigError):
    """Error for invalid or non-existent model names"""
    
    def __init__(self, model_name: str, agent_file: Optional[Path] = None, available_models: Optional[List[str]] = None):
        message = f"Invalid model name '{model_name}'"
        
        suggestions = []
        
        # Common model name corrections
        common_corrections = {
            "gpt-4": "openai/gpt-4o",
            "gpt-4-mini": "openai/gpt-4o-mini", 
            "gpt-3.5": "openai/gpt-3.5-turbo",
            "claude": "anthropic/claude-3-sonnet",
            "claude-3": "anthropic/claude-3-sonnet",
        }
        
        if model_name.lower() in common_corrections:
            suggestions.append(f"Did you mean '{common_corrections[model_name.lower()]}'?")
        
        # Check for common typos
        if "gpt" in model_name.lower() and "openai/" not in model_name:
            suggestions.append(f"OpenAI models need 'openai/' prefix. Try 'openai/{model_name}'")
        
        if "claude" in model_name.lower() and "anthropic/" not in model_name:
            suggestions.append(f"Anthropic models need 'anthropic/' prefix. Try 'anthropic/{model_name}'")
        
        suggestions.extend([
            "Check OpenRouter.ai for available models",
            "Common models: openai/gpt-4o-mini, openai/gpt-4o, anthropic/claude-3-sonnet",
            "Ensure model name includes provider prefix (e.g., 'openai/', 'anthropic/')"
        ])
        
        if available_models:
            suggestions.append(f"Available models: {', '.join(available_models[:5])}...")
        
        super().__init__(message, agent_file, suggestions)


class InvalidToolError(AgentConfigError):
    """Error for invalid or non-existent tools"""
    
    def __init__(self, tool_name: str, agent_file: Optional[Path] = None, available_tools: Optional[List[str]] = None):
        message = f"Tool '{tool_name}' not found"
        
        suggestions = []
        
        # Check for common typos
        if available_tools:
            # Simple fuzzy matching for suggestions
            close_matches = [t for t in available_tools if self._is_similar(tool_name, t)]
            if close_matches:
                suggestions.append(f"Did you mean: {', '.join(close_matches[:3])}?")
        
        suggestions.extend([
            f"Check that '{tool_name}.py' exists in the tools directory",
            "Ensure tool name matches the filename exactly (case-sensitive)",
            "Verify the tool file has proper structure with TOOL_METADATA and main function"
        ])
        
        if available_tools:
            suggestions.append(f"Available tools: {', '.join(sorted(available_tools))}")
        
        super().__init__(message, agent_file, suggestions)
    
    def _is_similar(self, name1: str, name2: str) -> bool:
        """Conservative similarity check for typo detection"""
        # Only suggest if one is a substring of the other (for obvious typos)
        if len(name1) >= 4 and len(name2) >= 4:
            if name1.lower() in name2.lower() or name2.lower() in name1.lower():
                return True
        
        # Only suggest for single character differences in same-length names
        if len(name1) == len(name2) and len(name1) >= 5:
            diff_count = sum(c1 != c2 for c1, c2 in zip(name1.lower(), name2.lower()))
            return diff_count == 1  # Only single character differences
        
        return False


class InvalidMCPServerError(AgentConfigError):
    """Error for invalid or non-existent MCP servers"""
    
    def __init__(self, server_name: str, agent_file: Optional[Path] = None, available_servers: Optional[List[str]] = None):
        message = f"MCP server '{server_name}' not found in configuration"
        
        suggestions = []
        
        # Check for common typos
        if available_servers:
            close_matches = [s for s in available_servers if self._is_similar(server_name, s)]
            if close_matches:
                suggestions.append(f"Did you mean: {', '.join(close_matches[:3])}?")
        
        suggestions.extend([
            "Check your MCP server configuration in .cursor/mcp.json",
            "Ensure server name matches exactly (case-sensitive unless case_insensitive_matching is enabled)",
            "Verify the MCP server is properly installed and configured"
        ])
        
        if available_servers:
            suggestions.append(f"Available MCP servers: {', '.join(sorted(available_servers))}")
        
        super().__init__(message, agent_file, suggestions)
    
    def _is_similar(self, name1: str, name2: str) -> bool:
        """Conservative similarity check for typo detection"""
        # Only suggest if one is a substring of the other and both are reasonably long
        if len(name1) >= 4 and len(name2) >= 4:
            return name1.lower() in name2.lower() or name2.lower() in name1.lower()
        return False


class TemplateProcessingError(AgentConfigError):
    """Error for template processing issues"""
    
    def __init__(self, message: str, agent_file: Optional[Path] = None, template_line: Optional[int] = None, include_file: Optional[str] = None):
        self.template_line = template_line
        self.include_file = include_file
        
        if template_line:
            message += f" (line {template_line})"
        
        suggestions = []
        
        if "include" in message.lower() and include_file:
            suggestions.extend([
                f"Check that '{include_file}' exists in the snippets directory",
                "Ensure include file has the correct extension (.md)",
                "Verify include syntax: {% include \"filename.md\" %}",
                "Check file path is relative to snippets directory"
            ])
        
        suggestions.extend([
            "Validate Jinja2 template syntax",
            "Check for unmatched braces {{ }} or {% %}",
            "Ensure variable names are spelled correctly"
        ])
        
        super().__init__(message, agent_file, suggestions)


class InvalidFieldTypeError(AgentConfigError):
    """Error for fields with incorrect data types"""
    
    def __init__(self, field_name: str, expected_type: str, actual_value: Any, agent_file: Optional[Path] = None):
        message = f"Field '{field_name}' must be {expected_type}, got {type(actual_value).__name__}: {actual_value}"
        
        suggestions = []
        
        if field_name == "tools" and not isinstance(actual_value, list):
            suggestions.extend([
                "The 'tools' field must be a list",
                "Example: tools:\n  - web_search\n  - file_creator",
                "If you have only one tool, still use list format: tools:\n  - tool_name"
            ])
        elif field_name == "mcp" and not isinstance(actual_value, list):
            suggestions.extend([
                "The 'mcp' field must be a list", 
                "Example: mcp:\n  - server_name\n  - another_server",
                "If you have only one server, still use list format: mcp:\n  - server_name"
            ])
        elif field_name in ["temperature", "max_tokens", "top_p"] and not isinstance(actual_value, (int, float)):
            suggestions.extend([
                f"The '{field_name}' field must be a number",
                f"Example: {field_name}: 0.7" if field_name == "temperature" else f"Example: {field_name}: 2048"
            ])
        
        super().__init__(message, agent_file, suggestions)


class AgentFileFormatError(AgentConfigError):
    """Error for incorrect agent file format"""
    
    def __init__(self, message: str, agent_file: Optional[Path] = None):
        suggestions = [
            "Agent files must follow this format:",
            "---",
            "name: agent_name",
            "description: \"Agent description\"",
            "model: \"openai/gpt-4o-mini\"",
            "tools:",
            "  - tool1",
            "  - tool2",
            "---",
            "",
            "# Agent system prompt content here...",
            "",
            "Ensure there are exactly three dashes (---) before and after the YAML frontmatter"
        ]
        
        super().__init__(message, agent_file, suggestions) 