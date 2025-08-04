---
name: "Creating Agents"
purpose: "Complete guide for creating effective specialist agents in the Oneshot system"
companion_guides: ["How to Create Tools", "How to Use Tool Services"]
---

# Creating Agents: Complete Guide

## Overview

This guide teaches you how to create powerful specialist agents in the Oneshot system. Agents are purpose-built AI assistants that excel at specific tasks through carefully crafted instructions and appropriate tool allocation.

## Quick Start

To avoid creating duplicate agents, you can check to see the actual agents that already exist and are available, by using your `list_agents` oneshot mcp tool. 

To create a new agent:

1. Create a markdown file in `/agents/` directory (e.g., `research_agent.md`)
2. Add YAML frontmatter with configuration
3. Write system prompt instructions
4. Test with various scenarios

The filename becomes the agent name (e.g., `research_agent.md` → `research_agent`).

## Agent Structure

Every agent consists of two essential parts:

```markdown
---
# YAML Frontmatter: Technical configuration
name: agent_name
description: "What this agent does"
model: openai/gpt-4o-mini
tools:
  - tool_1
  - tool_2
---

# System Prompt: The agent's instructions
You are [agent_name], a specialist agent...

[Detailed instructions here]
```

## Part 1: YAML Frontmatter Configuration

### Basic Configuration

```yaml
---
name: my_agent              # Must match filename (without .md)
description: "Brief description of agent's purpose"
model: openai/gpt-4o-mini   # Optional: overrides config.yaml
tools:                      # Optional: list of available tools
  - web_search
  - save_to_file
---
```

### Model Selection Guide

Choose the right model for your agent's needs:

#### Cost-Effective Models (Recommended for most agents)
```yaml
# Best overall value - recommended default
model: openai/gpt-4o-mini
# $0.40/M input | $1.60/M output

# Alternative for large context windows
model: google/gemini-2.0-flash
# $0.30/M input | $2.50/M output
```

#### High-Performance Models (For complex tasks)
```yaml
# When you need maximum intelligence
model: openai/gpt-4o
# $2/M input | $8/M output

# For very large documents/context
model: google/gemini-2.0-pro
# $1.25/M input | $10/M output
```

### Model Parameters

```yaml
temperature: 0.7      # 0.0 = deterministic, 1.0+ = creative
max_tokens: 2048      # Increase for long outputs (e.g., 8192 for reports)
```

### Tool Allocation Strategy

#### 1. List Available Tools First
```bash
# Use the MCP tool to see what's available
oneshot mcp list_tools
```

#### 2. Allocate Only Necessary Tools
```yaml
tools:
  # Core tools for this agent's purpose
  - primary_tool_1
  - primary_tool_2
  
  # Supporting tools if needed
  - support_tool_1
```

#### 3. Consider Tool Categories

**Research Agents:**
```yaml
tools:
  - web_search
  - web_fetch
  - save_to_file
  - read_file_contents
```

**Writing Agents:**
```yaml
tools:
  - save_to_file
  - read_file_contents
  - wip_doc_create
  - wip_doc_edit
```

**Analysis Agents:**
```yaml
tools:
  - read_file_contents
  - data_analyzer
  - save_to_file
```

## Part 2: System Prompt Instructions

The system prompt is the agent's "soul" - it defines personality, approach, and behavior.

### Structure Template

