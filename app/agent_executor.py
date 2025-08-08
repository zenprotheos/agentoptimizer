"""
Agent execution engine module.
Handles the core execution logic, multimodal processing, and response formatting.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits
from pydantic_ai.messages import ToolCallPart

from app.agent_config import AgentConfig
from app.agent_tools import AgentToolManager
from app.run_persistence import RunPersistence
from app.tool_services import helper as tool_services
from app.agent_errors import MultimodalProcessingError, MultimodalFileError, MultimodalURLError, MultimodalCapabilityError


class AgentExecutor:
    """Handles agent execution with multimodal support and comprehensive error handling"""
    
    def __init__(self, config: Dict[str, Any], run_persistence: RunPersistence, debug: bool = False):
        self.config = config
        self.run_persistence = run_persistence
        self.debug = debug
    
    def _process_multimodal_inputs(self, files: List[str] = None, urls: List[str] = None) -> Tuple[bool, Any]:
        """Process inputs and determine if multimodal handling is needed"""
        if not files and not urls:
            return False, None
            
        # Lazy import to avoid loading multimodal dependencies unless needed
        try:
            from app.multimodal_processor import MultimodalProcessor
        except ImportError as e:
            if self.debug:
                print(f"Multimodal processor not available - falling back to text processing: {e}")
            return False, None
        
        try:
            processor = MultimodalProcessor(self.config, self.debug)
            
            if processor.should_use_multimodal(files or [], urls or []):
                result = processor.process_inputs(files, urls)
                return True, result
            else:
                # Fall back to existing text processing
                return False, None
        except MultimodalCapabilityError as e:
            # Capability errors are non-fatal - fall back to text processing
            if self.debug:
                print(f"Multimodal capability error - falling back to text processing: {e}")
            return False, None
        except (MultimodalFileError, MultimodalURLError) as e:
            # These are user errors that should be reported
            raise e
    
    def _create_openrouter_model(self, config: AgentConfig) -> OpenAIModel:
        """Create OpenRouter model with validation"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        try:
            return OpenAIModel(
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
                raise ValueError(f"Model '{config.model}' not found on OpenRouter. Check https://openrouter.ai/models for available models.")
            elif "401" in model_error or "unauthorized" in model_error.lower():
                raise ValueError("OpenRouter API authentication failed. Check your OPENROUTER_API_KEY.")
            else:
                raise ValueError(f"Failed to initialize model '{config.model}': {e}")
    
    def _create_model_settings(self, config: AgentConfig) -> ModelSettings:
        """Create model settings from agent config"""
        return ModelSettings(
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            top_p=config.top_p,
            presence_penalty=config.presence_penalty,
            frequency_penalty=config.frequency_penalty,
            timeout=config.timeout,
            stream=config.stream,
            parallel_tool_calls=True
        )
    
    def _create_usage_limits(self, config: AgentConfig) -> UsageLimits:
        """Create usage limits from config"""
        default_request_limit = self.config.get('usage_limits', {}).get('request_limit', 50)
        agent_request_limit = config.request_limit if config.request_limit is not None else default_request_limit
        
        return UsageLimits(
            request_limit=agent_request_limit,
            request_tokens_limit=self.config.get('usage_limits', {}).get('request_tokens_limit'),
            response_tokens_limit=self.config.get('usage_limits', {}).get('response_tokens_limit'),
            total_tokens_limit=self.config.get('usage_limits', {}).get('total_tokens_limit')
        )
    
    def _extract_tool_call_summary(self, messages) -> List[str]:
        """Simple tool call summary - much lighter than full extraction"""
        tool_calls = []
        for message in messages:
            if hasattr(message, 'parts') and message.parts:
                for part in message.parts:
                    if isinstance(part, ToolCallPart):
                        tool_calls.append(part.tool_name)
        
        return list(set(tool_calls))  # Unique tool names used
    
    def _append_files_to_message(self, message: str, files: List[str] = None, urls: List[str] = None) -> str:
        """Append file information to message when agent has no template-based file handling"""
        if not files and not urls:
            return message
        
        # Build the file list
        file_list = []
        if files:
            file_list.extend(files)
        if urls:
            file_list.extend(urls)
        
        if not file_list:
            return message
        
        # Append file information to the message
        appended_message = message + "\n\nProvided files:\n"
        for filepath in file_list:
            appended_message += f"- {filepath}\n"
        
        return appended_message
    
    def _handle_execution_error(self, e: Exception, run_id: str = None, config: 'AgentConfig' = None) -> Dict[str, Any]:
        """Handle execution errors with specific messaging and intelligent recovery strategies"""
        from pydantic_ai.exceptions import UsageLimitExceeded, UnexpectedModelBehavior
        from .agent_errors import LLMAPIError
        from pathlib import Path
        
        # Handle multimodal-specific errors first
        if isinstance(e, MultimodalProcessingError):
            return {
                "output": "",
                "success": False,
                "run_id": run_id,
                "error": f"Multimodal Processing Error: {e.get_formatted_message()}",
                "error_type": "multimodal_error",
                "multimodal_error_type": type(e).__name__
            }
        
        if isinstance(e, UsageLimitExceeded):
            return {
                "output": "",
                "success": False,
                "run_id": run_id,
                "error": f"Agent reached usage limit: {e}\n"
                        f"The agent exceeded its configured limits to prevent infinite loops or excessive costs.\n"
                        f"Consider increasing the request_limit in the agent's configuration if this task requires more iterations.",
                "error_type": "usage_limit_exceeded",
                "usage_limit_type": "request_limit" if "request_limit" in str(e) else "token_limit"
            }
        
        # Handle LLM API errors with enhanced context and recovery strategies
        error_message = str(e)
        is_llm_error = any(indicator in error_message.lower() for indicator in [
            "openai", "anthropic", "google", "chat completion", "finish_reason", 
            "pydantic", "validation error", "rate limit", "token", "model", "api"
        ]) or isinstance(e, UnexpectedModelBehavior)
        
        if is_llm_error:
            # Determine run directory for context
            run_directory = None
            if run_id:
                run_directory = Path(f"runs/{run_id}")
            
            # Create enhanced LLM error with recovery strategies
            agent_file = Path(f"agents/{config.name}.md") if config else None
            llm_error = LLMAPIError(
                original_error=e,
                run_id=run_id,
                run_directory=run_directory,
                agent_file=agent_file
            )
            
            return {
                "output": "",
                "success": False,
                "run_id": run_id,
                "error": llm_error.get_formatted_message(),
                "error_type": "llm_api_error",
                "recovery_suggestions": llm_error.suggestions,
                "original_error": error_message
            }
        
        # Handle common MCP server errors with helpful messages
        if "401 Unauthorized" in error_message:
            return {
                "output": "",
                "success": False,
                "run_id": run_id,
                "error": f"MCP server authentication failed: {e}\n"
                        f"This usually means the MCP server requires authentication credentials.\n"
                        f"Check your MCP server configuration for missing API keys or tokens."
            }
        elif "Connection" in error_message or "timeout" in error_message.lower():
            return {
                "output": "",
                "success": False,
                "run_id": run_id,
                "error": f"MCP server connection failed: {e}\n"
                        f"Check that the MCP server is running and accessible."
            }
        else:
            return {
                "output": "",
                "success": False,
                "run_id": run_id,
                "error": f"Agent execution failed: {e}"
            }
    
    async def execute_agent(self, config: AgentConfig, tool_manager: AgentToolManager, 
                          message: str, files: List[str] = None, urls: List[str] = None, 
                          run_id: Optional[str] = None, message_history: List = None,
                          is_new_run: bool = True) -> Dict[str, Any]:
        """Execute an agent with the given configuration and inputs"""
        
        # Check for multimodal inputs first
        try:
            is_multimodal, multimodal_result = self._process_multimodal_inputs(files, urls)
        except MultimodalProcessingError as e:
            return self._handle_execution_error(e, run_id, config)
        
        try:
            # Create model and settings
            model = self._create_openrouter_model(config)
            model_settings = self._create_model_settings(config)
            usage_limits = self._create_usage_limits(config)
            
            # Load tools and MCP servers
            tool_functions = tool_manager.create_tool_functions(config.tools)
            mcp_servers = []
            if config.mcp:
                mcp_servers = await tool_manager.create_mcp_servers(config.mcp)
            
            # Handle multimodal system prompt modification
            system_prompt = config.system_prompt
            if is_multimodal and multimodal_result.text_context:
                # Inject multimodal text context into system prompt
                from app.agent_template_processor import AgentTemplateProcessor
                template_processor = AgentTemplateProcessor(
                    Path.cwd(), 
                    self.config.get('template_engine', {}), 
                    tool_services, 
                    self.debug
                )
                
                system_prompt = await template_processor._render_system_prompt(
                    config.system_prompt, 
                    multimodal_result.text_context
                )
            
            # Create agent
            if mcp_servers:
                agent = Agent(
                    model=model,
                    system_prompt=system_prompt,
                    tools=tool_functions if tool_functions else [],
                    model_settings=model_settings,
                    mcp_servers=mcp_servers
                )
            else:
                agent = Agent(
                    model=model,
                    system_prompt=system_prompt,
                    tools=tool_functions if tool_functions else [],
                    model_settings=model_settings
                )
            
            # Set run ID in tool helper for file organization
            tool_services.set_run_id(run_id)
            
            # Handle message appending for agents without template-based file handling
            final_message = message
            if config.template_strategy == 'message_append' and (files or urls):
                final_message = self._append_files_to_message(message, files, urls)
                if self.debug:
                    print(f"Agent has no file template variables, appending files to message")
            
            # Run the agent with message history
            if is_multimodal:
                # Use multimodal message construction
                message_parts = multimodal_result.create_message_parts(final_message)
                if mcp_servers:
                    async with agent.run_mcp_servers():
                        result = await agent.run(message_parts, message_history=message_history, usage_limits=usage_limits)
                else:
                    result = await agent.run(message_parts, message_history=message_history, usage_limits=usage_limits)
            else:
                # Use existing text-based flow
                if mcp_servers:
                    async with agent.run_mcp_servers():
                        result = await agent.run(final_message, message_history=message_history, usage_limits=usage_limits)
                else:
                    result = await agent.run(final_message, message_history=message_history, usage_limits=usage_limits)
            
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
            return self._handle_execution_error(e, run_id, config) 