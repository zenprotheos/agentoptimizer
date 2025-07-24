# app/tool_services.py

import os
import json
import yaml
import requests
import asyncio
from pathlib import Path
from typing import Dict, Any, Union, Optional, List, Type
from datetime import datetime
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
import tiktoken

# Pydantic AI imports
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    
    def _load_config(self):
        """Load config with sensible defaults"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}
    
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
    
    # ULTRA-MINIMAL LLM CALLING using Pydantic AI
    def llm(self, prompt: str, model: str = None, system_prompt: str = None, **kwargs) -> str:
        """Ultra-simple LLM call using Pydantic AI"""
        return asyncio.run(self._llm_async(prompt, model, system_prompt, **kwargs))
    
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
        
        # Create a simple agent for this call
        agent = Agent(
            model=current_model,
            system_prompt=system_prompt or "You are a helpful assistant.",
            model_settings=current_settings
        )
        
        # Run the agent
        result = await agent.run(prompt, usage_limits=self.usage_limits)
        return str(result.output)
    
    def llm_json(self, prompt: str, model: str = None, **kwargs) -> Dict:
        """LLM call that returns parsed JSON using Pydantic AI"""
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        response = self.llm(json_prompt, model, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "raw_response": response}
    
    def llm_structured(self, prompt: str, pydantic_model: Type[BaseModel], model: str = None, **kwargs):
        """LLM call with structured output using Pydantic AI"""
        return asyncio.run(self._llm_structured_async(prompt, pydantic_model, model, **kwargs))
    
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
        
        # Create agent with structured response
        agent = Agent(
            model=current_model,
            result_type=pydantic_model,
            system_prompt="You are a helpful assistant. Respond with structured data matching the required format.",
            model_settings=current_settings
        )
        
        # Run the agent
        result = await agent.run(prompt, usage_limits=self.usage_limits)
        return result.output
    
    # CHAIN PROMPTS - using Pydantic AI conversation capabilities
    def chain_prompts(self, prompts: List[str], model: str = None, system_prompt: str = None, **kwargs) -> List[str]:
        """Chain multiple prompts together using Pydantic AI conversation"""
        return asyncio.run(self._chain_prompts_async(prompts, model, system_prompt, **kwargs))
    
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
        
        # Create agent for conversation
        agent = Agent(
            model=current_model,
            system_prompt=system_prompt or "You are a helpful assistant.",
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
        """Set the current run ID for file organization"""
        self._current_run_id = run_id
    
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
    def read(self, filepath: str) -> str:
        """Read any file"""
        return Path(filepath).read_text()
    
    def save(self, content: str, description: str = "", filename: str = None) -> Dict[str, Any]:
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
        
        # Add frontmatter
        frontmatter = f"""---
description: {description}
created: {datetime.now().isoformat()}
tokens: {token_count}
summary: {summary}
---

{content}"""
        
        filepath.write_text(frontmatter)
        
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
    
    # ULTRA-MINIMAL API CALLS
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


# GLOBAL INSTANCE - IMPORT AND USE IMMEDIATELY
helper = ToolHelper()

# CONVENIENCE FUNCTIONS FOR EVEN LESS BOILERPLATE
def llm(prompt: str, **kwargs) -> str:
    """Global LLM function using Pydantic AI"""
    return helper.llm(prompt, **kwargs)

def llm_json(prompt: str, **kwargs) -> Dict:
    """Global LLM JSON function using Pydantic AI"""
    return helper.llm_json(prompt, **kwargs)

def llm_structured(prompt: str, pydantic_model: Type[BaseModel], **kwargs):
    """Global structured LLM function using Pydantic AI"""
    return helper.llm_structured(prompt, pydantic_model, **kwargs)

def chain_prompts(prompts: List[str], **kwargs) -> List[str]:
    """Global prompt chaining function using Pydantic AI"""
    return helper.chain_prompts(prompts, **kwargs)

def save(content: str, description: str = "", filename: str = None) -> Dict[str, Any]:
    """Global save function"""
    return helper.save(content, description, filename)

def read(filepath: str) -> str:
    """Global read function"""
    return helper.read(filepath)

def api(url: str, method: str = "GET", **kwargs) -> requests.Response:
    """Global API function"""
    return helper.api(url, method, **kwargs)

def template(template_str: str, **context) -> str:
    """Global template function"""
    return helper.template(template_str, **context)

def set_run_id(run_id: str):
    """Set the current run ID for file organization"""
    return helper.set_run_id(run_id)

def get_run_id() -> Optional[str]:
    """Get the current run ID"""
    return helper.get_run_id()

# Namespace class for even cleaner usage
class AI:
    """Namespace for AI operations - enables ai.llm(), ai.save(), etc."""
    llm = staticmethod(llm)
    llm_json = staticmethod(llm_json)
    llm_structured = staticmethod(llm_structured)
    chain_prompts = staticmethod(chain_prompts)
    save = staticmethod(save)
    read = staticmethod(read)
    api = staticmethod(api)
    template = staticmethod(template)
    set_run_id = staticmethod(set_run_id)
    get_run_id = staticmethod(get_run_id)

# Create global AI instance
ai = AI()

# Define what gets imported with "from app.tool_services import *"
__all__ = [
    'llm', 'llm_json', 'llm_structured', 'chain_prompts',
    'save', 'read', 'api', 'template', 'set_run_id', 'get_run_id',
    'ai', 'helper'
]