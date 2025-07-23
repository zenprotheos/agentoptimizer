# tools/chain_example.py
# Example tool showing prompt chaining with Pydantic AI

from app.tool_helper import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "chain_example",
        "description": "Research and write using prompt chaining with Pydantic AI",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to research and write about"}
            },
            "required": ["topic"]
        }
    }
}

def chain_example(topic: str) -> str:
    """Example of prompt chaining with minimal code"""
    
    # Define the chain of prompts
    prompts = [
        f"Create a detailed research outline for the topic: {topic}",
        "Based on the outline you just created, research each section in detail and provide comprehensive information.",
        "Using the research you've compiled, write a well-structured, engaging article."
    ]
    
    # Execute the chain with one line using Pydantic AI conversation!
    results = chain_prompts(prompts, system_prompt="You are a research assistant and writer.")
    
    # Get the final article (last result)
    article = results[-1]
    
    # Save with metadata
    result = save(article, f"Article about {topic}")
    
    return json.dumps({
        "success": True,
        "topic": topic,
        "filepath": result["filepath"],
        "tokens": result["frontmatter"]["tokens"],
        "preview": article[:200] + "...",
        "chain_steps": len(results)
    }, indent=2) 