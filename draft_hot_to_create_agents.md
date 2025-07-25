# How to Create World-Class AI Agents

This guide provides an expert-level approach to engineering highly effective, well-prompted agents for the `oneshot` framework. Moving beyond simple instructions, we will leverage proven techniques from world-class AI systems like Cursor, Manus, and Claude-Code. The goal is not just to create agents that *work*, but agents that work with precision, efficiency, and reliability.

## Core Philosophy: Structured, Tag-Based Prompting

The most effective agents are not prompted with simple prose, but with a structured set of instructions, often using XML-style tags. This approach provides clarity, reduces ambiguity, and gives you fine-grained control over the agent's behavior.

**Abandon simple markdown headers.** Instead, structure your agent's system prompt using tagged blocks that define its identity, rules, and workflows.

**Old Way (Less Effective):**
```markdown
# ABOUT YOU
You are a helpful assistant.

## GUIDELINES
Be concise.
```

**New Standard (Highly Effective):**
```markdown
<identity>
You are Cluely, an assistant whose sole purpose is to analyze and solve problems.
</identity>

<general_guidelines>
- NEVER use meta-phrases (e.g., "let me help you", "I can see that").
- ALWAYS be specific, detailed, and accurate.
- ALWAYS use markdown formatting.
</general_guidelines>
```
This structured format is easier for the LLM to parse and adhere to, leading to more consistent and predictable behavior.

---

## Agent Definition: Configuration and Prompt

An agent consists of two parts:
1.  **YAML Frontmatter**: The technical configuration (model, tools, parameters).
2.  **System Prompt**: The agent's "soul." This is where you define its identity, rules, and approach using the structured, tag-based format.

### 1. Agent Configuration (YAML Frontmatter)

The frontmatter defines the agent's technical parameters. While many are optional (and will fall back to `config.yaml` defaults), being explicit gives you precise control.

```yaml
---
name: code_architect_agent
description: "Designs and architects software solutions based on user requirements."
model: "anthropic/claude-3-opus-20240229" # Specify a powerful model for complex reasoning
temperature: 0.2                          # Low temperature for precise, logical output
max_tokens: 4096                          # Allow for detailed architectural documents
tools:                                    # Explicitly list the tools this agent needs
  - file_creator
  - agent_caller
---
```

**Required Fields:**
*   `name`: A unique, descriptive, snake-case identifier for the agent.
*   `description`: A concise explanation of the agent's purpose and capabilities.

**Optional Control Parameters:**
*   `model`: The specific OpenRouter model ID. Choose a model that fits the agent's task (e.g., a powerful model for coding, a fast model for classification).
*   `temperature`: Controls creativity. Use low values (e.g., `0.1` - `0.3`) for factual, code-related, or analytical tasks. Use higher values (e.g., `0.7` - `0.9`) for creative or brainstorming tasks.
*   `max_tokens`: The maximum length of the agent's response.
*   `tools`: A list of tool names the agent is permitted to use. **Best Practice:** Only grant the tools absolutely necessary for the agent's defined role to reduce complexity and improve security.

### 2. The System Prompt: Crafting the Agent's Mind

This is the most critical part of creating an effective agent. Use the following tagged sections to build a comprehensive and robust prompt.

#### `<identity>` and `<purpose>`: Define the Agent's Core
Start by giving the agent a clear and specific identity. This is more than just a name; it's their fundamental purpose and personality.

**Example from `Cluely`:**
```markdown
<core_identity>
You are an assistant called Cluely, developed and created by Cluely, whose sole purpose is to analyze and solve problems asked by the user or shown on the screen. Your responses must be specific, accurate, and actionable.
</core_identity>
```

**Example from `Trae AI`:**
```markdown
<identity>
You are Trae AI, a powerful agentic AI coding assistant. You are exclusively running within a fantastic agentic IDE, you operate on the revolutionary AI Flow paradigm, enabling you to work both independently and collaboratively with a user.
</identity>

<purpose>
Currently, user has a coding task to accomplish, and the user received some thoughts on how to solve the task. Now, please take a look at the task user inputted and the thought on it. You should first decide whether an additional tool is required to complete the task or if you can respond to the user directly.
</purpose>
```

#### `<agent_loop>` or `<workflow>`: Describe How the Agent Operates
Explain the agent's internal thought process or operational loop. This helps the LLM understand its own lifecycle and execute tasks methodically.

**Example from `Manus Agent`:**
```markdown
<agent_loop>
You are operating in an agent loop, iteratively completing tasks through these steps:
1. Analyze Events: Understand user needs and current state through event stream, focusing on latest user messages and execution results
2. Select Tools: Choose next tool call based on current state, task planning, relevant knowledge and available data APIs
3. Wait for Execution: Selected tool action will be executed by sandbox environment with new observations added to event stream
4. Iterate: Choose only one tool call per iteration, patiently repeat above steps until task completion
5. Submit Results: Send results to user via message tools, providing deliverables and related files as message attachments
</agent_loop>
```

#### `<general_guidelines>`: Set The Ground Rules
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

