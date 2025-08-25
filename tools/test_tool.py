#!/usr/bin/env python3
"""
Test tool for the AI Agent framework
Simple tool that returns a test message - used for testing agent configurations
"""

from app.tool_services import *

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "test_tool",
        "description": "A simple test tool that returns a test message",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Optional message to include in the test response",
                    "default": "Hello from test tool!"
                }
            },
            "required": []
        }
    }
}


def test_tool(message: str = "Hello from test tool!") -> str:
    """
    A simple test tool that returns a test message
    
    Args:
        message: Optional message to include in the test response
    
    Returns:
        Test response message
    """
    # Use tool_services for consistency, but maintain exact output format for system testing
    # Removed emoji to prevent Windows Unicode encoding errors
    response = f"[OK] Test tool executed successfully! Message: {message}"
    
    # Save test execution for run-aware organization (optional for test tool)
    save(response, "Test tool execution")
    
    # Return the exact same format as before for system testing compatibility
    return response


# Main function (required by the framework)
def main():
    """Main function for standalone testing"""
    result = test_tool("Testing from main function")
    print(result)
    return result


if __name__ == "__main__":
    main() 