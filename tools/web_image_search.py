#!/usr/bin/env python3
"""
Tool: web_image_search
Description: Search for images using Brave Images API

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.web_image_search import web_image_search
result = web_image_search('sunset landscape', 5)
print(result)
"
"""

from app.tool_services import *

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "web_image_search",
        "description": "Search for images using a search query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of image results to return",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}


def web_image_search(query: str, num_results: int = 10) -> str:
    """
    Search for images using Brave Images API
    
    Args:
        query: The search query to execute
        num_results: Number of image results to return (default: 10)
    
    Returns:
        JSON string containing image search results
    """
    try:
        # Check for Brave API key
        brave_api_key = os.getenv('BRAVE_API_KEY')
        if not brave_api_key:
            return json.dumps({"error": "BRAVE_API_KEY not found in environment variables"}, indent=2)
        
        # Brave Images API endpoint
        url = "https://api.search.brave.com/res/v1/images/search"
        
        # Parameters for the search
        params = {
            "q": query,
            "count": min(num_results, 20),  # Brave API allows max 20 results
            "country": "us",
            "search_lang": "en",
            "spellcheck": 1
        }
        
        # Use tool_services api() function with custom headers
        response = api(url, method="GET", params=params, timeout=10, headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": brave_api_key
        })
        
        # Parse the response
        data = response.json()
        
        # Extract and format results
        results = []
        if "results" in data:
            for result in data["results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "image_url": result.get("image", ""),
                    "thumbnail": result.get("thumbnail", ""),
                    "width": result.get("width", ""),
                    "height": result.get("height", ""),
                    "source": result.get("source", ""),
                    "age": result.get("age", "")
                })
        
        return json.dumps({
            "success": True,
            "query": query,
            "total_results": len(results),
            "results": results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Image search failed: {str(e)}"}, indent=2)


if __name__ == "__main__":
    # Test the tool
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = web_image_search(query)
        print(result)
    else:
        print("Usage: python web_image_search.py <search query>") 