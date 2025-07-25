#!/usr/bin/env python3
"""
Todo read tool for the AI Agent framework - reads the current todo list for the session
"""

from ast import Return
import json
import os
from pathlib import Path
from typing import Dict, Any, List

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "todo_read",
        "description": "Read the current todo list for the session. This tool takes no parameters. It returns a list of todo items with their status, priority, and content. Use this information to track progress and plan next steps. If no todos exist yet, an empty list will be returned",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


def todo_read() -> str:
    """
    Read the current todo list for the session
    
    Returns:
        JSON string containing the current todo list with items, their status, priority, and content
    """
    try:
        # Get the current run ID from environment variable set by agent runner
        run_id = os.getenv('ONESHOT_RUN_ID')
        if not run_id:
            return json.dumps({
                "error": "No active run session found. Todo lists are session-specific.",
                "todos": []
            }, indent=2)
        
        # Path to the todo file for this run
        todo_file = Path(f"runs/{run_id}/todos.json")
        
        # If todo file doesn't exist, return empty list
        if not todo_file.exists():
            return json.dumps({
                "message": "No todos found for this session",
                "todos": []
            }, indent=2)
        
        # Read and return the todo list
        with open(todo_file, 'r') as f:
            todos = json.load(f)
        
        return json.dumps({
            "message": f"Found {len(todos)} todo items for this session",
            "todos": todos
        }, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON in todo file: {str(e)}",
            "todos": []
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"Failed to read todo list: {str(e)}",
            "todos": []
        }, indent=2)


if __name__ == "__main__":
    # Test the function
    print(todo_read()) 