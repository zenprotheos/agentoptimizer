

# Creating an Agent

Create a new agent by adding a markdown file to the `/agents` directory. The file name is used as the agent name. Eg research_agent.md = `research_agent`

# Agent Definition: Configuration and Prompting

An agent consists of two parts:
1.  **YAML Frontmatter**: The technical configuration (model, tools, parameters).
2.  **System Prompt**: The agent's "soul." This is where you define its identity, rules, and approach using the structured, tag-based format.

## 1. Agent Configuration (YAML Frontmatter)

The frontmatter defines the agent's technical parameters. While many are optional (and will fall back to `config.yaml` defaults), being explicit gives you precise control.

```markdown
---
name: my_agent # should match name of file, eg agent_name.md
description: "Brief description of what this agent does"
model: openai/gpt-4.1-mini    # Optional: overrides config.yaml default
tools:                      # Optional: list of tools this agent can use
  - web_search
  - web_read_page
---

{Agent instructions go here}

```

### Selecting & configuring the Agent's model

If no model params are selected, the Agent will use the defaults in config.yaml.

The main params to consider are: model, temperature, max_tokens but if the user wants other model params included you can do so.

#### Model name - can be overridden per agent

Naming convention is provider_name/model_name
`model: "openai/gpt-4.1-mini"`

Pick the right model for the job:

openai/gpt-4.1-mini: 




temperature: 0.7          # 0.0 = deterministic, higher = more creative
max_tokens: 2048          # Maximum tokens to generate



### Allocating tools to agents

An agent's capabilities are determined by the tools they have available. You allocate tools to an agent in the `tools` section of the agent config frontmatter.

```yaml
---
name: research_agent
description: "Deep research specialist that conducts comprehensive, iterative research using structured WIP document management"
model: openai/gpt-4.1-mini
tools:
  - research_prompt_rewriter
  - research_planner
  - wip_doc_read
  - wip_doc_create
  - wip_doc_edit
  - web_search
  - web_read_page
---
```

Each tool has rich tool metadata that describe what the tool does(tool description) and how to use it (parameter descriptions). 

Example: 
```python
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "read_file_contents",
        "description": "Use this tool to read the full content of markdown or JSON files in the artifacts directory",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file in the artifacts directory (e.g., 'ec3aa3b5/20250725_083525_results.md' or '1910ea06/20250725_084543_results.json')"
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Whether to include metadata, incl token count, about the file in the response (default: true)",
                    "default": True
                }
            },
            "required": ["filepath"]
        }
    }
}
```

#### How to decide which tools to allocate

Think step by step about what you are designing the agent for and only allocate the tools that it is going to need for completing its tasks successfully. The more tools you allocate, the more potential there is for confusion and the more context is used up.

Before allocating tools, first call your `list_tools` mcp tool to see what tools are available and how they work.







### Recommended models









## 2. Agent Instructions (System Prompt)

It is critical that we provide out agents with carefully constructed instructions that outline their role, goals, process, constraints, etc.

This guide helps AI coding agents create effective specialist agents for knowledge work tasks like research, writing, and analysis.

### 1. Identity & Purpose Block
Start with clear identity. Best agents establish purpose immediately.

**Example Pattern:**
```
You are [agent_name], a specialist agent focused on [primary_task].

You excel at:
1. [Capability 1 - specific, measurable]
2. [Capability 2 - specific, measurable]
3. [Capability 3 - specific, measurable]
```

### 2. Specific Goals Block

Define the specific approach to achieving the agent's goals, using proven patterns for that kind of agent.

For example a research agent may include this speciic approach:

```
You operate through these steps:
1. Analyze Request: Parse user needs, identify key requirements
2. Plan Approach: Break down into subtasks, identify tools needed
3. Execute: Gather information systematically using available tools
4. Synthesize: Combine findings into coherent insights
5. Deliver: Present results in requested format with clear structure
6. Iterate: Refine based on feedback or additional requirements
```