```markdown
# 1. Identity & Purpose
You are [agent_name], a specialist agent focused on [primary_task].

You excel at:
- [Specific capability 1]
- [Specific capability 2]
- [Specific capability 3]

# 2. Workflow Approach
<workflow>
Your approach to tasks:
1. **Analyze**: [How you understand requirements]
2. **Plan**: [How you break down tasks]
3. **Execute**: [How you perform work]
4. **Deliver**: [How you present results]
</workflow>

# 3. Agent Loop (Include via snippet)

The agent loop is a structured cycle that guides an AI agent to complete complex tasks through a series of deliberate, step-by-step decisions. It operates by analysing the current state of a task via a shared message stream, planning the next action, selecting and invoking tools one at a time, and reflecting on the results before proceeding. The agent builds and updates a working model of the task, reasoning through uncertainty and revising its plan as needed until the goal is met. Final outputs are packaged and returned to the orchestrator for task handoff.

You should always include the agent_loop snippet in the agent's instructions unless there is a reason we would not want the agent to operate autonomously in a continuous loop. 

The snippet to use is: {% include "agent_loop.md" %}

# 4. General Guidelines
<general_guidelines>
- NEVER expose tool names to users
- ALWAYS save substantial outputs to files
- DO NOT provide unnecessary explanations
- MAINTAIN focus on your specialty
</general_guidelines>

# 5. Specific Instructions
[Task-specific guidance here]
```

### Key Instruction Patterns

#### 1. Identity Block Pattern
```markdown
You are Research Specialist, an expert agent that conducts thorough, 
evidence-based research on any topic.

Your core strengths:
- Systematic information gathering from multiple sources
- Critical evaluation of source credibility
- Synthesis of complex information into clear insights
- Iterative refinement based on findings
```

#### 2. Workflow Block Pattern
```markdown
<workflow>
You follow this systematic approach:

1. **Request Analysis**
   - Parse the research question
   - Identify key concepts and scope
   - Determine required depth

2. **Research Planning**
   - Break into research subtasks
   - Identify information sources
   - Create search strategies

3. **Information Gathering**
   - Execute searches systematically
   - Evaluate source quality
   - Extract relevant information

4. **Synthesis & Delivery**
   - Organize findings logically
   - Create comprehensive report
   - Include citations and sources
</workflow>
```

#### 3. Guidelines Block Pattern
```markdown
<general_guidelines>
# Communication Rules
- NEVER mention tool names (say "I'll search for that" not "I'll use web_search")
- AVOID meta-commentary ("Let me help you with that")
- BE direct and action-oriented

# Quality Standards
- ALWAYS verify information from multiple sources
- CITE sources for all claims
- ACKNOWLEDGE uncertainty when appropriate

# Output Management
- SAVE all substantial content to files
- RETURN file paths, not full content
- USE clear, descriptive filenames
</general_guidelines>
```

### Advanced Features

#### Using Snippets

Include reusable instruction blocks:

```markdown
# Include the standard agent loop
{% include "agent_loop.md" %}

# For agents using todos
{% include "todo_management.md" %}

# For agents using WIP documents
{% include "wip_document_management.md" %}
```

#### File Management Instructions

For agents that handle files:

```markdown
<file_management>
# Output Strategy
- Generate all substantial outputs as files in /artifacts
- Use descriptive filenames: YYYYMMDD_HHMMSS_description.md
- Include metadata in file frontmatter

# File Passing
- Accept file paths as input for processing
- Pass file paths (not content) between tools
- Read files only when necessary for processing

# Context Preservation
- Keep main context clean by using file references
- Summarize file contents briefly when reporting
- Use absolute paths for all file operations
</file_management>
```

#### WIP Document Instructions

For iterative document development:

```markdown
<wip_document_usage>
You use WIP (Work-In-Progress) documents for complex, multi-stage writing:

1. **Creation**: Start with document structure and metadata
2. **Iteration**: Edit sections based on research/feedback
3. **Tracking**: Maintain audit trail of changes
4. **Guidance**: Use section briefs and acceptance criteria

WIP documents enable:
- Structured, iterative development
- Clear section-by-section progress
- Collaboration with other agents
- Quality control through acceptance criteria
</wip_document_usage>
```

## Common Agent Patterns

### 1. Research Agent Pattern

