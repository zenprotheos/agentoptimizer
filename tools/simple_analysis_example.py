# tools/simple_analysis_example.py
# Example tool using the new Pydantic AI-powered tool helper

from app.tool_services import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "simple_analysis_example",
        "description": "Analyze text and save results using Pydantic AI",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"}
            },
            "required": ["text"]
        }
    }
}

def simple_analysis_example(text: str) -> str:
    """Ultra-minimal tool using Pydantic AI through tool helper"""
    
    # One line LLM call using Pydantic AI!
    analysis = llm(f"Analyze this text and provide insights: {text}")
    
    # One line save with metadata!
    result = save(analysis, "Text analysis results")
    
    return json.dumps({
        "success": True, 
        "filepath": result["filepath"],
        "tokens": result["frontmatter"]["tokens"]
    }, indent=2) 