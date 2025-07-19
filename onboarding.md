# Oneshot Agent System - Coding Agent Onboarding Guide

## Philosophy: Primum Non Nocere (First, Do No Harm)

**CRITICAL PRINCIPLE**: Before making ANY changes to the core application code in `/app`, you MUST diagnose the root cause of issues using the diagnostic tools and resources outlined in this document. Most problems are configuration, environment, or usage issues - NOT core application bugs.

### Common Failure Pattern to AVOID
❌ User reports issue → Agent immediately modifies `/app` code → Core system breaks → User loses confidence

✅ **Correct Approach**: User reports issue → Agent investigates using diagnostics → Identifies root cause → Makes minimal, targeted fix

## System Architecture Overview

The oneshot system is built on **Pydantic AI** and consists of:

1. **Core Application** (`/app/agent_runner.py`) - The Pydantic AI-based agent execution engine
2. **MCP Server** (`agent_mcp.py`) - Exposes agent functionality via Model Context Protocol
3. **Agent Definitions** (`/agents/*.md`) - Markdown-based agent configurations
4. **Tools** (`/tools/*.py`) - Python modules providing agent capabilities
5. **Configuration** (`config.yaml`) - System configuration and tool assignments

### Key Components
- **Pydantic AI**: Handles LLM integration, tool orchestration, and agent execution
- **OpenRouter**: LLM gateway (requires API key)
- **Logfire**: Observability and debugging (requires project token)
- **FastMCP**: MCP server framework for tool exposure

## Diagnostic Methodology

### Step 1: Check System Health
Before investigating specific issues, verify basic system health:

```bash
# Test the agent CLI directly
./agent web_agent "hello"

# Test MCP server functionality
python3 -c "from app.mcp_modules.agents import list_agents; print(list_agents('.'))"
```

### Step 2: Use Logfire for Investigation
Logfire is your primary diagnostic tool. Common queries:

```python
# Check recent errors
mcp_logfire_arbitrary_query(
    query="SELECT start_timestamp, message, exception_message FROM records WHERE is_exception = true OR level >= 40 ORDER BY start_timestamp DESC LIMIT 10",
    age=60
)

# Check token usage and API calls
mcp_logfire_arbitrary_query(
    query="SELECT start_timestamp, span_name, attributes->>'gen_ai.usage.input_tokens' as input_tokens FROM records WHERE service_name = 'oneshot' ORDER BY start_timestamp DESC LIMIT 10",
    age=30
)

# Look for specific tool failures
mcp_logfire_arbitrary_query(
    query="SELECT start_timestamp, span_name, message, attributes FROM records WHERE span_name LIKE '%tool%' AND start_timestamp >= NOW() - INTERVAL '1 hour'",
    age=60
)
```

### Step 3: Verify Environment Configuration
Check for missing credentials or configuration:

```python
import os
print("OpenRouter API Key:", "✓" if os.getenv("OPENROUTER_API_KEY") else "✗ MISSING")
print("Logfire Token:", "✓" if os.getenv("LOGFIRE_TOKEN") else "✗ MISSING")
```

### Step 4: Access Documentation When Needed
For deeper understanding of Pydantic AI or OpenRouter issues, use Context7:

```python
# Get Pydantic AI documentation for agent-related issues
mcp_context7_get-library-docs(
    context7CompatibleLibraryID="/context7/ai_pydantic_dev",
    topic="agents"
)

# Get OpenRouter documentation for API-related issues  
mcp_context7_get-library-docs(
    context7CompatibleLibraryID="/context7/openrouter_ai", 
    topic="api"
)
```

## Common Issues and Diagnostic Patterns

### Issue: "Agent not responding" or "MCP server not working"
**Before touching code**, check:
1. Is the bash script executable? `ls -la agent`
2. Are environment variables set? Check `.env` file
3. Is the MCP server calling the bash script correctly?
4. Check Logfire for subprocess errors

**Diagnostic Commands**:
```bash
# Test bash script directly
./agent --help

# Test MCP server Python import
python3 -c "import agent_mcp; print('MCP imports OK')"
```

### Issue: "Tool not found" or "Tool execution failed"
**Root causes** (in order of likelihood):
1. Tool not properly imported in `config.yaml`
2. Tool file missing or has syntax errors
3. Tool dependencies not installed
4. Tool trying to access missing environment variables

**Investigation**:
```python
# Check tool loading
from app.agent_runner import load_tools
tools = load_tools(Path('.'), ['tool_name'])
print(f"Loaded tools: {list(tools.keys())}")
```