```yaml
---
name: research_specialist
description: "Deep research agent for comprehensive topic investigation"
model: openai/gpt-4o-mini
tools:
  - web_search
  - web_fetch
  - save_to_file
  - read_file_contents
---

You are Research Specialist, focused on thorough, evidence-based research.

{% include "agent_loop.md" %}

<workflow>
1. Parse research question → identify scope
2. Create research plan → break into subtasks
3. Gather information → evaluate sources
4. Synthesize findings → create report
5. Save comprehensive results → provide summary
</workflow>

<general_guidelines>
- ALWAYS verify information from multiple sources
- SAVE detailed findings to markdown files
- RETURN concise summaries with file references
</general_guidelines>
```

### 2. Writing Agent Pattern

```yaml
---
name: content_writer
description: "Professional content creation and editing"
model: openai/gpt-4o-mini
max_tokens: 8192
tools:
  - save_to_file
  - read_file_contents
  - wip_doc_create
  - wip_doc_edit
---

You are Content Writer, specializing in clear, engaging content.

{% include "agent_loop.md" %}
{% include "wip_document_management.md" %}

<workflow>
1. Analyze content requirements
2. Create outline/structure
3. Draft content sections
4. Refine and polish
5. Deliver polished document
</workflow>
```

### 3. Analysis Agent Pattern

```yaml
---
name: data_analyst
description: "Data analysis and insight generation"
model: google/gemini-2.0-flash  # Good for large datasets
tools:
  - read_file_contents
  - data_processor
  - save_to_file
  - create_visualization
---

You are Data Analyst, expert at extracting insights from data.

{% include "agent_loop.md" %}

<workflow>
1. Load and examine data
2. Identify patterns and anomalies
3. Perform relevant analyses
4. Generate visualizations
5. Create insight report
</workflow>
```

## Best Practices

### 1. Agent Design Principles

- **Single Responsibility**: Each agent should excel at one type of task
- **Clear Boundaries**: Define what the agent does and doesn't do
- **Tool Minimalism**: Only include necessary tools
- **Output Focus**: Emphasize creating valuable "finished" artifacts

### 2. Instruction Writing Tips

- **Be Specific**: Vague instructions lead to inconsistent behavior
- **Use Examples**: Show don't just tell
- **Negative Constraints**: "NEVER" rules are powerful
- **Test Iteratively**: Refine based on actual usage

### 3. Common Pitfalls to Avoid

- **Tool Overload**: Too many tools confuse the agent
- **Vague Identity**: Unclear purpose leads to poor performance
- **Missing Guidelines**: Agents need clear behavioral rules
- **Context Waste**: Not using file passing effectively

## Testing Your Agent

### 1. Basic Functionality Test
```bash
./oneshot your_agent "Test basic task"
```

### 2. File Handling Test
```bash
./oneshot your_agent "Process this file" --files test.txt
```

### 3. Conversation Continuity Test
```bash
# First message
./oneshot your_agent "Start a research project on AI" --json
# Note the run_id from response

# Continue conversation
./oneshot your_agent "Add more details" --run-id [run_id]
```

### 4. Edge Case Testing
- Test with minimal input
- Test with complex, multi-part requests
- Test error handling
- Test tool coordination

## Agent Examples Library

You can see the actual agents that already exist and are available, by using your `list_agents` oneshot mcp tool. 


## Summary

Creating effective agents requires:

1. **Clear Configuration**: Choose appropriate model and tools
2. **Strong Identity**: Define specific purpose and capabilities
3. **Structured Instructions**: Use proven patterns and blocks
4. **Appropriate Tools**: Allocate only what's needed
5. **Structured Cycle**: Autonomous control flow via the agent_loop
6. **Valuable artifacts**: Prompting and tooling the agent to produce valuable artifacts for the user

Remember: The best agents are specialists, not generalists. Focus on doing one thing exceptionally well rather than many things adequately.

For tool creation and usage, refer to:
- **"How to Create Tools"**: Building custom tools
- **"How to Use Tool Services"**: Leveraging the tool services system