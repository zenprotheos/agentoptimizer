# How to Make Tools: Complete Guide for AI Coding Assistants

## Overview

This guide teaches you how to create powerful, minimal-code tools using the `app/tool_helper.py` system. Tools built with this system integrate seamlessly with the Pydantic AI-powered agent framework and require minimal boilerplate code.

## Core Principles

1. **Minimal Code**: Most tools require only 10-20 lines of actual logic
2. **Single Import**: `from app.tool_helper import *` gives you everything
3. **Automatic Metadata**: File saving includes YAML frontmatter, token counting, and summaries
4. **Error-Free**: The helper handles all error cases gracefully
5. **Consistent Structure**: All tools follow the same pattern

## Tool Structure Template

Every tool follows this exact structure:

```python
# tools/your_tool_name.py
from app.tool_helper import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "your_tool_name",
        "description": "Clear description of what the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Description of param1"},
                "param2": {"type": "integer", "description": "Description of param2", "default": 5}
            },
            "required": ["param1"]
        }
    }
}

def your_tool_name(param1: str, param2: int = 5) -> str:
    """Tool function with clear docstring"""
    
    # Your tool logic here (typically 5-15 lines)
    
    return json.dumps({"success": True, "result": "your_result"}, indent=2)
```

## Available Helper Functions

After `from app.tool_helper import *`, you have access to:

| Function | Purpose | Example |
|----------|---------|---------|
| `llm(prompt, **kwargs)` | Basic LLM call | `llm("Summarize this text")` |
| `llm_json(prompt, **kwargs)` | LLM returning JSON | `llm_json("List 3 colors as JSON")` |
| `llm_structured(prompt, Model, **kwargs)` | Structured Pydantic output | `llm_structured("Analyze", Analysis)` |
| `chain_prompts(prompts, **kwargs)` | Multi-step conversation | `chain_prompts(["Step 1", "Step 2"])` |
| `save(content, description, filename)` | Save with run-aware organization | `save(text, "Analysis results")` |
| `read(filepath)` | Read any file | `read("data.txt")` |
| `template(template_str, **context)` | Jinja2 templating | `template("Hello {{name}}", name="AI")` |
| `api(url, method, **kwargs)` | HTTP requests with auto-auth | `api("https://api.example.com")` |
| `set_run_id(run_id)` | Set current run ID for file organization | `set_run_id("a1b2c3d4")` |
| `get_run_id()` | Get current run ID | `get_run_id()` |

## Run-Aware Artifact Organization

The tool helper system automatically organizes generated files by conversation run:

- **Files are saved to `/artifacts/{run_id}/`** instead of a flat directory
- **Run ID is included in file frontmatter** for educational traceability
- **Multiple files from the same conversation are grouped together**
- **Easy correlation with conversation history** in `/runs/{run_id}/`

### How It Works

When an agent runs, the system automatically:
1. Sets the current run ID in the tool helper
2. All calls to `save()` use this run ID for organization
3. Files include run_id in their YAML frontmatter
4. Directory structure makes conversation context clear

### Example File Organization

```
/runs/a1b2c3d4/              # Conversation history
├── run.json                 # Complete conversation data
├── messages.json            # Message history
└── metadata.json            # Run summary

/artifacts/a1b2c3d4/         # Files generated during conversation
├── analysis_report.md       # First tool output
├── summary.txt              # Second tool output
└── processed_data.json      # Third tool output
```

### Generated File Structure

Each file saved by `save()` includes comprehensive frontmatter:

```yaml
---
description: Analysis report for user query
created: 2024-01-15T10:32:00Z
tokens: 450
summary: This report analyzes the provided data and offers insights...
run_id: a1b2c3d4
---

[Your file content here]
```

## Tool Examples

### 1. Basic Text Processing Tool

```python
# tools/text_processor.py
from app.tool_helper import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "text_processor",
        "description": "Process and analyze text with AI",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to process"},
                "operation": {"type": "string", "description": "Operation: summarize, analyze, or extract_keywords"}
            },
            "required": ["text", "operation"]
        }
    }
}

def text_processor(text: str, operation: str) -> str:
    """Process text using AI with different operations"""
    
    prompts = {
        "summarize": f"Summarize this text concisely: {text}",
        "analyze": f"Analyze the tone, style, and key themes in this text: {text}",
        "extract_keywords": f"Extract the 10 most important keywords from this text: {text}"
    }
    
    if operation not in prompts:
        return json.dumps({"error": f"Invalid operation. Use: {list(prompts.keys())}"})
    
    result = llm(prompts[operation])
    # save() automatically organizes by run ID and includes run_id in frontmatter
    saved_file = save(result, f"Text {operation} results")
    
    return json.dumps({
        "success": True,
        "operation": operation,
        "result": result,
        "filepath": saved_file["filepath"],
        "run_id": saved_file["run_id"],
        "artifacts_dir": saved_file["artifacts_dir"],
        "tokens": saved_file["frontmatter"]["tokens"]
    }, indent=2)
```

