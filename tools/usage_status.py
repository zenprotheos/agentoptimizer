#!/usr/bin/env python3
"""
Tool: usage_status
Description: Get current usage statistics and remaining limits for this agent run

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.usage_status import usage_status
result = usage_status()
print(result)
"
"""

import os
import json
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "usage_status",
        "description": "Get current usage statistics and remaining limits for this agent run. This tool helps agents monitor their resource usage and make intelligent decisions about task complexity and depth. Useful for long-running tasks that might approach usage limits.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

def usage_status() -> str:
    """
    Get current usage statistics and remaining limits for this agent run.
    
    Returns:
        JSON string containing:
        - current_requests: Number of requests used so far
        - request_limit: Maximum requests allowed
        - remaining_requests: Requests remaining
        - usage_percentage: Percentage of limit used
        - status: Usage status (low, medium, high, critical)
        - recommendations: Suggested actions based on usage
    """
    
    try:
        # Get usage context from environment variables
        current_requests = int(os.getenv('ONESHOT_CURRENT_REQUESTS', 0))
        request_limit = int(os.getenv('ONESHOT_REQUEST_LIMIT', 30))
        
        # Note: current_requests tracks tool calls made so far
        # This may not exactly match Pydantic AI's request count, but gives a good approximation
        
        # Calculate derived metrics
        remaining_requests = max(0, request_limit - current_requests)
        usage_percentage = int((current_requests / request_limit) * 100) if request_limit > 0 else 0
        
        # Determine status and recommendations
        if usage_percentage < 50:
            status = "low"
            recommendations = [
                "Usage is low - you can continue with complex tasks",
                "Consider conducting thorough research or analysis",
                "No immediate concerns about hitting limits"
            ]
        elif usage_percentage < 75:
            status = "medium" 
            recommendations = [
                "Usage is moderate - be mindful of task complexity",
                "Focus on essential tasks and avoid unnecessary tool calls",
                "Consider prioritizing most important work"
            ]
        elif usage_percentage < 90:
            status = "high"
            recommendations = [
                "Usage is high - approach limit carefully",
                "Focus only on essential tasks",
                "Consider wrapping up current work soon",
                "Avoid starting new complex subtasks"
            ]
        else:
            status = "critical"
            recommendations = [
                "Usage is critical - very close to limit",
                "Complete current task quickly and summarize findings",
                "Avoid any non-essential tool calls",
                "Prepare to hand off unfinished work with clear status"
            ]
        
        usage_info = {
            "current_requests": current_requests,
            "request_limit": request_limit,
            "remaining_requests": remaining_requests,
            "usage_percentage": usage_percentage,
            "status": status,
            "recommendations": recommendations,
            "timestamp": llm("What is the current timestamp in ISO format? Just return the timestamp, nothing else.")
        }
        
        return json.dumps(usage_info, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get usage status: {str(e)}",
            "current_requests": "unknown",
            "request_limit": "unknown",
            "status": "unknown"
        }, indent=2)


# Test the tool if run directly
if __name__ == "__main__":
    # Test usage status
    test_result = usage_status()
    print("Usage Status Test:")
    print(test_result)