### Issue: "LLM API errors" or "401/403/404 from OpenRouter"
**Root causes**:
1. Missing or invalid `OPENROUTER_API_KEY`
2. Insufficient credits/quota
3. Invalid model name in agent configuration
4. Network connectivity issues

**Investigation**: Check Logfire for HTTP response codes and error messages.

### Issue: "Agent gives poor responses"
**Root causes**:
1. Poor system prompt in agent definition
2. Wrong tools assigned to agent
3. Model not suitable for task
4. Context window exceeded

**Investigation**: Check token usage in Logfire and review agent's `.md` file.

## Resource Utilization Guide

### 1. Pydantic AI Documentation
- **When to use**: Understanding agent architecture, tool integration, model configuration
- **Key sections**: Agent creation, tool binding, model settings
- **Access**: Use Context7 MCP server with library ID `/context7/ai_pydantic_dev` (most comprehensive with 1554 code snippets) or `/pydantic/pydantic-ai` (official with 366 code snippets)
- **Example**: `mcp_context7_get-library-docs` with `context7CompatibleLibraryID="/context7/ai_pydantic_dev"` and topic like "agents" or "tools"

### 2. OpenRouter Documentation  
- **When to use**: LLM API issues, model selection, pricing questions
- **Access**: Use Context7 MCP server with library ID `/context7/openrouter_ai` (best coverage with 268 code snippets) or `/llmstxt/openrouter_ai-docs-llms-full.txt` (comprehensive with 550 code snippets)
- **Example**: `mcp_context7_get-library-docs` with `context7CompatibleLibraryID="/context7/openrouter_ai"` and topic like "api" or "models"

### 3. Logfire Logs
- **When to use**: Runtime debugging, performance analysis, error investigation
- **Primary tool**: `mcp_logfire_arbitrary_query`
- **Schema**: Use `mcp_logfire_get_logfire_records_schema` for query structure

### 4. Repository Documentation
- **`README.md`**: High-level system overview
- **Agent creation guide**: `mcp_oneshot_how_to_create_agents`
- **Available tools**: `mcp_oneshot_list_tools`

## Safe Contribution Guidelines

### Creating New Agents
1. **Check existing tools**: Call `mcp_oneshot_list_agents` to avoid duplication
2. **Use the guide**: Call `mcp_oneshot_how_to_create_agents` first
3. **Follow the pattern**: Examine existing agents in `/agents/`
4. **Test incrementally**: Create agent → test basic functionality → add tools → test again

### Creating New Tools
1. **Check existing tools**: Call `mcp_oneshot_list_tools` to avoid duplication
2. **Follow the pattern**: Examine existing tools in `/tools/`
3. **Start simple**: Basic functionality first, then add complexity
4. **Test isolation**: Test tool independently before integrating with agents

### Modifying Core Application (`/app`)
**ONLY modify core application code if**:
- You've confirmed the issue is in the core logic (not config/environment)
- You've tested the fix in isolation
- You understand the full impact of the change
- You've verified the fix with Logfire logs

**Never modify** without first:
1. Reading the current implementation thoroughly
2. Understanding why the current code exists
3. Confirming your change doesn't break existing functionality

## Troubleshooting Workflow

```
User reports issue
       ↓
Check Logfire logs for errors
       ↓
Verify environment/config
       ↓
Test components in isolation
       ↓
Identify root cause
       ↓
Apply minimal fix
       ↓
Verify fix with Logfire
       ↓
Document solution for user
```

## Emergency Recovery

If you accidentally break the core application:

1. **Stop immediately** - Don't make more changes
2. **Check git status** - See what files were modified
3. **Revert changes**: `git checkout -- app/` (if safe to do so)
4. **Test basic functionality**: `./agent web_agent "test"`
5. **Check Logfire** for any remaining issues

## Success Metrics

A successful intervention should result in:
- ✅ User's original issue resolved
- ✅ System remains stable and functional
- ✅ No new errors in Logfire logs
- ✅ User can continue their work confidently
- ✅ Clear explanation of what was fixed and why

## Key Takeaways

1. **Investigate first, code later** - Use diagnostic tools before making changes
2. **Logfire is your friend** - It shows you exactly what's happening but there pbviously won't be logs if the oneshot system has never actually run.
3. **Most issues are environmental** - Check config, credentials, and setup first
4. **The core app is battle-tested** - It's probably not the problem
5. **Users are learning** - Provide clear explanations, not just fixes
6. **One shot means getting it right** - Take time to understand before acting

Remember: The goal is to help users succeed with the oneshot system, not to demonstrate coding prowess. Sometimes the best solution is the simplest one. 