### 2. Structured Data Analysis Tool

```python
# tools/data_analyzer.py
from app.tool_helper import *
from pydantic import BaseModel
from typing import List
import json

class DataInsights(BaseModel):
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    confidence_score: float

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "data_analyzer",
        "description": "Analyze data and provide structured insights",
        "parameters": {
            "type": "object",
            "properties": {
                "data_file": {"type": "string", "description": "Path to data file"},
                "analysis_type": {"type": "string", "description": "Type of analysis to perform"}
            },
            "required": ["data_file", "analysis_type"]
        }
    }
}

def data_analyzer(data_file: str, analysis_type: str) -> str:
    """Analyze data file and return structured insights"""
    
    # Read the data
    data_content = read(data_file)
    
    # Get structured analysis
    insights = llm_structured(
        f"Analyze this {analysis_type} data and provide insights:\n\n{data_content}",
        DataInsights
    )
    
    # Create markdown report
    report = f"""# Data Analysis Report: {analysis_type}

## Summary
{insights.summary}

## Key Findings
{chr(10).join(f"- {finding}" for finding in insights.key_findings)}

## Recommendations
{chr(10).join(f"- {rec}" for rec in insights.recommendations)}

## Confidence Score: {insights.confidence_score}/1.0
"""
    
    saved_file = save(report, f"{analysis_type} analysis report")
    
    return json.dumps({
        "success": True,
        "analysis_type": analysis_type,
        "insights": insights.dict(),
        "report_path": saved_file["filepath"],
        "confidence": insights.confidence_score
    }, indent=2)
```

### 3. Multi-Step Research Tool

```python
# tools/research_assistant.py
from app.tool_helper import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "research_assistant",
        "description": "Conduct multi-step research and create comprehensive reports",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Research topic"},
                "depth": {"type": "string", "description": "Research depth: basic, detailed, or comprehensive", "default": "detailed"}
            },
            "required": ["topic"]
        }
    }
}

def research_assistant(topic: str, depth: str = "detailed") -> str:
    """Conduct multi-step research using prompt chaining"""
    
    depth_prompts = {
        "basic": [
            f"Create a basic research outline for: {topic}",
            "Based on the outline, provide key information for each section",
            "Write a concise summary report"
        ],
        "detailed": [
            f"Create a detailed research outline for: {topic}",
            "Research each section thoroughly with specific details and examples",
            "Analyze the findings and identify key insights",
            "Write a comprehensive report with actionable conclusions"
        ],
        "comprehensive": [
            f"Create an extensive research framework for: {topic}",
            "Conduct deep research for each area with multiple perspectives",
            "Perform critical analysis and identify trends/patterns",
            "Synthesize findings into strategic insights",
            "Create a comprehensive report with executive summary and detailed appendices"
        ]
    }
    
    if depth not in depth_prompts:
        return json.dumps({"error": f"Invalid depth. Use: {list(depth_prompts.keys())}"})
    
    # Execute research chain
    results = chain_prompts(
        depth_prompts[depth],
        system_prompt="You are a thorough research assistant. Provide detailed, accurate information."
    )
    
    # Get final report (last result)
    final_report = results[-1]
    
    # Save the complete research
    saved_file = save(final_report, f"{depth.title()} research on {topic}")
    
    return json.dumps({
        "success": True,
        "topic": topic,
        "depth": depth,
        "steps_completed": len(results),
        "report_path": saved_file["filepath"],
        "tokens": saved_file["frontmatter"]["tokens"],
        "preview": final_report[:200] + "..."
    }, indent=2)
```

### 4. Template-Based Content Generator

