#!/usr/bin/env python3
"""
Tool: web_search
Description: Search the web with automatic fallback between multiple providers:
1. OpenAI Search (GPT-4o-mini-search-preview) via OpenRouter
2. Serper.dev API (if SERPER_API_KEY available)
3. Google Custom Search (if GOOGLE_API_KEY available) 
4. Brave Search API (if BRAVE_API_KEY available)

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.web_search import web_search
result = web_search('artificial intelligence news', 3)
print(result)
"
"""

from app.tool_services import *
import json
import os

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web with automatic fallback between multiple providers (Serper.dev, Google CSE, Brave, OpenAI Search). Prioritizes external APIs for cost efficiency.",
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


def web_search_openai(query: str, num_results: int = 5) -> dict:
    """Search using OpenAI's search-enabled model via OpenRouter"""
    try:
        search_prompt = f"""Search for: "{query}"

Provide {num_results} relevant web search results in the following JSON format:
{{
  "results": [
    {{
      "title": "Page title",
      "url": "https://example.com",
      "snippet": "Brief description of the content"
    }}
  ]
}}

Return only valid JSON with actual search results from the web."""

        search_results = llm_json(
            search_prompt,
            model="openai/gpt-4o-mini-search-preview"
        )
        
        # Handle case where llm_json returns an error dict
        if isinstance(search_results, dict) and "error" in search_results:
            # Try to extract JSON from the raw response if it's wrapped in markdown
            raw_response = search_results.get("raw_response", "")
            if "```json" in raw_response:
                # Extract JSON from markdown code blocks
                start = raw_response.find("```json") + 7
                end = raw_response.find("```", start)
                if end != -1:
                    json_str = raw_response[start:end].strip()
                    try:
                        search_results = json.loads(json_str)
                    except json.JSONDecodeError:
                        raise Exception(f"Failed to parse OpenAI search response: {search_results.get('error', 'Unknown error')}")
            else:
                raise Exception(f"OpenAI search failed: {search_results.get('error', 'Unknown error')}")
        
        # Normalize the results format
        results = []
        if isinstance(search_results, dict) and "results" in search_results:
            for result in search_results["results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "provider": "OpenAI Search"
                })
        
        return {
            "success": True,
            "provider": "OpenAI Search",
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"OpenAI search failed: {str(e)}"}


def web_search_serper(query: str, num_results: int = 5) -> dict:
    """Search using Serper.dev API"""
    try:
        serper_api_key = os.getenv('SERPER_API_KEY')
        if not serper_api_key:
            return {"error": "SERPER_API_KEY not found in environment variables"}
        
        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "num": min(num_results, 100),
            "gl": "us",
            "hl": "en"
        }
        
        response = api(url, method="POST", json=payload, timeout=10, headers={
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        })
        
        data = response.json()
        results = []
        
        if "organic" in data:
            for result in data["organic"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "provider": "Serper.dev"
                })
        
        return {
            "success": True,
            "provider": "Serper.dev",
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"Serper search failed: {str(e)}"}


def web_search_google(query: str, num_results: int = 5) -> dict:
    """Search using Google Custom Search Engine API"""
    try:
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_cx = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not google_api_key:
            return {"error": "GOOGLE_API_KEY not found in environment variables"}
        if not google_cx:
            return {"error": "GOOGLE_SEARCH_ENGINE_ID not found in environment variables"}
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": google_api_key,
            "cx": google_cx,
            "q": query,
            "num": min(num_results, 10),
            "gl": "us",
            "hl": "en"
        }
        
        response = api(url, method="GET", params=params, timeout=10, headers={
            "Accept": "application/json"
        })
        
        data = response.json()
        
        if "error" in data:
            return {"error": f"Google API error: {data['error'].get('message', 'Unknown error')}"}
        
        results = []
        if "items" in data:
            for item in data["items"][:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "provider": "Google CSE"
                })
        
        return {
            "success": True,
            "provider": "Google CSE",
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"Google search failed: {str(e)}"}


def web_search_brave(query: str, num_results: int = 5) -> dict:
    """Search using Brave Search API"""
    try:
        brave_api_key = os.getenv('BRAVE_API_KEY')
        if not brave_api_key:
            return {"error": "BRAVE_API_KEY not found in environment variables"}
        
        url = "https://api.search.brave.com/res/v1/web/search"
        params = {
            "q": query,
            "count": min(num_results, 20),
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "freshness": "all"
        }
        
        response = api(url, method="GET", params=params, timeout=10, headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": brave_api_key
        })
        
        data = response.json()
        results = []
        
        if "web" in data and "results" in data["web"]:
            for result in data["web"]["results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("description", ""),
                    "provider": "Brave Search"
                })
        
        return {
            "success": True,
            "provider": "Brave Search",
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"Brave search failed: {str(e)}"}


def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web with automatic fallback between multiple providers
    
    Tries providers in this order (external APIs first for cost efficiency):
    1. Serper.dev API (if SERPER_API_KEY available)
    2. Google Custom Search (if GOOGLE_API_KEY available)
    3. Brave Search API (if BRAVE_API_KEY available)
    4. OpenAI Search (GPT-4o-mini-search-preview) - Fallback only
    
    Args:
        query: The search query to execute
        num_results: Number of search results to return (default: 5)
    
    Returns:
        JSON string containing search results from the first successful provider
    """
    
    # List of search providers to try in order (external APIs first for cost efficiency)
    providers = [
        ("Serper.dev", web_search_serper), 
        ("Google CSE", web_search_google),
        ("Brave Search", web_search_brave),
        ("OpenAI Search", web_search_openai)  # Fallback only
    ]
    
    errors = []
    
    for provider_name, search_func in providers:
        try:
            result = search_func(query, num_results)
            
            if "success" in result and result["success"]:
                # Add fallback information to the result
                result["fallback_info"] = {
                    "provider_used": provider_name,
                    "providers_tried": [p[0] for p in providers[:providers.index((provider_name, search_func)) + 1]],
                    "errors_encountered": errors
                }
                return json.dumps(result, indent=2)
            else:
                error_msg = result.get("error", f"{provider_name} returned no results")
                errors.append(f"{provider_name}: {error_msg}")
                
        except Exception as e:
            error_msg = f"{provider_name}: {str(e)}"
            errors.append(error_msg)
    
    # If all providers failed
    return json.dumps({
        "error": "All search providers failed",
        "query": query,
        "providers_tried": [p[0] for p in providers],
        "errors": errors
    }, indent=2)


if __name__ == "__main__":
    # Test the tool
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = web_search(query)
        print(result)
    else:
        print("Usage: python web_search.py <search query>") 