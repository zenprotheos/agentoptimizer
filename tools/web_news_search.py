#!/usr/bin/env python3
"""
Tool: web_news_search
Description: Search for news using Brave News API

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.web_news_search import web_news_search
result = web_news_search('british lions', 5)
print(result)
"
"""

from app.tool_services import *

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "web_news_search",
        "description": "Search for news articles using a search query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of news results to return",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}


def web_news_search(query: str, num_results: int = 10) -> str:
    """
    Search for news articles with automatic fallback between multiple providers
    
    Tries providers in this order (external APIs first for cost efficiency):
    1. Serper.dev News API (if SERPER_API_KEY available)
    2. Brave News API (if BRAVE_API_KEY available)
    3. OpenAI Search (GPT-4o-mini-search-preview) - Fallback only
    
    Args:
        query: The search query to execute
        num_results: Number of news results to return (default: 10)
    
    Returns:
        JSON string containing news search results from the first successful provider
    """
    
    # Try Serper.dev News API first (most cost effective)
    try:
        serper_api_key = os.getenv('SERPER_API_KEY')
        if serper_api_key:
            url = "https://google.serper.dev/news"
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
            
            if "news" in data:
                for result in data["news"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "description": result.get("snippet", ""),
                        "age": result.get("date", ""),
                        "provider": "Serper.dev"
                    })
                
                if results:
                    return json.dumps({
                        "success": True,
                        "provider": "Serper.dev",
                        "query": query,
                        "total_results": len(results),
                        "results": results,
                        "fallback_info": {
                            "provider_used": "Serper.dev",
                            "providers_tried": ["Serper.dev"]
                        }
                    }, indent=2)
    
    except Exception as e:
        pass  # Continue to next provider
    
    # Try Brave News API as final fallback
    try:
        brave_api_key = os.getenv('BRAVE_API_KEY')
        if brave_api_key:
            url = "https://api.search.brave.com/res/v1/news/search"
            params = {
                "q": query,
                "count": min(num_results, 20),
                "country": "us",
                "search_lang": "en",
                "spellcheck": 1
            }
            
            response = api(url, method="GET", params=params, timeout=10, headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": brave_api_key
            })
            
            data = response.json()
            results = []
            
            if "results" in data:
                for result in data["results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("description", ""),
                        "age": result.get("age", ""),
                        "provider": "Brave Search"
                    })
                
                if results:
                    return json.dumps({
                        "success": True,
                        "provider": "Brave Search",
                        "query": query,
                        "total_results": len(results),
                        "results": results,
                        "fallback_info": {
                            "provider_used": "Brave Search",
                            "providers_tried": ["Serper.dev", "Brave Search"]
                        }
                    }, indent=2)
    
    except Exception as e:
        pass
    
    # Try OpenAI Search as final fallback
    try:
        search_prompt = f"""Search for recent news about: "{query}"

Provide {num_results} relevant news articles in the following JSON format:
{{
  "results": [
    {{
      "title": "News headline",
      "url": "https://example.com",
      "description": "Brief description of the news",
      "age": "How recent this news is"
    }}
  ]
}}

Focus on recent, factual news articles. Return only valid JSON."""

        search_results = llm_json(
            search_prompt,
            model="openai/gpt-4o-mini-search-preview"
        )
        
        # Handle case where llm_json returns an error dict
        if isinstance(search_results, dict) and "error" in search_results:
            raw_response = search_results.get("raw_response", "")
            if "```json" in raw_response:
                start = raw_response.find("```json") + 7
                end = raw_response.find("```", start)
                if end != -1:
                    json_str = raw_response[start:end].strip()
                    try:
                        search_results = json.loads(json_str)
                    except json.JSONDecodeError:
                        pass
        
        if isinstance(search_results, dict) and "results" in search_results:
            results = []
            for result in search_results["results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "age": result.get("age", ""),
                    "provider": "OpenAI Search"
                })
            
            if results:
                return json.dumps({
                    "success": True,
                    "provider": "OpenAI Search",
                    "query": query,
                    "total_results": len(results),
                    "results": results,
                    "fallback_info": {
                        "provider_used": "OpenAI Search",
                        "providers_tried": ["Serper.dev", "Brave Search", "OpenAI Search"]
                    }
                }, indent=2)
    
    except Exception as e:
        pass
    
    # If all providers failed
    return json.dumps({
        "error": "All news search providers failed",
        "query": query,
        "providers_tried": ["Serper.dev", "Brave Search", "OpenAI Search"]
    }, indent=2)


if __name__ == "__main__":
    # Test the tool
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = web_news_search(query)
        print(result)
    else:
        print("Usage: python web_news_search.py <search query>") 