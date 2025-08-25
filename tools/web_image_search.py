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
    Search for images with automatic fallback between multiple providers
    
    Tries providers in this order (external APIs first for cost efficiency):
    1. Serper.dev Images API (if SERPER_API_KEY available)
    2. Brave Images API (if BRAVE_API_KEY available)
    3. OpenAI Search (GPT-4o-mini-search-preview) - Fallback only
    
    Args:
        query: The search query to execute
        num_results: Number of image results to return (default: 10)
    
    Returns:
        JSON string containing image search results from the first successful provider
    """
    
    # Try Serper.dev Images API first (most cost effective)
    try:
        search_prompt = f"""Search for images related to: "{query}"

Provide {num_results} relevant image results in the following JSON format:
{{
  "results": [
    {{
      "title": "Image description",
      "url": "https://example.com/image.jpg",
      "image_url": "https://example.com/image.jpg",
      "thumbnail": "https://example.com/thumb.jpg",
      "width": "800",
      "height": "600",
      "source": "Source website name"
    }}
  ]
}}

Focus on finding relevant, high-quality images. Return only valid JSON."""

        search_results = llm_json(
            search_prompt,
            model="openai/gpt-5-nano"
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
                        pass  # Continue to next provider
        
        # Normalize the results format
        results = []
        if isinstance(search_results, dict) and "results" in search_results:
            for result in search_results["results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "image_url": result.get("image_url", ""),
                    "thumbnail": result.get("thumbnail", ""),
                    "width": result.get("width", ""),
                    "height": result.get("height", ""),
                    "source": result.get("source", ""),
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
                        "providers_tried": ["OpenAI Search"]
                    }
                }, indent=2)
    
    except Exception as e:
        pass  # Continue to next provider
    
    # Try Serper.dev Images API
    try:
        serper_api_key = os.getenv('SERPER_API_KEY')
        if serper_api_key:
            url = "https://google.serper.dev/images"
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
            
            if "images" in data:
                for result in data["images"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "image_url": result.get("imageUrl", ""),
                        "thumbnail": result.get("thumbnail", ""),
                        "width": result.get("imageWidth", ""),
                        "height": result.get("imageHeight", ""),
                        "source": result.get("source", ""),
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
                            "providers_tried": ["OpenAI Search", "Serper.dev"]
                        }
                    }, indent=2)
    
    except Exception as e:
        pass  # Continue to next provider
    
    # Try Brave Images API as final fallback
    try:
        brave_api_key = os.getenv('BRAVE_API_KEY')
        if brave_api_key:
            url = "https://api.search.brave.com/res/v1/images/search"
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
                        "image_url": result.get("image", ""),
                        "thumbnail": result.get("thumbnail", ""),
                        "width": result.get("width", ""),
                        "height": result.get("height", ""),
                        "source": result.get("source", ""),
                        "provider": "Serper.dev"
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
                            "providers_tried": ["OpenAI Search", "Serper.dev", "Brave Search"]
                        }
                    }, indent=2)
    
    except Exception as e:
        pass
    
    # If all providers failed
    return json.dumps({
        "error": "All image search providers failed",
        "query": query,
        "providers_tried": ["OpenAI Search", "Serper.dev", "Brave Search"]
    }, indent=2)


if __name__ == "__main__":
    # Test the tool
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = web_image_search(query)
        print(result)
    else:
        print("Usage: python web_image_search.py <search query>") 