Note, this is separate to the agent_loop block which is generic, and describes the overall control flow.

### 3. Agent Loop Block

The `agent_loop` block describes the control flow of the agent. It explains how the agent should orchestrate its tool calling in an iterative loop. For each loop the agent is analysing the current state, choosing one precise action, then responding to its result—rather than attempting to solve everything at once. This disciplined loop ensures that each decision is grounded in updated context and leads progressively toward task completion.

The `agent_loop` block is provided below. You can include it as a snippet in the agent instructions, using: `{% include "agent_loop.md" %}`

```markdown
<agent_loop>
You operate in an iterative agent loop. Your job is to complete tasks effectively by making deliberate, accurate tool calls and reasoning through each step. Follow this cycle:
1. Analyze Events: Interpret the message stream to determine the user's current needs and task state. Consider:
   - Instructions from the Orchestrator Agent  
   - Relevant content or artifacts provided to you 
   - Results of prior tool calls  
Maintain a working model of the task’s progress and outstanding requirements.
1. Plan: Carefully plan your moves by considering what needs to be done and what tools you have to achieve that. Pay attention to the tool description and parameter description to understand its capabilities and calling requirements.
2. Select Tools: Choose the tool/s that is most appropriate for executing your next step. Base your selection on:
   - Your plan from step 2  
   - The tool's capabilities and requirements  
   - The current state of task data  
Prepare clean, valid inputs. Be precise and minimal.
1. Wait for Execution: Selected tool action will be executed in local sandbox environment with new tool response outputs added to the message stream.
2. Reflect on the new output. Assess:
   - Whether the last step succeeded  
   - What new information has emerged  
   - Whether your working plan needs to be revised  
3. Iterate: Choose only one tool per iteration, patiently repeat above steps until task completion
4. Submit Results: Once the task is complete, prepare your output. Include:
   - Final artifacts (as file paths)
   - A summary of how the task was solved, if useful  
Send these to the Orchestrator Agent to signal task completion.
</agent_loop>
```


## `<general_guidelines>`: Set The Ground Rules
Use this section for universal rules that apply to all tasks. Negative constraints (`NEVER`, `DO NOT`) are extremely powerful for preventing undesirable behavior.

**Example combining best practices from `Cursor` and `Cluely`:**
```markdown
<general_guidelines>
- **NEVER refer to tool names when speaking to the USER.** For example, instead of saying 'I need to use the edit_file tool', just say 'I will edit your file'.
- NEVER use meta-phrases (e.g., "let me help you", "I can see that").
- NEVER lie or make up facts. If you are unsure, state your uncertainty.
- ALWAYS use markdown formatting for clarity.
- DO NOT add additional code explanation summary unless requested by the user. After working on a file, just stop, rather than providing an explanation of what you did.
</general_guidelines>
```


## File Passing and Context Management

### Overview
The oneshot system is designed to have agents perform useful knowledge work for a user. They do that by generating valuable artifacts. Artifacts include documents like reports, analysis, project plans, emails, articles, posts, and more. In most cases these are files saved to the user's computer. Oneshot's default location for saving these outputs is the `artifacts` directory.

Ordinarily an agent would have to generate very long user messages containing the content that it wants to provide to a given tool or sub-agent. The oneshot system, however, is designed to preserve an agent's context window wherever possible by passing files between agents, using filepaths.  Agents can then read those files or pass them into their tools without having to add them to the context window. This allows agents to keep their main thread context window clean while spinnging off tool and agents to process large blocks of content. This enables efficient multi-agent workflows and keeps a high signal to noise ratio in an agent's cotext window (ie the messages stream).

Files should be passed using their absolute path. New file outputs from tools get saved to the artifacts dir.


## Usage of snippets

There are other helpful agent instruction boilerplate snippets available in the `snippets` dir which you can include with the jinja2 format `{% include "snippet_name.md" %}`




Usage of file passing
Usage of sub agents
Usage of wip documents
Usage of todos

Using the tool_services