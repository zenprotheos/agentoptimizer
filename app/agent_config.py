"""
Agent configuration management module.
Handles parsing, validation, and processing of agent configuration data.
"""

from typing import Dict, Any, List
from pathlib import Path
from app.agent_template_processor import AgentTemplateProcessor
from app.agent_validation import AgentConfigValidator
from app.agent_errors import AgentConfigError


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
        self.request_limit = config_data.get('request_limit')  # Per-agent override for usage limits


class AgentConfigManager:
    """Manages agent configuration parsing and validation"""
    
    def __init__(self, project_root: Path, config: Dict[str, Any], 
                 template_processor: AgentTemplateProcessor, 
                 validator: AgentConfigValidator, debug: bool = False):
        self.project_root = project_root
        self.config = config
        self.template_processor = template_processor
        self.validator = validator
        self.debug = debug
    
    async def parse_agent_config(self, agent_file: Path, files: List[str] = None) -> AgentConfig:
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