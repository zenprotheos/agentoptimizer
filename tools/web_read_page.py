#!/usr/bin/env python3
"""
Web page reading tool for the AI Agent framework
"""

from app.tool_services import *
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "web_read_page",
        "description": "Read and extract text content from a web page",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the web page to read"
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of text to return (in characters)",
                    "default": 5000
                }
            },
            "required": ["url"]
        }
    }
}


def web_read_page(url: str, max_length: int = 5000) -> str:
    """
    Read and extract text content from a web page
    
    Args:
        url: The URL to read
        max_length: Maximum length of text to return
        
    Returns:
        JSON string with page content
    """
    
    try:
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract main content
        # Try to find main content areas first
        main_content = None
        for selector in ['main', 'article', '.content', '#content', '.post', '.entry']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            main_content = soup
        
        # Extract text
        text = main_content.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Extract some metadata
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True)[:10]:  # Limit to first 10 links
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                links.append({
                    'text': link.get_text().strip(),
                    'url': absolute_url
                })
        
        return json.dumps({
            "url": url,
            "title": title_text,
            "description": description,
            "content": text,
            "links": links,
            "content_length": len(text)
        }, indent=2)
        
    except requests.RequestException as e:
        return json.dumps({
            "error": f"Failed to fetch page: {str(e)}",
            "url": url
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"Failed to parse page: {str(e)}",
            "url": url
        }, indent=2)


if __name__ == "__main__":
    # Test the tool
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = web_read_page(url)
        print(result)
    else:
        print("Usage: python web_read_page.py <url>") 