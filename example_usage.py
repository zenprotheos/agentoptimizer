#!/usr/bin/env python3
"""
Example usage of the AI Agent Framework
"""

import os
from app.agent_runner import AgentRunner
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def example_programmatic_usage():
    """Example of using the framework programmatically"""
    
    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("Please set OPENROUTER_API_KEY environment variable")
        return
    
    # Create an agent runner (will load config.yaml automatically)
    runner = AgentRunner()
    
    # Run an agent with a message
    result = runner.run_agent("web_agent", "Hello, can you help me search for information about Python?")
    
    print("Agent Response:")
    print(result)

def example_cli_usage():
    """Example of CLI usage (shown as comments)"""
    print("""
    CLI Usage Examples:
    
    # Basic usage
    python3 app/agent_runner.py web_agent "Search for Python tutorials"
    
    # Ask for help with a specific topic
    python3 app/agent_runner.py web_agent "Find information about Pydantic AI framework"
    
    # Web search and reading
    python3 app/agent_runner.py web_agent "Search for 'machine learning' and read the first result"
    """)

if __name__ == "__main__":
    print("=== AI Agent Framework Usage Examples ===\n")
    
    print("1. Programmatic Usage:")
    example_programmatic_usage()
    
    print("\n2. CLI Usage:")
    example_cli_usage()
    
    print("\nNote: Make sure to set OPENROUTER_API_KEY in environment variables or .env file before running agents.") 