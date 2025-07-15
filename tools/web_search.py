#!/usr/bin/env python3
"""
Web search tool for the AI Agent framework
"""

import requests
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for information using a search query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}


def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for information using Brave Search API
    
    Args:
        query: The search query to execute
        num_results: Number of search results to return (default: 5)
    
    Returns:
        JSON string containing search results
    """
    try:
        # Get Brave API key from environment
        api_key = os.getenv('BRAVE_API_KEY')
        if not api_key:
            return json.dumps({"error": "BRAVE_API_KEY not found in environment variables"}, indent=2)
        
        # Brave Search API endpoint
        url = "https://api.search.brave.com/res/v1/web/search"
        
        # Headers for Brave API
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        # Parameters for the search
        params = {
            "q": query,
            "count": min(num_results, 20),  # Brave API allows max 20 results
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "freshness": "all"
        }
        
        # Make the API request
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Extract and format results
        results = []
        if "web" in data and "results" in data["web"]:
            for result in data["web"]["results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("description", ""),
                    "published": result.get("age", "")
                })
        
        formatted_results = {
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
        return json.dumps(formatted_results, indent=2)
        
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"API request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"}, indent=2)


if __name__ == "__main__":
    # Test the tool
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = web_search(query)
        print(result)
    else:
        print("Usage: python web_search.py <search query>") 