```python
# tools/content_generator.py
from app.tool_helper import *
import json
from datetime import datetime

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "content_generator",
        "description": "Generate various types of content using templates",
        "parameters": {
            "type": "object",
            "properties": {
                "content_type": {"type": "string", "description": "Type: email, blog_post, report, or presentation"},
                "topic": {"type": "string", "description": "Main topic or subject"},
                "audience": {"type": "string", "description": "Target audience"},
                "tone": {"type": "string", "description": "Tone: professional, casual, or technical", "default": "professional"}
            },
            "required": ["content_type", "topic", "audience"]
        }
    }
}

def content_generator(content_type: str, topic: str, audience: str, tone: str = "professional") -> str:
    """Generate content using templates and AI"""
    
    templates = {
        "email": """Subject: {{topic}}

Dear {{audience}},

{{content}}

Best regards,
[Your Name]
""",
        "blog_post": """# {{topic}}

## Introduction
{{intro}}

## Main Content
{{content}}

## Conclusion
{{conclusion}}

---
*Published: {{date}}*
""",
        "report": """# {{topic}} - Report

**Audience:** {{audience}}  
**Date:** {{date}}  
**Tone:** {{tone}}

## Executive Summary
{{summary}}

## Detailed Analysis
{{content}}

## Recommendations
{{recommendations}}
""",
        "presentation": """# {{topic}}
*Presentation for {{audience}}*

## Slide 1: Overview
{{overview}}

## Slide 2-N: Main Content
{{content}}

## Final Slide: Key Takeaways
{{takeaways}}
"""
    }
    
    if content_type not in templates:
        return json.dumps({"error": f"Invalid content_type. Use: {list(templates.keys())}"})
    
    # Generate content with AI
    content_prompt = f"Create {tone} {content_type} content about '{topic}' for {audience}. Make it engaging and informative."
    ai_content = llm(content_prompt)
    
    # Use template to format
    formatted_content = template(
        templates[content_type],
        topic=topic,
        audience=audience,
        tone=tone,
        content=ai_content,
        date=datetime.now().strftime("%Y-%m-%d"),
        intro="[AI will fill this]",
        conclusion="[AI will fill this]",
        summary="[AI will fill this]",
        recommendations="[AI will fill this]",
        overview="[AI will fill this]",
        takeaways="[AI will fill this]"
    )
    
    # Enhance with AI for missing sections
    final_content = llm(f"Complete this {content_type} by filling in any placeholder sections:\n\n{formatted_content}")
    
    saved_file = save(final_content, f"{content_type.title()} about {topic}")
    
    return json.dumps({
        "success": True,
        "content_type": content_type,
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "filepath": saved_file["filepath"],
        "tokens": saved_file["frontmatter"]["tokens"]
    }, indent=2)
```

### 5. API Integration Tool

```python
# tools/api_processor.py
from app.tool_helper import *
import json

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "api_processor",
        "description": "Fetch data from APIs and process with AI",
        "parameters": {
            "type": "object",
            "properties": {
                "api_url": {"type": "string", "description": "API endpoint URL"},
                "processing_task": {"type": "string", "description": "What to do with the API data"},
                "output_format": {"type": "string", "description": "Output format: summary, analysis, or raw", "default": "summary"}
            },
            "required": ["api_url", "processing_task"]
        }
    }
}

def api_processor(api_url: str, processing_task: str, output_format: str = "summary") -> str:
    """Fetch API data and process it with AI"""
    
    try:
        # Fetch data from API (auto-handles auth headers)
        response = api(api_url)
        
        if response.status_code != 200:
            return json.dumps({"error": f"API request failed: {response.status_code}"})
        
        api_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
        # Process with AI based on task
        if output_format == "raw":
            processed_data = api_data
        else:
            prompt = f"Process this API data for the following task: {processing_task}\n\nData: {json.dumps(api_data, indent=2)}"
            processed_data = llm(prompt)
        
        # Save results
        saved_file = save(
            str(processed_data) if output_format == "raw" else processed_data,
            f"API processing: {processing_task}"
        )
        
        return json.dumps({
            "success": True,
            "api_url": api_url,
            "task": processing_task,
            "format": output_format,
            "status_code": response.status_code,
            "filepath": saved_file["filepath"],
            "tokens": saved_file["frontmatter"]["tokens"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Processing failed: {str(e)}"}, indent=2)
```

## Conversation Continuity in Tools

Tools can access conversation context and run information:

### Accessing Run Information

```python
def context_aware_tool(query: str) -> str:
    """Tool that's aware of its conversation context"""
    
    current_run_id = get_run_id()  # Get the current run ID
    
    if current_run_id:
        # Tool can reference its conversation context
        result = llm(f"Based on our ongoing conversation (run {current_run_id}), analyze: {query}")
        saved_file = save(result, f"Contextual analysis for run {current_run_id}")
        
        return json.dumps({
            "success": True,
            "query": query,
            "run_id": current_run_id,
            "filepath": saved_file["filepath"],
            "note": "This analysis considers our conversation context"
        }, indent=2)
    else:
        # Fallback for tools called outside of agent runs
        result = llm(f"Analyze: {query}")
        saved_file = save(result, "Standalone analysis")
        
        return json.dumps({
            "success": True,
            "query": query,
            "run_id": None,
            "filepath": saved_file["filepath"],
            "note": "This is a standalone analysis"
        }, indent=2)
```

### Multi-File Generation

Tools can generate multiple related files in the same conversation:

