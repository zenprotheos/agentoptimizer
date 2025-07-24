# Agent Configuration Error Handling System

## Overview

The Oneshot agent system now includes comprehensive error handling for common agent configuration mistakes. This system provides specific, actionable error messages that help users (and orchestrating agents) quickly identify and fix configuration issues.

## Key Features

### 🎯 **Specific Error Classes**
- **YAMLFrontmatterError**: YAML syntax issues with line numbers
- **MissingRequiredFieldError**: Missing required fields with examples
- **InvalidModelError**: Invalid model names with suggestions
- **InvalidToolError**: Non-existent tools with fuzzy matching suggestions
- **InvalidMCPServerError**: Invalid MCP servers with suggestions
- **TemplateProcessingError**: Jinja2 template issues with context
- **InvalidFieldTypeError**: Wrong data types with examples
- **AgentFileFormatError**: File format issues with structure guide

### 🔍 **Smart Suggestions**
- **Fuzzy matching** for tool and MCP server name typos
- **Common corrections** for model names (e.g., "gpt-4" → "openai/gpt-4o")
- **Provider prefix detection** for model names
- **YAML syntax guidance** with specific line numbers
- **File structure examples** for malformed agents

### 📍 **Precise Error Context**
- **Line numbers** for YAML syntax errors
- **Field names** and expected types
- **File paths** and agent names in all errors
- **Available options** listed for invalid choices

## Error Types and Examples

### 1. YAML Frontmatter Errors

**Problem**: Invalid YAML syntax
```yaml
---
name: my_agent
description: "Missing closing quote
model: openai/gpt-4o-mini
---
```

**Error Message**:
```
Agent 'my_agent': YAML syntax error: found unexpected end of stream
  Problem line 3: model: openai/gpt-4o-mini

Suggestions:
  • Check that YAML frontmatter is enclosed in '---' lines
  • Ensure proper YAML indentation (use spaces, not tabs)
  • Validate YAML syntax using an online YAML validator
  • Check for missing colons after field names
  • Ensure list items start with '- ' (dash followed by space)
```

### 2. Missing Required Fields

**Problem**: Missing required fields
```yaml
---
name: my_agent
# missing description and model
tools:
  - web_search
---
```

**Error Message**:
```
Agent 'my_agent': Missing required field 'description' in YAML frontmatter

Suggestions:
  • Add 'description' field to your agent's YAML frontmatter
  • Provide a clear description of what your agent does
  • Example: description: "Searches the web and reads web pages"
```

### 3. Invalid Model Names

**Problem**: Common model name mistakes
```yaml
---
name: my_agent
description: "Test agent"
model: gpt-4  # missing provider prefix
---
```

**Error Message**:
```
Agent 'my_agent': Invalid model name 'gpt-4' missing provider prefix

Suggestions:
  • Did you mean 'openai/gpt-4o'?
  • OpenAI models need 'openai/' prefix. Try 'openai/gpt-4'
  • Check OpenRouter.ai for available models
  • Common models: openai/gpt-4o-mini, openai/gpt-4o, anthropic/claude-3-sonnet
  • Ensure model name includes provider prefix (e.g., 'openai/', 'anthropic/')
```

### 4. Invalid Tool Names

**Problem**: Typos in tool names
```yaml
---
name: my_agent
description: "Test agent"
model: openai/gpt-4o-mini
tools:
  - web_search  # correct
  - web_serch   # typo
---
```

**Error Message**:
```
Agent 'my_agent': Tool 'web_serch' not found

Suggestions:
  • Did you mean: web_search?
  • Check that 'web_serch.py' exists in the tools directory
  • Ensure tool name matches the filename exactly (case-sensitive)
  • Verify the tool file has proper structure with TOOL_METADATA and main function
  • Available tools: file_creator, web_search, youtube_highlighter
```

### 5. Wrong Field Types

**Problem**: Incorrect data types
```yaml
---
name: my_agent
description: "Test agent"
model: openai/gpt-4o-mini
tools: web_search  # should be a list
temperature: "hot"  # should be a number
---
```

**Error Message**:
```
Agent 'my_agent': Field 'tools' must be list, got str: web_search

Suggestions:
  • The 'tools' field must be a list
  • Example: tools:
    - web_search
    - file_creator
  • If you have only one tool, still use list format: tools:
    - tool_name
```

### 6. File Format Issues

**Problem**: Missing frontmatter delimiters
```
# My Agent

This agent has no frontmatter.
```

**Error Message**:
```
Agent 'my_agent': Agent file must start with YAML frontmatter delimiter '---'

Suggestions:
  • Agent files must follow this format:
  • ---
  • name: agent_name
  • description: "Agent description"
  • model: "openai/gpt-4o-mini"
  • tools:
  •   - tool1
  •   - tool2
  • ---
  • 
  • # Agent system prompt content here...
```

## Integration Points

### 1. Agent Runner (`app/agent_runner.py`)
- **Enhanced `_parse_agent_config()`**: Uses comprehensive validation before processing
- **Structured error responses**: Returns error type and context for MCP server
- **Model validation**: Catches OpenRouter API errors with helpful messages

### 2. Template Processor (`app/agent_template_processor.py`)
- **Enhanced YAML parsing**: Better error messages with line numbers
- **Template validation**: Pre-validates include files before rendering
- **Jinja2 error handling**: Converts template errors to user-friendly messages

