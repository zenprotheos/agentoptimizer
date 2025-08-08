#!/usr/bin/env python3
"""
Tool: search_analyst
Description: This tool allows research agents to delegate focused search tasks to a specialised search analyst agent that has access to web search and other databases like arxiv and bioarxiv.

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.search_analyst import search_analyst
result = search_analyst('Find information about GPT-5 models', context='Testing', max_sources=3)
print(result)
"
"""

# tools/search_analyst.py
# Specialized tool that allows research agents to delegate focused search tasks to a search analyst sub-agent

import subprocess
import json
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "search_analyst",
        "description": """Delegate focused search and analysis tasks to a specialized search analyst agent that has access to web search and other databases like arxiv and bioarxiv. 
        
Use this tool when you need:
- Deep investigation of a specific topic with 10+ sources
- Verification of claims with independent sources  
- Parallel research on a narrow topic while you work on other sections
- Technical or specialized searches requiring focused attention
- Fact-checking with contradictory source analysis

The search analyst will return synthesized findings with citations that you can integrate into your research.""",
        "parameters": {
            "type": "object",
            "properties": {
                "research_brief": {
                    "type": "string",
                    "description": """Clear, specific research brief for the search analyst. Include:
                    - Exactly what to research
                    - Types of sources to prioritize  
                    - Specific data points or metrics needed
                    - Any claims to verify or contradict
                    - Expected output format"""
                },
                "context": {
                    "type": "string",
                    "description": "Optional context about the larger research project to help analyst understand significance",
                    "default": ""
                },
                "max_sources": {
                    "type": "integer",
                    "description": "Maximum number of sources to find and analyze (default: 15)",
                    "default": 15
                },
                "focus_area": {
                    "type": "string",
                    "enum": ["technical", "market", "academic", "news", "government", "general"],
                    "description": "Primary type of sources to prioritize",
                    "default": "general"
                },
                "run_id": {
                    "type": "string",
                    "description": "Optional run ID to continue a previous conversation with the search analyst agent",
                    "default": ""
                }
            },
            "required": ["research_brief"]
        }
    }
}

def search_analyst(
    research_brief: str,
    context: str = "",
    max_sources: int = 15,
    focus_area: str = "general",
    run_id: str = ""
) -> str:
    """
    Delegate a focused search task to a specialized search analyst agent.
    
    The search analyst has access to:
    - web_search: For finding relevant sources
    - web_read_page: For reading full content
    - citation management: For tracking sources
    
    Returns synthesized findings with citations ready for integration.
    """
    
    try:
        # Get project root
        project_root = Path(__file__).parent.parent
        agent_script = project_root / "app" / "oneshot"
        
        if not agent_script.exists():
            return json.dumps({
                "success": False,
                "error": f"Agent script not found at {agent_script}. This tool requires the 'oneshot' script in the app directory.",
                "task_id": str(uuid.uuid4())[:8]
            }, indent=2)
        
        # Craft the message for the search analyst
        analyst_message = f"""You are a specialized search analyst. Your task is to conduct focused research and provide synthesized findings with citations.

RESEARCH BRIEF:
{research_brief}

{f"PROJECT CONTEXT: {context}" if context else ""}

REQUIREMENTS:
- Find and analyze up to {max_sources} relevant sources
- Focus on {focus_area} sources primarily
- Provide synthesized findings, not just a list of sources
- Include specific data points, quotes, and statistics
- Add inline citations in format: <cite ref="author-year"/>
- Identify any contradictions or conflicting information
- Return findings in a format ready for integration into a larger research document

OUTPUT FORMAT:
1. Key Findings (synthesized narrative with citations)
2. Data Points (specific metrics, statistics)  
3. Contradictions/Limitations (if any)
4. Citations (formatted list of sources)

Focus on depth over breadth. Quality analysis of fewer sources is better than surface-level coverage of many."""

        # Generate a unique task ID for logging/tracking
        task_id = str(uuid.uuid4())[:8]
        
        # Build the command to execute the search analyst agent
        cmd = ["bash", str(agent_script), "search_analyst_agent", analyst_message]
        
        # Add run_id parameter if provided for conversation continuation
        if run_id:
            cmd.extend(["--run-id", run_id])
        
        # Execute the search analyst agent
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Get the full response from the search analyst agent
            analyst_response = result.stdout.strip()
            
            # Save the analysis for audit trail
            analysis_log = {
                "task_id": task_id,
                "research_brief": research_brief,
                "context": context,
                "max_sources": max_sources,
                "focus_area": focus_area,
                "run_id": run_id,
                "analyst_response": analyst_response,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            log_result = save_json(
                analysis_log,
                f"Search analyst task: {task_id}",
                f"search_analyst_{task_id}.json"
            )
            
            # Return the full analyst response directly
            return analyst_response
            
        else:
            error_msg = result.stderr.strip() or "Search analyst execution failed"
            
            return json.dumps({
                "success": False,
                "error": error_msg,
                "task_id": task_id
            }, indent=2)
            
    except subprocess.TimeoutExpired:
        return json.dumps({
            "success": False,
            "error": "Search analyst task timed out after 5 minutes",
            "task_id": str(uuid.uuid4())[:8]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to execute search analyst: {str(e)}",
            "task_id": str(uuid.uuid4())[:8]
        }, indent=2)




# Test the tool if run directly
if __name__ == "__main__":
    # Test search analyst delegation
    test_result = search_analyst(
        research_brief="""Find and analyze techno-economic comparisons of enzymatic vs chemical 
        depolymerization of algal EPS. Focus on:
        - Production costs ($/kg)
        - Process efficiency metrics
        - Scalability assessments
        - Environmental impact comparisons
        Need specific quantitative data from peer-reviewed sources.""",
        context="Part of larger research on algal EPS applications in cosmetics",
        max_sources=10,
        focus_area="academic"
    )
    
    print("Test Result:")
    print(test_result)