```python
def comprehensive_analysis_tool(data: str) -> str:
    """Generate multiple related files for comprehensive analysis"""
    
    # Generate different types of analysis
    summary = llm(f"Provide a brief summary of: {data}")
    detailed_analysis = llm(f"Provide detailed analysis of: {data}")
    recommendations = llm(f"Provide actionable recommendations based on: {data}")
    
    # Save all files - they'll be organized in the same run directory
    summary_file = save(summary, "Executive summary", "executive_summary.md")
    analysis_file = save(detailed_analysis, "Detailed analysis", "detailed_analysis.md")
    recommendations_file = save(recommendations, "Recommendations", "recommendations.md")
    
    return json.dumps({
        "success": True,
        "run_id": get_run_id(),
        "files_generated": [
            {"type": "summary", "path": summary_file["filepath"]},
            {"type": "analysis", "path": analysis_file["filepath"]},
            {"type": "recommendations", "path": recommendations_file["filepath"]}
        ],
        "artifacts_dir": summary_file["artifacts_dir"],
        "note": "All files are organized together by conversation run"
    }, indent=2)
```

### Educational Value

The run-aware system provides educational benefits:

1. **Context Correlation**: Users can see which files were generated from which conversations
2. **Progressive Building**: Multiple tool calls in the same conversation build related artifacts
3. **Learning Visibility**: File frontmatter shows the run_id for easy correlation
4. **Organization**: Related files are grouped together automatically

## Best Practices

### 1. Error Handling
Always return JSON with success/error status:
```python
try:
    # Tool logic
    return json.dumps({"success": True, "result": result})
except Exception as e:
    return json.dumps({"error": str(e)}, indent=2)
```

### 2. Parameter Validation
Validate inputs early:
```python
def my_tool(param: str) -> str:
    if not param.strip():
        return json.dumps({"error": "Parameter cannot be empty"})
    # Continue with logic...
```

### 3. Meaningful Descriptions
Use clear, specific descriptions in metadata:
```python
"description": "Analyze customer feedback data and generate insights report with sentiment analysis"
# NOT: "Analyze data"
```

### 4. Consistent Return Format
Always return structured JSON:
```python
return json.dumps({
    "success": True,
    "operation": "data_analysis",
    "result": analysis_result,
    "filepath": saved_file["filepath"],
    "metadata": {"tokens": token_count, "processing_time": elapsed}
}, indent=2)
```

### 5. Use Type Hints
Always include proper type hints:
```python
def my_tool(text: str, count: int = 5) -> str:
```

### 6. Leverage Run Awareness
Include run information in tool responses for educational value:
```python
def my_tool(data: str) -> str:
    result = llm(f"Process: {data}")
    saved_file = save(result, "Processing results")
    
    return json.dumps({
        "success": True,
        "result": result,
        "filepath": saved_file["filepath"],
        "run_id": saved_file["run_id"],  # Include for educational correlation
        "artifacts_dir": saved_file["artifacts_dir"]  # Show organization
    }, indent=2)
```

## Common Patterns

### File Processing Pattern
```python
def process_file_tool(filepath: str, operation: str) -> str:
    content = read(filepath)
    result = llm(f"Perform {operation} on this content: {content}")
    saved = save(result, f"{operation} results")
    return json.dumps({"success": True, "filepath": saved["filepath"]})
```

### Multi-Step Analysis Pattern
```python
def analyze_tool(data: str) -> str:
    steps = ["outline", "analyze", "summarize"]
    prompts = [f"Step {i+1}: {step} this data: {data}" for i, step in enumerate(steps)]
    results = chain_prompts(prompts)
    final = save(results[-1], "Analysis results")
    return json.dumps({"success": True, "steps": len(results), "filepath": final["filepath"]})
```

### Template + AI Pattern
```python
def generate_tool(topic: str) -> str:
    template_str = "# {{topic}}\n\n{{content}}\n\n## Conclusion\n{{conclusion}}"
    content = llm(f"Write about {topic}")
    conclusion = llm(f"Write a conclusion for this content: {content}")
    final = template(template_str, topic=topic, content=content, conclusion=conclusion)
    saved = save(final, f"Generated content: {topic}")
    return json.dumps({"success": True, "filepath": saved["filepath"]})
```

## Testing Your Tools

Test tools independently:
```python
# Test the tool function directly
if __name__ == "__main__":
    result = your_tool_name("test input")
    print(result)
```

## Summary

With this system, creating powerful tools requires:
1. Copy the template structure
2. Define clear metadata
3. Write 5-15 lines of logic using helper functions
4. Return structured JSON results
5. Leverage run awareness for educational value

The helper handles all complexity: LLM integration, file operations, error handling, metadata generation, token counting, and **run-aware artifact organization**. 

### Key Benefits:

- **Educational Organization**: Files are automatically grouped by conversation
- **Context Correlation**: Easy to understand which files came from which conversations
- **Progressive Building**: Multiple tool calls build related artifacts together
- **Visible Traceability**: Run IDs in frontmatter connect files to conversation history

Focus on your tool's unique logic, not boilerplate code. The system automatically handles conversation continuity and artifact organization for an optimal educational experience. 