### 3. MCP Server (`oneshot_mcp.py`)
- **Formatted error responses**: Converts technical errors to markdown with suggestions
- **Error categorization**: Different formatting for configuration vs execution errors
- **Troubleshooting guides**: Built-in help for common issues

### 4. Validation System (`app/agent_validation.py`)
- **AgentConfigValidator**: Central validation logic with comprehensive checks
- **Template include validation**: Ensures all referenced files exist
- **Fuzzy matching**: Suggests corrections for typos in tool/MCP server names

## Usage Examples

### For Orchestrating Agents

When an agent configuration fails, the error response includes:

```json
{
  "output": "",
  "success": false,
  "error": "Agent Configuration Error: [detailed message with suggestions]",
  "error_type": "configuration",
  "agent_file": "agents/my_agent.md"
}
```

The orchestrating agent can:
1. **Parse the error type** to understand the category of issue
2. **Extract suggestions** from the formatted error message  
3. **Identify the specific file** that needs fixing
4. **Provide targeted help** to the user based on the error type

### For Direct Users

Error messages are formatted as markdown with:
- ❌ **Clear problem identification**
- 💡 **Actionable suggestions**
- 📝 **Examples of correct syntax**
- 📋 **Lists of available options**

## Error Prevention

The system also includes:

### 1. **Proactive Validation**
- Validates configuration before attempting to run agents
- Checks tool and MCP server existence during startup
- Validates numeric parameter ranges

### 2. **Warning System**
- Non-fatal warnings for uncommon but valid configurations
- Tool loading warnings that don't prevent agent execution
- MCP server connection warnings

### 3. **Graceful Degradation**
- Agents can run with partial tool sets if some tools fail to load
- Missing MCP servers are warned about but don't prevent execution
- Template rendering continues with available context

## Best Practices

### For Agent Creators
1. **Use the validator**: Run `AgentConfigValidator.validate_complete_config()` on new agents
2. **Check error messages**: Read the full error message including suggestions
3. **Validate incrementally**: Fix one error at a time and re-test
4. **Use common patterns**: Follow the examples in error messages

### For Orchestrating Agents
1. **Parse error types**: Use the `error_type` field to categorize issues
2. **Extract suggestions**: Parse the formatted error message for actionable items
3. **Provide context**: Include the agent filename in user communications
4. **Retry after fixes**: Re-attempt agent creation after addressing issues

## Testing the System

### Comprehensive System Test

A complete test suite is available to validate the entire agent system:

```bash
python3 test_system.py
```

This test suite validates:
- ✅ **Valid agent configuration** - Tests that the test_agent works correctly
- ✅ **Tool functionality** - Verifies that tools can be called successfully
- ✅ **File processing** - Tests file content injection via --files parameter
- ✅ **Template includes** - Validates that snippet includes work correctly
- ✅ **Error handling** - Tests that configuration errors are caught and reported properly
- ✅ **MCP server integration** - Basic validation of MCP server functionality

### Test Components

The test system includes:

#### 1. **Test Agent** (`agents/test_agent.md`)
A comprehensive test agent that:
- Uses proper YAML frontmatter configuration
- Includes the test_tool in its tools list
- Demonstrates template includes with test_snippet.md
- Supports file processing via template system

#### 2. **Test Tool** (`tools/test_tool.py`)
A simple tool that:
- Returns test messages to verify tool calling works
- Has proper TOOL_METADATA structure
- Can be called with optional parameters

#### 3. **Test Snippet** (`snippets/test_snippet.md`)
A template snippet that:
- Tests that template includes work correctly
- Provides content for the test agent
- Validates snippets directory configuration

#### 4. **Test File** (`test_data/sample_file.txt`)
A sample file that:
- Tests file content injection functionality
- Validates the --files parameter works correctly
- Provides content for file processing tests

### Manual Testing

You can also test individual components manually:

```bash
# Test basic agent functionality
./oneshot test_agent "Hello, please test your functionality"

# Test tool calling
./oneshot test_agent "Please call your test_tool to verify it works"

# Test file processing
./oneshot test_agent "I've provided you with a test file. Please confirm you can see its content." --files test_data/sample_file.txt

# Test error handling (create a broken agent first)
./oneshot broken_agent "This should fail with helpful error messages"
```

### After Making Changes

**Always run the test suite after making changes to:**
- Agent configuration parsing (`app/agent_runner.py`, `app/agent_template_processor.py`)
- Error handling system (`app/agent_errors.py`, `app/agent_validation.py`)
- Tool loading mechanisms (`app/tool_services.py`)
- MCP server integration (`oneshot_mcp.py`, `app/mcp_modules/`)
- Template processing (`app/agent_template_processor.py`)

### Test Results Interpretation

- ✅ **PASS**: Component is working correctly
- ⚠️ **WARNING**: Component is working but may need attention
- ❌ **FAIL**: Component has issues that need to be fixed

The test suite is designed to be comprehensive but not overly strict - some warnings are acceptable if the functionality is working correctly.

## Future Enhancements

Potential improvements to the error handling system:

1. **Model availability checking**: Real-time validation against OpenRouter API
2. **Tool dependency analysis**: Check if tools have required dependencies
3. **Configuration templates**: Suggest complete configurations for common use cases
4. **Interactive fixing**: Guided prompts to fix configuration issues
5. **Batch validation**: Validate multiple agents at once with summary reports
6. **Enhanced test coverage**: More comprehensive test scenarios and edge cases 