## URGENT & IMPORTANT SET UP

Before you can do anything useful with this repo, you need to set it up. You will know it is set up if you see the oneshot mcp server with its `call_agent` tool (mcp_oneshot_call_agent), in your tools, and the logfire mcp server with its `arbitrary_query` tool (mcp_logfire_arbitrary_query) in your tools.

If you do not see those things then the repo is not properly set up. You MUST read app/docs/how_to_setup.md and guide the user through setup, doing the tasks you can and helping the user through the manual steps. Once successfully setup, come back and remove this URGENT & IMPORTANT SETUP section of this onboarding document. That will ensure that you don't unnecessarily repeat the setup steps in future.

CRITICAL: Ask yourself, is the oneshot system setup based on the guide above? If yes, delete this section and then continue with your task.



# Oneshot Agent System - Coding Agent Onboarding Guide

IMPORTANT: You first read this document to get onboarded, to learn how to work with this repo. Then you read app/docs/how_oneshot_works.md to learn how the code actually works. Do not attempt changes before you have read both.

## Philosophy: Primum Non Nocere (First, Do No Harm)

**CRITICAL PRINCIPLE**: Before making ANY changes to the core application code in `/app`, you MUST diagnose the root cause of issues using the diagnostic tools and resources outlined in this document. Most problems are configuration, environment, or usage issues - NOT core application bugs.

### Common Failure Pattern to AVOID
❌ User reports issue → Agent immediately modifies `/app` code → Core system breaks → User loses confidence

✅ **Correct Approach**: User reports issue → Agent investigates using diagnostics → Identifies root cause → Makes minimal, targeted fix

## System Overview

The Oneshot system is a Pydantic AI-based agent runner. It is designed to be robust and observable. For a detailed technical breakdown of the architecture, including how the agent runner, run persistence, and context processing works, refer to the **`how_oneshot_works.md`** document.

Your primary goal is to interact with and troubleshoot this system on behalf of a user, using the provided diagnostic tools.

## Diagnostic Methodology

### Step 1: Check System Health
Before investigating specific issues, verify basic system health:

```bash
# Test the agent CLI directly
./oneshot web_agent "hello"

# Test MCP server functionality
python3 -c "from app.mcp_modules.agents import list_agents; print(list_agents('.'))"

# Test run persistence
python3 -c "from app.run_persistence import RunPersistence; rp = RunPersistence(); print('Run persistence OK')"
```

### Step 2: Use Logfire for Investigation
Logfire is your primary diagnostic tool. It provides detailed traces of every agent run.

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
```

### Step 3: Verify Environment Configuration
Check for missing credentials or configuration:

```python
import os
print("OpenRouter API Key:", "✓" if os.getenv("OPENROUTER_API_KEY") else "✗ MISSING")
print("Logfire Token:", "✓" if os.getenv("LOGFIRE_TOKEN") else "✗ MISSING")
```

### Step 4: Access Documentation When Needed
For deeper understanding of Pydantic AI or other libraries, use the Context7 MCP server. To understand the Oneshot system's internal workings, read `how_oneshot_works.md`.

```python
# Get Pydantic AI documentation
mcp_context7_get-library-docs(
    context7CompatibleLibraryID="/context7/ai_pydantic_dev",
    topic="agents"
)
```

## Common Issues and Diagnostic Patterns

### Issue: "Agent not responding" or "MCP server not working"
**Before touching code**, check:
1. Is the `agent` script executable?
2. Are environment variables set?
3. Check Logfire for subprocess errors.

### Issue: "Tool not found" or "Tool execution failed"
**Root causes**:
1. Tool not defined in `config.yaml` for the agent.
2. Tool file has syntax errors.
3. Tool dependencies are not installed.

### Issue: "LLM API errors" (e.g., 401, 403)
**Root causes**:
1. Invalid `OPENROUTER_API_KEY`.
2. Insufficient credits on OpenRouter.
3. Invalid model name in the agent's `.md` file.

### Issue: "Run continuation not working"
**Root causes**:
1. Run ID is incorrect.
2. The `/runs` directory is not writable.
3. The `run.json` file for the run is corrupted.

## Safe Contribution Guidelines

### Creating New Agents and Tools
1.  **Avoid Duplication**: Check for existing agents and tools first.
2.  **Follow Patterns**: Examine existing files in `/agents` and `/tools`.
3.  **Test Incrementally**: Test your changes in small, verifiable steps.

### Modifying Core Application (`/app`)
**DO NOT** modify the core application code unless you have:
1.  Confirmed the issue is in the core logic by using the diagnostic tools.
2.  Read and understood the relevant sections of `how_oneshot_works.md`.
3.  A clear plan to fix the issue with minimal changes.

## Emergency Recovery

If you break the application:
1.  **Stop.** Do not make more changes.
2.  **Check `git status`** to see what you modified.
3.  **Revert your changes**: `git checkout -- app/`
4.  **Verify** that the system is working again.

## Key Takeaways

1.  **Investigate first, code later**.
2.  **Logfire is your primary tool**.
3.  **Most issues are environmental or configuration-related**.
4.  **The core app is stable**. Assume it works correctly until you can prove otherwise.
5.  **Consult `how_oneshot_works.md`** for technical details.