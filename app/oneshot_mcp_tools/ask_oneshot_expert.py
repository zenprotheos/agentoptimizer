#!/usr/bin/env python3
"""
Ask Oneshot Expert Tool

This tool allows you to ask questions about the oneshot repo to a simulated senior developer
who has deep knowledge of the system architecture and implementation.
"""

import os
import json
from pathlib import Path
from typing import List

# Import PydanticAI directly to avoid async issues
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from dotenv import load_dotenv
load_dotenv()


async def ask_oneshot_expert(question: str, project_root: str = ".") -> str:
    """Ask a question about the oneshot repo to a senior developer expert
    
    Args:
        question: The question to ask about the oneshot system
        project_root: Root directory of the project
        
    Returns:
        str: JSON formatted response from the expert
    """
    try:
        # Build comprehensive context about the oneshot system
        context = _build_expert_context(project_root)
        
        # Create OpenRouter model directly
        model = OpenAIModel(
            model_name="google/gemini-2.5-flash",
            provider=OpenAIProvider(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv('OPENROUTER_API_KEY')
            )
        )
        
        # Create comprehensive system prompt with expert persona and repo contents
        system_prompt = f"""You are the lead architect and senior developer of the oneshot agentic AI system. You have complete, intimate knowledge of every line of code, configuration option, and architectural decision in this codebase.

Your primary role is to serve as a rapid diagnostic expert for developers working with oneshot. When asked about problems, issues, or behaviors, you should:

1. **Pinpoint exact code locations**: Identify the specific files, classes, methods, and line ranges responsible for the behavior in question
2. **Trace execution paths**: Follow the complete flow from entry point through all relevant components 
3. **Identify edge cases and failure modes**: Highlight what can go wrong and under what conditions
4. **Provide actionable solutions**: Give specific code changes, configuration fixes, or debugging approaches
5. **Reference actual implementation details**: Quote relevant code snippets, configuration patterns, and architectural decisions

You excel at quickly getting to the heart of complex issues without requiring multiple back-and-forth questions. You can instantly see how different components interact, where data flows, and what happens in edge cases that might not be immediately obvious.

Below is the complete documentation and source code for the oneshot system.

--------------------------------
ONESHOT SYSTEM DOCUMENTATION AND CODE:


{context}


--------------------------------

When answering questions, focus on being precise, actionable, and comprehensive. Always reference specific code locations and implementation details to support your analysis."""
        
        # Create agent with the comprehensive system prompt that includes all repo contents
        agent = Agent(
            model=model,
            system_prompt=system_prompt
        )
        
        # Simple user message with just the question
        user_message = question
        
        # Run asynchronously in the current event loop
        result = await agent.run(user_message)
        response = result.data
        
        return json.dumps({
            "success": True,
            "question": question,
            "expert_response": response,
            "model_used": "google/gemini-2.5-flash"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get expert response: {str(e)}",
            "question": question
        }, indent=2)


def _build_expert_context(project_root: str) -> str:
    """Build comprehensive context from guides and code files"""
    context_parts = []
    
    # Add background documentation
    context_parts.append("BACKGROUND DOCUMENTATION ON ONESHOT SYSTEM:")
    context_parts.append("=" * 50)
    
    # Add README.md first
    readme_path = Path(project_root) / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            context_parts.append(f"\n## README.md\n")
            context_parts.append(content)
        except Exception as e:
            context_parts.append(f"\n## README.md (Error reading: {e})\n")
    
    # Get all guide files
    guides_dir = Path(project_root) / "app" / "guides"
    if guides_dir.exists():
        for guide_file in sorted(guides_dir.glob("*.md")):
            try:
                with open(guide_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                context_parts.append(f"\n## {guide_file.name}\n")
                context_parts.append(content)
            except Exception as e:
                context_parts.append(f"\n## {guide_file.name} (Error reading: {e})\n")
    
    # Add configuration files
    context_parts.append("\n\nCONFIG FILES:")
    context_parts.append("=" * 50)
    
    # Add .cursor/*.mdc files
    cursor_dir = Path(project_root) / ".cursor"
    if cursor_dir.exists():
        context_parts.append(f"\n### .cursor/ directory\n")
        for mdc_file in sorted(cursor_dir.glob("*.mdc")):
            try:
                with open(mdc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                context_parts.append(f"\n#### {mdc_file.name}\n")
                context_parts.append(f"```\n{content}\n```\n")
            except Exception as e:
                context_parts.append(f"\n#### {mdc_file.name} (Error reading: {e})\n")
    
    # Add requirements.txt
    requirements_path = Path(project_root) / "requirements.txt"
    if requirements_path.exists():
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                content = f.read()
            context_parts.append(f"\n### requirements.txt\n")
            context_parts.append(f"```\n{content}\n```\n")
        except Exception as e:
            context_parts.append(f"\n### requirements.txt (Error reading: {e})\n")
    
    # Add config.yaml
    config_path = Path(project_root) / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            context_parts.append(f"\n### config.yaml\n")
            context_parts.append(f"```yaml\n{content}\n```\n")
        except Exception as e:
            context_parts.append(f"\n### config.yaml (Error reading: {e})\n")

    # Add code files
    context_parts.append("\n\nCODE FILES:")
    context_parts.append("=" * 50)
    
    # Get all Python files in /app directory (including subdirectories)
    app_dir = Path(project_root) / "app"
    if app_dir.exists():
        # Group files by directory
        code_by_dir = {}
        
        for py_file in app_dir.rglob("*.py"):
            # Skip __pycache__ directories
            if "__pycache__" in str(py_file):
                continue
                
            # Get relative path from app directory
            rel_path = py_file.relative_to(app_dir)
            dir_name = str(rel_path.parent) if rel_path.parent != Path('.') else "root"
            
            if dir_name not in code_by_dir:
                code_by_dir[dir_name] = []
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                code_by_dir[dir_name].append((py_file.name, content))
            except Exception as e:
                code_by_dir[dir_name].append((py_file.name, f"Error reading file: {e}"))
        
        # Output organized by directory
        for dir_name in sorted(code_by_dir.keys()):
            context_parts.append(f"\n### {dir_name.upper()} DIRECTORY\n")
            
            for filename, content in sorted(code_by_dir[dir_name]):
                context_parts.append(f"\n#### {filename}\n")
                context_parts.append(f"```python\n{content}\n```\n")
    
    return "\n".join(context_parts)


if __name__ == "__main__":
    # Test the tool
    test_question = "How does the agent orchestration system work?"
    result = ask_oneshot_expert(test_question)
    print(result)