# tools/structured_example.py
# Example tool showing structured output with Pydantic AI

from app.tool_helper import *
from pydantic import BaseModel
from typing import List
import json

class Analysis(BaseModel):
    summary: str
    key_points: List[str]
    sentiment: str
    confidence: float

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "structured_example",
        "description": "Analyze text with structured output using Pydantic AI",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"}
            },
            "required": ["text"]
        }
    }
}

def structured_example(text: str) -> str:
    """Example of structured output with minimal code"""
    
    # One line structured LLM call using Pydantic AI!
    analysis = llm_structured(f"Analyze this text: {text}", Analysis)
    
    # Convert to markdown for saving
    markdown = f"""# Analysis Results

## Summary
{analysis.summary}

## Key Points
{chr(10).join(f"- {point}" for point in analysis.key_points)}

## Sentiment: {analysis.sentiment}
**Confidence:** {analysis.confidence}
"""
    
    # Save with one line
    result = save(markdown, "Structured analysis")
    
    return json.dumps({
        "success": True,
        "analysis": analysis.dict(),
        "filepath": result["filepath"],
        "tokens": result["frontmatter"]["tokens"]
    }, indent=2) 