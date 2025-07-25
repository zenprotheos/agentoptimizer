# tools/structured_search.py
# Structured search tool using OpenAI GPT-4o-mini-search-preview model

from app.tool_services import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "structured_search",
        "description": "Use this tool to perform a web search via an AI search agent (OpenAI's GPT-4o-search) to return structured data matching a JSON schema that you define. Best for: real-time data extraction, multi-source aggregation, fact verification. The agent interprets your query, searches multiple sources, and synthesizes results into your schema. The response is saved to a json file and the filepath is returned to you.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string", 
                    "description": "The search query that you want the search agent to perform. Treat this as a prompt to an intelligent search agent. Be clear about what information you want the search agent to return."
                },
                "schema": {
                    "type": "string", 
                    "description": "Use a JSONC schema that defines the structure of the search results required. In your JSONC schema, the key you use should be the actual key you want returned; the value should be a realistic examplar of a value that you could expect to be returned; the comment should be a description of how the required value should be derived and formatted. Example: {\"match\": \"The Lions vs Wallabies\", // the name of the match being played on the Lions tour, in the format `The Lions` vs `name of the other team`\"}"
                }
            },
            "required": ["query", "schema"]
        }
    }
}

def structured_search(query: str, schema: str) -> str:
    """Perform structured search using GPT-4o-mini-search-preview model"""
    
    try:
        # Handle JSONC schema (JSON with comments) by removing comments
        schema_clean = schema
        # Remove single-line comments
        schema_clean = '\n'.join([line.split('//')[0].rstrip() for line in schema_clean.split('\n')])
        # Remove multi-line comments (basic handling)
        schema_clean = schema_clean.replace('/*', '').replace('*/', '')
        
        # Parse the schema to validate it's valid JSON
        try:
            schema_dict = json.loads(schema_clean)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Invalid JSON schema: {str(e)}",
                "schema_provided": schema,
                "cleaned_schema": schema_clean
            }, indent=2)
        
        # Create the search prompt with schema instructions
        search_prompt = f"""Perform a structured search for: "{query}"

Return results that match this JSON schema structure:
{json.dumps(schema_dict, indent=2)}

The schema uses example values to show the expected format. Provide comprehensive, accurate search results that fit the specified structure. Return only valid JSON that matches the schema exactly."""

        # Use the GPT-4o-mini-search-preview model for structured search
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
                        pass  # Keep the original error response
        
        # Save results to file as JSON
        saved_file = save_json(search_results, f"Structured search results for: {query}")
        
        return json.dumps({
            "success": True,
            "query": query,
            "schema": schema_dict,
            "results": search_results,
            "filepath": saved_file["filepath"],
            "run_id": saved_file["run_id"],
            "tokens": saved_file["frontmatter"]["tokens"],
            "model_used": "openai/gpt-4o-mini-search-preview"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Structured search failed: {str(e)}",
            "query": query,
            "schema": schema
        }, indent=2) 