#### `<tool_calling>`: Provide Explicit Instructions for Tool Use
This is a critical section for any agent that uses tools. Be extremely specific about when, why, and how tools should be used.

**Example from the `Cursor` prompt, emphasizing parallelization:**
```markdown
<tool_calling>
You have tools at your disposal to solve the coding task. Follow these rules regarding tool calls:
1. ALWAYS follow the tool call schema exactly as specified and make sure to provide all necessary parameters.
2. The conversation may reference tools that are no longer available. NEVER call tools that are not explicitly provided.
3. If you make a plan, immediately follow it, do not wait for the user to confirm or tell you to go ahead.
4. **CRITICAL INSTRUCTION: For maximum efficiency, whenever you perform multiple operations, invoke all relevant tools simultaneously rather than sequentially.** Prioritize calling tools in parallel whenever possible. For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into context at the same time.
5. **DEFAULT TO PARALLEL:** Unless you have a specific reason why operations MUST be sequential (output of A required for input of B), always execute multiple tools simultaneously.
</tool_calling>
```

**Example from `Claude-Code`, specifying when NOT to use a tool:**```markdown
When NOT to use the Agent tool:
- If you want to read a specific file path, use the view_file or read_file tool instead of the Agent tool, to find the match more quickly
- If you are searching for a specific class definition like "class Foo", use the find_symbol tool instead, to find the match more quickly
```

#### `<task_specific_rules>`: Create Specialized Behavior
For complex agents, create dedicated sections for different tasks. This allows you to define nuanced behavior for each context.

**Example inspired by `Cluely` for a coding agent:**
```markdown
<coding_rules>
- START IMMEDIATELY WITH THE SOLUTION CODE – ZERO INTRODUCTORY TEXT.
- LITERALLY EVERY SINGLE LINE OF CODE MUST HAVE A COMMENT, on the following line for each, not inline. NO LINE WITHOUT A COMMENT.
- After the solution, provide a detailed markdown section explaining the time/space complexity and algorithmic approach.
- NEVER output code directly to the USER. Instead use one of the code edit tools to implement the change.
</coding_rules>

<debugging_rules>
1. Address the root cause instead of the symptoms.
2. Add descriptive logging statements and error messages to track variables and code state.
3. If you fail after multiple attempts (>3), ask the user for help.
</debugging_rules>
```

---

## File Handling and Multi-Agent Workflows

The `oneshot` framework is designed for powerful, file-based multi-agent workflows. An agent's output (a file) can become the input for another, without the expensive process of regenerating content into a context window.

**To make your agent file-aware, you MUST include the Jinja2 snippet `{% include "provided_content.md" %}` in your system prompt.**

This snippet is a placeholder where `agent_template_processor.py` will inject the content of any files passed to the agent.

### Example File-Aware Agent Prompt (`analyst_agent.md`)

```markdown
---
name: analyst_agent
description: "Receives text documents and produces structured analysis."
model: "anthropic/claude-3-haiku-20240307"
temperature: 0.1
tools:
  - file_creator
---

<identity>
You are a meticulous analyst. Your purpose is to read provided documents, identify key themes, and generate a structured JSON summary of your findings.
</identity>

<workflow>
1.  Acknowledge that content has been provided via the file-passing system.
2.  Analyze the full text of the provided content.
3.  Identify the top 5 key themes and 3 actionable insights.
4.  Construct a JSON object containing this analysis.
5.  Use the `file_creator` tool to save this JSON object to a file named `analysis_output.json`.
6.  Respond to the user with a confirmation message stating that the analysis is complete and has been saved to the file.
</workflow>

## PROVIDED CONTENT
The following content has been passed to you for analysis.

{% include "provided_content.md" %}

```

### Multi-Agent Best Practices
1.  **Atomicity:** Design agents to perform one specific task well (e.g., research, analysis, writing).
2.  **Structured I/O:** Agents should consume structured data (like markdown or code files) and produce structured data.
3.  **Efficiency:** Pass file handles, not raw text. Design your agents' final responses to be concise summaries (e.g., "Analysis complete, see `analysis.md`"), leaving the detailed output in the saved files for the next agent in the chain.

---

## Final Checklist and Best Practices

1.  **Use a Structured, Tag-Based Prompt:** This is the most critical change for creating robust agents.
2.  **Define a Clear Identity and Purpose:** Give your agent a specific role and persona.
3.  **Set Explicit Guardrails:** Use `NEVER` and `ALWAYS` to enforce constraints. Don't leave behavior to chance.
4.  **Grant Minimal Tool Access:** Only provide the tools essential for the agent's function.
5.  **Provide Detailed Tooling Instructions:** Explain when, why, and how to use tools, including parallelization strategies and negative constraints.
6.  **Design for File-Based Workflows:** Use `{% include "provided_content.md" %}` and design agents to produce files as their primary output.
7.  **Be Specific:** Vague instructions like "make the code better" are useless. Specific instructions like "refactor the function to be less than 30 lines and ensure it has 100% test coverage" are effective.
8.  **Borrow from the Best:** When in doubt, review the `agent_exemplars.md` and `claude_code` files to see how world-class agents are prompted.