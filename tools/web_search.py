#!/usr/bin/env python3
"""
Web search tool for the AI Agent framework
"""

from app.tool_services import *

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
        # Check for Brave API key
        brave_api_key = os.getenv('BRAVE_API_KEY')
        if not brave_api_key:
            return json.dumps({"error": "BRAVE_API_KEY not found in environment variables"}, indent=2)
        
        # Brave Search API endpoint
        url = "https://api.search.brave.com/res/v1/web/search"
        
        # Parameters for the search
        params = {
            "q": query,
            "count": min(num_results, 20),  # Brave API allows max 20 results
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "freshness": "all"
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
        
        # Save results using tool_services
        saved_file = save_json(formatted_results, f"Web search results for: {query}")
        
        return json.dumps({
            "success": True,
            "query": query,
            "total_results": len(results),
            "results": results,
            "filepath": saved_file["filepath"],
            "run_id": saved_file["run_id"]
        }, indent=2)
        
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