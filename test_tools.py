#!/usr/bin/env python3
"""
Test individual tools in the framework
"""

import sys
from tools.web_search import web_search
from tools.web_read_page import web_read_page

def test_web_search():
    """Test the web search tool"""
    print("Testing web search tool...")
    result = web_search("Python programming")
    print(result)
    print("\n" + "="*50 + "\n")

def test_web_read_page():
    """Test the web page reading tool"""
    print("Testing web page reading tool...")
    result = web_read_page("https://python.org")
    print(result)
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    print("=== Testing Individual Tools ===\n")
    
    if len(sys.argv) > 1:
        tool_name = sys.argv[1]
        if tool_name == "search":
            test_web_search()
        elif tool_name == "read":
            test_web_read_page()
        else:
            print(f"Unknown tool: {tool_name}")
            print("Available tools: search, read")
    else:
        print("Testing all tools...\n")
        test_web_search()
        test_web_read_page()
        print("All tools tested successfully!") 