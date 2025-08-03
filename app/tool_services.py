# app/tool_services.py
"""
This module provides a helpful set of capabillities that are commonly used by agent tools. It can be imported into a new tool so that code can be kept DRY. Changes to this module should trigger updates to the how_to_use_tool_services guide.
"""

import os
import json
import yaml
import requests
import asyncio
import re
import ast
import time
import threading
from pathlib import Path
from typing import Dict, Any, Union, Optional, List, Type
from datetime import datetime
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
import tiktoken
import functools
import inspect

# Pydantic AI imports
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits
from dotenv import load_dotenv

# Logfire import
try:
    import logfire
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    # Create a no-op logfire mock
    class MockLogfire:
        def instrument(self, name):
            return lambda func: func
        def span(self, name, **kwargs):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def info(self, *args, **kwargs):
            pass
        def error(self, *args, **kwargs):
            pass
        def configure(self, **kwargs):
            pass
    logfire = MockLogfire()

# Load environment variables from .env file
load_dotenv()

def auto_instrument(operation_type: str):
    """Decorator that automatically adds Logfire instrumentation to methods"""
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not LOGFIRE_AVAILABLE or not hasattr(logfire, '_configured'):
                return func(*args, **kwargs)
            
            # Extract method name and relevant parameters for logging
            func_name = func.__name__
            span_name = f"tool_services.{operation_type}.{func_name}"
            
            # Create span attributes from function signature
            span_attrs = {}
            try:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Add safe parameters to span (avoid logging sensitive data)
                for param_name, param_value in bound_args.arguments.items():
                    if param_name in ['self', 'cls']:
                        continue
                    if param_name in ['prompt', 'content'] and isinstance(param_value, str):
                        # Log only first 100 chars of text content
                        span_attrs[param_name] = param_value[:100] + "..." if len(param_value) > 100 else param_value
                    elif param_name == 'model':
                        span_attrs['model'] = param_value
                    elif param_name in ['filename', 'filepath', 'description', 'url', 'method']:
                        span_attrs[param_name] = str(param_value)
                    elif param_name in ['temperature', 'max_tokens', 'run_id']:
                        span_attrs[param_name] = param_value
            except Exception:
                # If signature inspection fails, continue without detailed params
                pass
            
            with logfire.span(span_name, **span_attrs) as span:
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful completion with relevant metrics
                    if operation_type == 'llm' and isinstance(result, str):
                        logfire.info(f"{func_name} completed", 
                                   response_length=len(result),
                                   operation=operation_type)
                    elif operation_type == 'file' and isinstance(result, dict):
                        logfire.info(f"{func_name} completed",
                                   filepath=result.get('filepath'),
                                   tokens=result.get('frontmatter', {}).get('tokens'),
                                   operation=operation_type)
                    elif operation_type == 'api' and hasattr(result, 'status_code'):
                        logfire.info(f"{func_name} completed",
                                   status_code=result.status_code,
                                   operation=operation_type)
                    else:
                        logfire.info(f"{func_name} completed", operation=operation_type)
                    
                    return result
                except Exception as e:
                    logfire.error(f"{func_name} failed", 
                                error=str(e), 
                                error_type=type(e).__name__,
                                operation=operation_type)
                    raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not LOGFIRE_AVAILABLE or not hasattr(logfire, '_configured'):
                return await func(*args, **kwargs)
            
            # Extract method name and relevant parameters for logging
            func_name = func.__name__
            span_name = f"tool_services.{operation_type}.{func_name}"
            
            # Create span attributes from function signature
            span_attrs = {}
            try:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Add safe parameters to span (avoid logging sensitive data)
                for param_name, param_value in bound_args.arguments.items():
                    if param_name in ['self', 'cls']:
                        continue
                    if param_name in ['prompt', 'content'] and isinstance(param_value, str):
                        # Log only first 100 chars of text content
                        span_attrs[param_name] = param_value[:100] + "..." if len(param_value) > 100 else param_value
                    elif param_name == 'model':
                        span_attrs['model'] = param_value
                    elif param_name in ['filename', 'filepath', 'description', 'url', 'method']:
                        span_attrs[param_name] = str(param_value)
                    elif param_name in ['temperature', 'max_tokens', 'run_id']:
                        span_attrs[param_name] = param_value
            except Exception:
                # If signature inspection fails, continue without detailed params
                pass
            
            with logfire.span(span_name, **span_attrs) as span:
                try:
                    result = await func(*args, **kwargs)
                    
                    # Log successful completion with relevant metrics
                    if operation_type == 'llm' and isinstance(result, str):
                        logfire.info(f"{func_name} completed", 
                                   response_length=len(result),
                                   operation=operation_type)
                    elif operation_type == 'file' and isinstance(result, dict):
                        logfire.info(f"{func_name} completed",
                                   filepath=result.get('filepath'),
                                   tokens=result.get('frontmatter', {}).get('tokens'),
                                   operation=operation_type)
                    else:
                        logfire.info(f"{func_name} completed", operation=operation_type)
                    
                    return result
                except Exception as e:
                    logfire.error(f"{func_name} failed", 
                                error=str(e), 
                                error_type=type(e).__name__,
                                operation=operation_type)
                    raise
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ToolHelper:
    """Lightweight helper for tools using Pydantic AI - can be imported independently"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize with minimal config loading"""
        self.config = self._load_config()
        self._setup_clients()
        self._setup_pydantic_ai()
        self._setup_logfire()
    
    def _load_config(self):
        """Load config with sensible defaults"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _setup_logfire(self):
        """Setup Logfire if available and not already configured"""
        if not LOGFIRE_AVAILABLE:
            return
            
        # Check if already configured by agent_runner
        if hasattr(logfire, '_configured'):
            return
            
        logfire_config = self.config.get('logfire', {})
        
        if not logfire_config.get('enabled', True) or not os.getenv('LOGFIRE_WRITE_TOKEN'):
            return
        
        try:
            logfire.configure(
                service_name=logfire_config.get('service_name', 'oneshot-tools'),
                service_version='1.0.0',
                environment=os.getenv('ENVIRONMENT', 'development'),
            )
            
            # Mark as configured to avoid double configuration
            logfire._configured = True
            
        except Exception as e:
            print(f"Warning: Failed to initialize Logfire in tool_services: {e}")
    
    def _setup_clients(self):
        """Setup internal clients"""
        self.artifacts_base_dir = Path(__file__).parent.parent / "artifacts"
        self.artifacts_base_dir.mkdir(exist_ok=True)
        
        # Current run ID for file organization (will be set by tools)
        self._current_run_id = None
        
        # Setup template engine
        snippets_dir = Path(__file__).parent.parent / "snippets"
        snippets_dir.mkdir(exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader([str(snippets_dir)]))
    
    def _setup_pydantic_ai(self):
        """Setup Pydantic AI model and settings"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        # Get model settings from config
        model_settings = self.config.get('model_settings', {})
        
        # Create OpenRouter model
        self.model = OpenAIModel(
            model_name=model_settings.get('model', 'openai/gpt-4o-mini'),
            provider=OpenAIProvider(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
        )
        
        # Create model settings
        self.model_settings = ModelSettings(
            temperature=model_settings.get('temperature', 0.7),
            max_tokens=model_settings.get('max_tokens', 2048),
            top_p=model_settings.get('top_p'),
            presence_penalty=model_settings.get('presence_penalty'),
            frequency_penalty=model_settings.get('frequency_penalty'),
            timeout=model_settings.get('timeout', 30.0),
            parallel_tool_calls=model_settings.get('parallel_tool_calls', True)
        )
        
        # Create usage limits
        usage_limits_config = self.config.get('usage_limits', {})
        self.usage_limits = UsageLimits(
            request_limit=usage_limits_config.get('request_limit', 15),
            request_tokens_limit=usage_limits_config.get('request_tokens_limit'),
            response_tokens_limit=usage_limits_config.get('response_tokens_limit'),
            total_tokens_limit=usage_limits_config.get('total_tokens_limit')
        )
    
    def _get_builtin_variables(self) -> Dict[str, Any]:
        """Generate built-in template variables available to all tools (same as agent system)"""
        from datetime import datetime
        
        now = datetime.now()
        
        return {
            'current_timestamp': now.isoformat(),
            'current_date': now.strftime('%Y-%m-%d'),
            'current_time': now.strftime('%H:%M:%S'),
            'current_datetime_friendly': now.strftime('%A, %B %d, %Y at %I:%M %p'),
            'current_unix_timestamp': int(now.timestamp()),
            'working_directory': str(Path.cwd()),
            'user_home': str(Path.home()),
            'project_root': str(Path(__file__).parent.parent),
        }
    
    def _expand_system_prompt_with_builtins(self, system_prompt: str) -> str:
        """Expand system prompt with built-in variables using Jinja2 template rendering"""
        if not system_prompt:
            return system_prompt
            
        try:
            # Get built-in variables
            builtin_vars = self._get_builtin_variables()
            
            # Use Jinja2 to render the system prompt with built-in variables
            template = self.jinja_env.from_string(system_prompt)
            return template.render(**builtin_vars)
        except Exception as e:
            # If template rendering fails, return original prompt
            print(f"Warning: Failed to expand system prompt with built-ins: {e}")
            return system_prompt
    
    # ULTRA-MINIMAL LLM CALLING using Pydantic AI
    @auto_instrument('llm')
    def llm(self, prompt: str, model: str = None, system_prompt: str = None, **kwargs) -> str:
        """Ultra-simple LLM call using Pydantic AI"""
        return asyncio.run(self._llm_async(prompt, model, system_prompt, **kwargs))
    
    @auto_instrument('llm')
    async def _llm_async(self, prompt: str, model: str = None, system_prompt: str = None, **kwargs) -> str:
        """Async LLM call using Pydantic AI"""
        # Override model if specified
        current_model = self.model
        if model:
            current_model = OpenAIModel(
                model_name=model,
                provider=OpenAIProvider(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv('OPENROUTER_API_KEY')
                )
            )
        
        # Override model settings if specified
        current_settings = self.model_settings
        if kwargs:
            settings_dict = {
                'temperature': kwargs.get('temperature', current_settings.temperature),
                'max_tokens': kwargs.get('max_tokens', current_settings.max_tokens),
                'top_p': kwargs.get('top_p', current_settings.top_p),
                'presence_penalty': kwargs.get('presence_penalty', current_settings.presence_penalty),
                'frequency_penalty': kwargs.get('frequency_penalty', current_settings.frequency_penalty),
                'timeout': kwargs.get('timeout', current_settings.timeout),
                'parallel_tool_calls': current_settings.parallel_tool_calls
            }
            current_settings = ModelSettings(**{k: v for k, v in settings_dict.items() if v is not None})
        
        # Expand system prompt with built-in variables
        expanded_system_prompt = self._expand_system_prompt_with_builtins(
            system_prompt or "You are a helpful assistant."
        )
        
        # Create a simple agent for this call
        agent = Agent(
            model=current_model,
            system_prompt=expanded_system_prompt,
            model_settings=current_settings
        )
        
        # Run the agent
        result = await agent.run(prompt, usage_limits=self.usage_limits)
        return str(result.output)
    
    @auto_instrument('llm')
    def llm_json(self, prompt: str, model: str = None, **kwargs) -> Dict:
        """LLM call that returns parsed JSON using Pydantic AI"""
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        response = self.llm(json_prompt, model, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "raw_response": response}
    
    @auto_instrument('llm')
    def llm_structured(self, prompt: str, pydantic_model: Type[BaseModel], model: str = None, **kwargs):
        """LLM call with structured output using Pydantic AI"""
        return asyncio.run(self._llm_structured_async(prompt, pydantic_model, model, **kwargs))
    
    @auto_instrument('llm')
    async def _llm_structured_async(self, prompt: str, pydantic_model: Type[BaseModel], model: str = None, **kwargs):
        """Async structured LLM call using Pydantic AI"""
        # Override model if specified
        current_model = self.model
        if model:
            current_model = OpenAIModel(
                model_name=model,
                provider=OpenAIProvider(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv('OPENROUTER_API_KEY')
                )
            )
        
        # Override model settings if specified
        current_settings = self.model_settings
        if kwargs:
            settings_dict = {
                'temperature': kwargs.get('temperature', current_settings.temperature),
                'max_tokens': kwargs.get('max_tokens', current_settings.max_tokens),
                'top_p': kwargs.get('top_p', current_settings.top_p),
                'presence_penalty': kwargs.get('presence_penalty', current_settings.presence_penalty),
                'frequency_penalty': kwargs.get('frequency_penalty', current_settings.frequency_penalty),
                'timeout': kwargs.get('timeout', current_settings.timeout),
                'parallel_tool_calls': current_settings.parallel_tool_calls
            }
            current_settings = ModelSettings(**{k: v for k, v in settings_dict.items() if v is not None})
        
        # Expand system prompt with built-in variables
        expanded_system_prompt = self._expand_system_prompt_with_builtins(
            "You are a helpful assistant. Respond with structured data matching the required format."
        )
        
        # Create agent with structured response
        agent = Agent(
            model=current_model,
            result_type=pydantic_model,
            system_prompt=expanded_system_prompt,
            model_settings=current_settings
        )
        
        # Run the agent
        result = await agent.run(prompt, usage_limits=self.usage_limits)
        return result.output
    
    # CHAIN PROMPTS - using Pydantic AI conversation capabilities
    @auto_instrument('llm')
    def chain_prompts(self, prompts: List[str], model: str = None, system_prompt: str = None, **kwargs) -> List[str]:
        """Chain multiple prompts together using Pydantic AI conversation"""
        return asyncio.run(self._chain_prompts_async(prompts, model, system_prompt, **kwargs))
    
    @auto_instrument('llm')
    async def _chain_prompts_async(self, prompts: List[str], model: str = None, system_prompt: str = None, **kwargs) -> List[str]:
        """Async prompt chaining"""
        # Override model if specified
        current_model = self.model
        if model:
            current_model = OpenAIModel(
                model_name=model,
                provider=OpenAIProvider(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv('OPENROUTER_API_KEY')
                )
            )
        
        # Override model settings if specified
        current_settings = self.model_settings
        if kwargs:
            settings_dict = {
                'temperature': kwargs.get('temperature', current_settings.temperature),
                'max_tokens': kwargs.get('max_tokens', current_settings.max_tokens),
                'top_p': kwargs.get('top_p', current_settings.top_p),
                'presence_penalty': kwargs.get('presence_penalty', current_settings.presence_penalty),
                'frequency_penalty': kwargs.get('frequency_penalty', current_settings.frequency_penalty),
                'timeout': kwargs.get('timeout', current_settings.timeout),
                'parallel_tool_calls': current_settings.parallel_tool_calls
            }
            current_settings = ModelSettings(**{k: v for k, v in settings_dict.items() if v is not None})
        
        # Expand system prompt with built-in variables
        expanded_system_prompt = self._expand_system_prompt_with_builtins(
            system_prompt or "You are a helpful assistant."
        )
        
        # Create agent for conversation
        agent = Agent(
            model=current_model,
            system_prompt=expanded_system_prompt,
            model_settings=current_settings
        )
        
        results = []
        conversation_history = []
        
        for prompt in prompts:
            # Run with conversation history
            result = await agent.run(prompt, usage_limits=self.usage_limits, message_history=conversation_history)
            response = str(result.output)
            results.append(response)
            
            # Update conversation history for next iteration
            conversation_history = result.all_messages()
        
        return results
    
    # RUN ID MANAGEMENT
    def set_run_id(self, run_id: str):
        """Set the current run ID for file organization and todo tools"""
        self._current_run_id = run_id
        # Set environment variable for todo tools to access run context
        os.environ['ONESHOT_RUN_ID'] = run_id
    
    def get_run_id(self) -> Optional[str]:
        """Get the current run ID"""
        return self._current_run_id
    
    def _get_artifacts_dir(self) -> Path:
        """Get the artifacts directory for the current run"""
        if self._current_run_id:
            artifacts_dir = self.artifacts_base_dir / self._current_run_id
        else:
            # Fallback to base artifacts dir if no run ID is set
            artifacts_dir = self.artifacts_base_dir / "no_run_id"
        
        artifacts_dir.mkdir(exist_ok=True)
        return artifacts_dir
    
    # ULTRA-MINIMAL FILE OPERATIONS
    @auto_instrument('file')
    def read(self, filepath: str) -> str:
        """Read any file"""
        return Path(filepath).read_text()
    
    @auto_instrument('file')
    def read_for_llm(self, filepath: str, include_frontmatter: bool = False, frontmatter_only: bool = False) -> str:
        """Read file for LLM prompts with frontmatter handling options"""
        content = Path(filepath).read_text()
        
        if frontmatter_only:
            return self._extract_frontmatter(content)
        elif not include_frontmatter:
            return self._strip_frontmatter(content)
        else:
            return content
    
    def _extract_frontmatter(self, content: str) -> str:
        """Extract only the YAML frontmatter from content"""
        lines = content.split('\n')
        if lines and lines[0].strip() == '---':
            frontmatter_lines = ['---']
            for i, line in enumerate(lines[1:], 1):
                frontmatter_lines.append(line)
                if line.strip() == '---':
                    break
            return '\n'.join(frontmatter_lines)
        return ""
    
    def _strip_frontmatter(self, content: str) -> str:
        """Strip YAML frontmatter from content if present"""
        lines = content.split('\n')
        if lines and lines[0].strip() == '---':
            # Find the end of frontmatter
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    # Return content after frontmatter, skipping empty lines
                    remaining_lines = lines[i+1:]
                    while remaining_lines and not remaining_lines[0].strip():
                        remaining_lines.pop(0)
                    return '\n'.join(remaining_lines)
        return content
    
    @auto_instrument('file')
    def save(self, content: str, description: str = "", filename: str = None, add_frontmatter: bool = True) -> Dict[str, Any]:
        """Save content and return filepath + metadata (organized by run ID)"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_desc = description.lower().replace(' ', '_').replace('/', '_')[:50]
            filename = f"{timestamp}_{safe_desc}.md" if safe_desc else f"{timestamp}_output.md"
        
        # Get run-specific artifacts directory
        artifacts_dir = self._get_artifacts_dir()
        filepath = artifacts_dir / filename
        
        # Calculate tokens
        token_count = self._count_tokens(content)
        
        # Create summary (first 200 chars)
        summary = content[:200].replace('\n', ' ').strip()
        if len(content) > 200:
            summary += "..."
        
        # Add frontmatter if requested
        if add_frontmatter:
            final_content = f"""---
description: {description}
created: {datetime.now().isoformat()}
tokens: {token_count}
summary: {summary}
---

{content}"""
        else:
            final_content = content
        
        filepath.write_text(final_content)
        
        return {
            "filepath": str(filepath),
            "run_id": self._current_run_id,
            "artifacts_dir": str(artifacts_dir),
            "frontmatter": {
                "description": description,
                "created": datetime.now().isoformat(),
                "tokens": token_count,
                "summary": summary,
                "run_id": self._current_run_id
            }
        }
    
    @auto_instrument('file')
    def save_json(self, content: Union[Dict, List, str], description: str = "", filename: str = None) -> Dict[str, Any]:
        """Save JSON content with metadata wrapper and return filepath + metadata (organized by run ID)"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_desc = description.lower().replace(' ', '_').replace('/', '_')[:50]
            filename = f"{timestamp}_{safe_desc}.json" if safe_desc else f"{timestamp}_output.json"
        
        # Get run-specific artifacts directory
        artifacts_dir = self._get_artifacts_dir()
        filepath = artifacts_dir / filename
        
        # Handle different content types
        if isinstance(content, str):
            try:
                # Try to parse as JSON if it's a string
                data = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, treat as plain text
                data = content
        else:
            # Assume it's already a dict/list
            data = content
        
        # Calculate tokens on the data
        data_str = json.dumps(data, indent=2, default=str)
        token_count = self._count_tokens(data_str)
        
        # Create summary (first 200 chars of data)
        summary = str(data)[:200].replace('\n', ' ').strip()
        if len(str(data)) > 200:
            summary += "..."
        
        # Create metadata
        metadata = {
            "description": description,
            "created": datetime.now().isoformat(),
            "tokens": token_count,
            "summary": summary,
            "run_id": self._current_run_id,
            "file_type": "json"
        }
        
        # Create JSON structure with metadata and data
        json_content = {
            "metadata": metadata,
            "data": data
        }
        
        # Write JSON file
        with open(filepath, 'w') as f:
            json.dump(json_content, f, indent=2, default=str)
        
        return {
            "filepath": str(filepath),
            "run_id": self._current_run_id,
            "artifacts_dir": str(artifacts_dir),
            "frontmatter": metadata,
            "content_type": "json"
        }
    
    # ULTRA-MINIMAL API CALLS
    @auto_instrument('api')
    def api(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Simple API call with auto env var injection"""
        headers = kwargs.get('headers', {})
        
        # Auto-inject common API keys
        for env_var in ['API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'BRAVE_API_KEY']:
            if env_var in os.environ and 'Authorization' not in headers:
                if 'brave' in url.lower():
                    headers['X-Subscription-Token'] = os.environ[env_var]
                else:
                    headers['Authorization'] = f"Bearer {os.environ[env_var]}"
        
        kwargs['headers'] = headers
        return requests.request(method, url, **kwargs)
    
    # TEMPLATE RENDERING
    @auto_instrument('template')
    def template(self, template_str: str, **context) -> str:
        """Render Jinja2 template"""
        template = self.jinja_env.from_string(template_str)
        return template.render(**context)
    
    def _count_tokens(self, text: str) -> int:
        """Simple token counting"""
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except:
            return int(len(text.split()) * 1.3)  # Rough estimate

    def calculate_hash(self, content: str) -> str:
        """Calculate hash of content for change tracking"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()

    def strip_frontmatter(self, content: str) -> str:
        """Strip YAML frontmatter from content if present"""
        lines = content.split('\n')
        if lines and lines[0].strip() == '---':
            # Find the end of frontmatter
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    # Return content after frontmatter, skipping empty lines
                    remaining_lines = lines[i+1:]
                    while remaining_lines and not remaining_lines[0].strip():
                        remaining_lines.pop(0)
                    return '\n'.join(remaining_lines)
        return content


# GLOBAL INSTANCE - IMPORT AND USE IMMEDIATELY
helper = ToolHelper()

# CONVENIENCE FUNCTIONS FOR EVEN LESS BOILERPLATE
@auto_instrument('llm')
def llm(prompt: str, **kwargs) -> str:
    """Global LLM function using Pydantic AI"""
    return helper.llm(prompt, **kwargs)

@auto_instrument('llm')
def llm_json(prompt: str, **kwargs) -> Dict:
    """Global LLM JSON function using Pydantic AI"""
    return helper.llm_json(prompt, **kwargs)

@auto_instrument('llm')
def llm_structured(prompt: str, pydantic_model: Type[BaseModel], **kwargs):
    """Global structured LLM function using Pydantic AI"""
    return helper.llm_structured(prompt, pydantic_model, **kwargs)

@auto_instrument('llm')
def chain_prompts(prompts: List[str], **kwargs) -> List[str]:
    """Global prompt chaining function using Pydantic AI"""
    return helper.chain_prompts(prompts, **kwargs)

@auto_instrument('file')
def save(content: str, description: str = "", filename: str = None, add_frontmatter: bool = True) -> Dict[str, Any]:
    """Global save function"""
    return helper.save(content, description, filename, add_frontmatter)

@auto_instrument('file')
def save_json(content: Union[Dict, List, str], description: str = "", filename: str = None) -> Dict[str, Any]:
    """Global save_json function"""
    return helper.save_json(content, description, filename)

@auto_instrument('file')
def read(filepath: str) -> str:
    """Global read function"""
    return helper.read(filepath)

@auto_instrument('file')
def read_for_llm(filepath: str, include_frontmatter: bool = False, frontmatter_only: bool = False) -> str:
    """Global read function for LLM prompts with frontmatter handling"""
    return helper.read_for_llm(filepath, include_frontmatter, frontmatter_only)

@auto_instrument('api')
def api(url: str, method: str = "GET", **kwargs) -> requests.Response:
    """Global API function"""
    return helper.api(url, method, **kwargs)

@auto_instrument('template')
def template(template_str: str, **context) -> str:
    """Global template function"""
    return helper.template(template_str, **context)

def set_run_id(run_id: str):
    """Set the current run ID for file organization"""
    return helper.set_run_id(run_id)

def get_run_id() -> Optional[str]:
    """Get the current run ID"""
    return helper.get_run_id()

def calculate_hash(content: str) -> str:
    """Global calculate_hash function"""
    return helper.calculate_hash(content)

def strip_frontmatter(content: str) -> str:
    """Global strip_frontmatter function"""
    return helper.strip_frontmatter(content)

# Namespace class for even cleaner usage
class AI:
    """Namespace for AI operations - enables ai.llm(), ai.save(), etc."""
    llm = staticmethod(llm)
    llm_json = staticmethod(llm_json)
    llm_structured = staticmethod(llm_structured)
    chain_prompts = staticmethod(chain_prompts)
    save = staticmethod(save)
    save_json = staticmethod(save_json)
    read = staticmethod(read)
    read_for_llm = staticmethod(read_for_llm)
    api = staticmethod(api)
    template = staticmethod(template)
    set_run_id = staticmethod(set_run_id)
    get_run_id = staticmethod(get_run_id)

# Create global AI instance
ai = AI()

# Define what gets imported with "from app.tool_services import *"
__all__ = [
    # Core functions
    'llm', 'llm_json', 'llm_structured', 'chain_prompts',
    'save', 'save_json', 'read', 'read_for_llm', 'api', 'template', 'set_run_id', 'get_run_id',
    'calculate_hash', 'strip_frontmatter', 'ai', 'helper',
    # Common imports for tools
    'json', 'yaml', 'Path', 're', 'ast', 'os', 'datetime', 'BaseModel', 'Dict', 'Any', 'List', 'Optional', 'Type'
]