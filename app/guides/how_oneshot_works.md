---
name: "How Oneshot Works"
purpose: "Comprehensive technical overview of the Oneshot system architecture for AI coding agents that are responsible for maintenance, extension, and troubleshooting"
---

# How the Oneshot System Works: A Technical Guide for AI Coding Agents

This document provides a holistic technical overview of the Oneshot system architecture, intended for an AI coding agent that is responsible for its maintenance, extension, and troubleshooting. For detailed information about the core agent execution engine, refer to `how_agent_runner_works.md`.

## System Philosophy

Oneshot is designed as a **specialist agent orchestration framework** that enables the creation and execution of purpose-built AI agents. The core philosophy centers on:

1. **Pydantic AI Foundation**: The system is fundamentally a sophisticated wrapper around the Pydantic AI library, which handles LLM interactions, tool orchestration, and message management.

2. **Agent Specialization**: Rather than one general-purpose agent, the system enables creating many specialized agents, each optimized for specific tasks with their own tools, prompts, and configurations.

3. **Modular Architecture**: Clean separation of concerns across configuration, tool management, execution, and persistence layers.

4. **Conversation Continuity**: Stateless LLM interactions are made stateful through persistent run management.

## System Architecture Overview

```mermaid
graph TB
    subgraph "Entry Points"
        CLI[CLI Interface<br/>app/oneshot bash script]
        MCP[MCP Server<br/>app/oneshot_mcp.py]
    end
    
    subgraph "Core Engine"
        AR[Agent Runner System<br/>4 modules]
        TS[Tool System<br/>/tools directory]
        TSV[Tool Services<br/>app/tool_services.py]
        RP[Run Persistence<br/>/runs directory]
        TP[Template Processor<br/>Jinja2 engine]
    end
    
    subgraph "External Services"
        OR[OpenRouter<br/>LLM API Gateway]
        LF[Logfire<br/>Observability]
        MCPS[MCP Servers<br/>External Tools]
    end
    
    subgraph "Data Storage"
        AD[Agent Definitions<br/>/agents directory]
        CF[Configuration<br/>config.yaml]
        MC[MCP Config<br/>.cursor/mcp.json]
        AF[Artifacts<br/>/artifacts directory]
    end
    
    CLI --> AR
    MCP --> AR
    AR --> TS
    TS --> TSV
    AR --> RP
    AR --> TP
    AR --> OR
    AR --> LF
    AR --> MCPS
    AR --> AD
    AR --> CF
    AR --> MC
    TSV --> AF
    TSV --> RP
    
    style AR fill:#e1f5fe
    style TSV fill:#c8e6c9
    style CLI fill:#f3e5f5
    style MCP fill:#f3e5f5
    style OR fill:#fff3e0
    style LF fill:#fff3e0
    style MCPS fill:#fff3e0
```

## Core Components

### 1. Agent Definitions (`/agents` directory)
- **Format**: Markdown files with YAML frontmatter
- **Purpose**: Define agent behavior, model parameters, available tools, and system prompts
- **Template System**: Jinja2 templating for dynamic content injection
- **Configuration Hierarchy**: Agent-specific settings override global defaults

### 2. Agent Runner System (`app/agent_runner.py` + 3 modules)
The heart of the system, responsible for agent execution. This is implemented as a modular system with four components:

- **`agent_runner.py`**: Main orchestrator and public API
- **`agent_config.py`**: Configuration parsing and validation
- **`agent_tools.py`**: Tool and MCP server management  
- **`agent_executor.py`**: Core execution engine with multimodal support

**📖 For detailed technical information about the agent runner system, see `how_agent_runner_works.md`.**

### 3. Tool System (`/tools` directory)
- **Dynamic Loading**: Tools are automatically discovered and loaded from Python files
- **Metadata-Driven**: Each tool defines `TOOL_METADATA` for discovery
- **Pydantic AI Integration**: Tools are bound to agents as callable functions
- **Error Handling**: Graceful degradation when tools are unavailable
- **Tool Services Integration**: Tools leverage the centralized `tool_services.py` module

### 4. Tool Services System (`app/tool_services.py`)
A critical infrastructure component that eliminates boilerplate code in tools:

- **LLM Integration**: Pre-configured Pydantic AI clients with automatic retry logic
- **File Operations**: Smart file handling with run-aware organization and metadata
- **API Integration**: HTTP requests with automatic authentication
- **Template Engine**: Jinja2 templating with built-in variables
- **Context Management**: Automatic run ID tracking for artifact organization

**Key Features of Tool Services:**
```python
# Single import provides everything
from app.tool_services import *

# Available functions:
- llm()              # Basic LLM calls
- llm_json()         # JSON-returning LLM calls
- llm_structured()   # Pydantic model validation
- chain_prompts()    # Multi-step conversations
- save()             # Smart file saving with metadata
- save_json()        # JSON with metadata wrapper
- read()             # File reading
- api()              # HTTP requests with auth
- template()         # Jinja2 templating
```

**📖 For complete documentation, see "How to Use Tool Services" and "How to Create Tools" guides.**

### 5. Run Persistence (`app/run_persistence.py`)
- **Conversation Continuity**: Maintains stateful conversations across stateless LLM calls
- **Storage**: JSON-based storage in `/runs/{run_id}/` directories
- **Message History**: Complete Pydantic AI message chains for context preservation
- **Metadata Tracking**: Usage statistics, timestamps, and execution details
- **Artifact Correlation**: Links with `/artifacts/{run_id}/` for generated files

### 6. Template Processing (`app/agent_template_processor.py`)
- **Dynamic Content**: Jinja2 templating for agent prompts
- **File Injection**: `--files` content is injected into agent context
- **Snippet System**: Reusable template components in `/snippets`
- **Context Variables**: Rich template context for dynamic prompt generation
- **Tool Services Integration**: Built-in variables available in all LLM calls

## Entry Points and Interfaces

```mermaid
graph LR
    subgraph "User Interactions"
        U1[Terminal User]
        U2[Cursor IDE]
        U3[Other AI Systems]
    end
    
    subgraph "Entry Points"
        CLI[CLI Interface<br/>./oneshot script in app dir]
        MCP[MCP Server<br/>app/oneshot_mcp.py]
    end
    
    subgraph "Interface Features"
        F1[File Context<br/>--files parameter]
        F2[Conversation Continuity<br/>--run-id parameter]
        F3[Output Formats<br/>--json flag]
        F4[Debug Mode<br/>--debug flag]
    end
    
    U1 --> CLI
    U2 --> MCP
    U3 --> MCP
    
    CLI --> F1
    CLI --> F2
    CLI --> F3
    CLI --> F4
    
    MCP --> F1
    MCP --> F2
    
    style CLI fill:#e8f5e8
    style MCP fill:#e8f5e8
```

### Command Line Interface
```bash
./oneshot <agent_name> "<message>" [--files file1|file2] [--run-id <id>] [--json] [--debug]
```
- **Primary Interface**: Direct agent execution from terminal
- **File Context**: Pass files as context via `--files` parameter
- **Conversation Continuity**: Use `--run-id` to continue existing conversations
- **Output Formats**: Human-readable or JSON for programmatic use

### MCP Server (`oneshot_mcp.py`)
- **Protocol**: Model Context Protocol for AI agent integration
- **Endpoints**: `call_agent`, `list_agents`, `list_tools`, etc.
- **Integration**: Allows other AI systems to use Oneshot agents
- **Cursor/CLI Integration**: Exposed as MCP server for Cursor IDE, or Claude Code CLI integration

## Configuration System

### Global Configuration (`config.yaml`)
- **Model Defaults**: Default LLM parameters for all agents
- **Usage Limits**: Request and token limits for cost control
- **Logfire Settings**: Observability and instrumentation configuration
- **Template Engine**: Jinja2 template processing settings

### Agent Configuration (YAML Frontmatter)
- **Model Override**: Agent-specific model and parameters
- **Tool Assignment**: Which tools the agent can access
- **MCP Servers**: External service integrations
- **Behavioral Settings**: Temperature, token limits, timeouts

### MCP Configuration (`.cursor/mcp.json`)
- **Server Definitions**: External MCP server configurations
- **Authentication**: API keys and connection settings
- **Tool Prefixes**: Namespace management for external tools

## Data Flow Architecture

### 1. Request Processing Flow
```mermaid
flowchart LR
    UI[User Input] --> EP[Entry Point]
    EP --> AR[Agent Runner]
    AR --> CL[Configuration Loading]
    CL --> TP[Template Processing]
    TP --> TL[Tool Loading]
    TL --> AE[Agent Execution]
    AE --> RF[Response Formatting]
    
    style UI fill:#f9f9f9
    style EP fill:#e8f5e8
    style AR fill:#e1f5fe
    style RF fill:#f3e5f5
```

### 2. File Context Flow
```mermaid
flowchart LR
    FP[--files parameter] --> FR[File Reading]
    FR --> TI[Template Injection]
    TI --> SPR[System Prompt Rendering]
    SPR --> AC[Agent Context]
    AC --> LP[LLM Processing]
    
    style FP fill:#fff3e0
    style LP fill:#e8f5e8
```

### 3. Conversation Flow
```mermaid
flowchart LR
    RID[Run ID] --> HL[History Loading]
    HL --> MC[Message Context]
    MC --> AE[Agent Execution]
    AE --> RG[Response Generation]
    RG --> HU[History Update]
    HU --> P[Persistence]
    
    style RID fill:#f3e5f5
    style P fill:#e8f5e8
```

### 4. Tool Services Flow
```mermaid
flowchart LR
    T[Tool Function] --> TS[Tool Services]
    TS --> LLM[LLM Operations]
    TS --> FO[File Operations]
    TS --> API[API Calls]
    FO --> AF[/artifacts/{run_id}/]
    LLM --> OR[OpenRouter]
    API --> ES[External Services]
    
    style T fill:#f3e5f5
    style TS fill:#c8e6c9
    style AF fill:#e8f5e8
```

## External Service Integration

```mermaid
graph TB
    subgraph "Oneshot Core"
        AR[Agent Runner]
        TS[Tool Services]
    end
    
    subgraph "LLM Services"
        OR[OpenRouter<br/>LLM Gateway]
        subgraph "LLM Providers"
            OAI[OpenAI<br/>GPT Models]
            ANT[Anthropic<br/>Claude Models]
            OTH[Other Providers]
        end
    end
    
    subgraph "Observability"
        LF[Logfire<br/>Tracing & Metrics]
        subgraph "Monitoring Data"
            TR[Execution Traces]
            MT[Performance Metrics]
            ER[Error Tracking]
        end
    end
    
    subgraph "External Tools"
        MCP1[Zapier Email<br/>MCP Server]
        MCP2[Notion<br/>MCP Server]
        MCP3[Context7<br/>Documentation]
        MCPN[Other MCP<br/>Servers]
    end
    
    AR --> OR
    TS --> OR
    OR --> OAI
    OR --> ANT
    OR --> OTH
    
    AR --> LF
    TS --> LF
    LF --> TR
    LF --> MT
    LF --> ER
    
    AR --> MCP1
    AR --> MCP2
    AR --> MCP3
    AR --> MCPN
    
    style AR fill:#e1f5fe
    style TS fill:#c8e6c9
    style OR fill:#fff3e0
    style LF fill:#e8f5e8
    style MCP1 fill:#f3e5f5
    style MCP2 fill:#f3e5f5
    style MCP3 fill:#f3e5f5
    style MCPN fill:#f3e5f5
```

### OpenRouter (LLM Gateway)
- **Purpose**: Unified API for multiple LLM providers
- **Authentication**: `OPENROUTER_API_KEY` environment variable
- **Model Selection**: Agent-specific model configuration
- **Error Handling**: Comprehensive API error management
- **Tool Services Integration**: Automatic retry logic and error handling

### Logfire (Observability)
- **Instrumentation**: Automatic Pydantic AI call tracing
- **Metrics**: Performance, usage, and error tracking
- **Debugging**: Detailed execution traces for troubleshooting
- **Configuration**: Optional service with graceful degradation
- **Tool Services Integration**: All tool operations are automatically instrumented

### MCP Servers (External Tools)
- **Integration**: External service access via Model Context Protocol
- **Examples**: Email (Zapier), Notion, Context7 documentation
- **Management**: Dynamic loading and error handling
- **Authentication**: Per-server credential management

## Artifact Organization

The system maintains a clear separation between conversation history and generated artifacts:

### Directory Structure
```
/runs/{run_id}/              # Conversation history
├── run.json                 # Complete conversation data
├── messages.json            # Message history
└── metadata.json            # Run summary

/artifacts/{run_id}/         # Files generated during conversation
├── analysis_report.md       # Tool-generated content
├── summary.txt              # With YAML frontmatter
└── data_results.json        # With metadata wrapper
```

### Artifact Features
- **Run-Aware Organization**: Files automatically organized by conversation
- **Metadata Rich**: All files include creation time, tokens, description
- **Frontmatter System**: YAML metadata for markdown/text files
- **JSON Wrapper**: Metadata structure for JSON files
- **Educational Value**: Clear correlation between conversations and outputs

## Multimodal Capabilities

The system supports comprehensive multimodal input processing:

### Supported Media Types
- **Images**: JPG, PNG, GIF, WebP
- **Documents**: PDF
- **Audio**: MP3, WAV, M4A
- **Video**: MP4, MOV, AVI
- **URLs**: Any supported format via HTTP/HTTPS

### Processing Pipeline
- **Detection**: Automatic media type identification
- **Validation**: File size and format verification
- **Integration**: Seamless combination with text context
- **Error Handling**: Graceful fallback to text processing

## Error Handling Philosophy

### Layered Error Management
- **Configuration Errors**: YAML, model, and tool validation with suggestions
- **Execution Errors**: Runtime failures with context-specific guidance
- **External Service Errors**: API and network issues with troubleshooting steps
- **Multimodal Errors**: File and URL processing with actionable feedback
- **Tool Services Errors**: Comprehensive error handling in all helper functions

### User Experience Focus
- **Specific Messages**: Clear identification of the problem
- **Actionable Suggestions**: Concrete steps to resolve issues
- **Graceful Degradation**: Continue operation when possible
- **Debug Support**: Comprehensive logging in debug mode

## Development and Extension

### Adding New Agents
1. Create `.md` file in `/agents` with YAML frontmatter
2. Define system prompt using Jinja2 templating
3. Specify required tools and model parameters
4. Test with various input scenarios

### Creating New Tools
1. Create Python file in `/tools` directory
2. Define `TOOL_METADATA` dictionary
3. Implement main function matching filename
4. **Use `tool_services.py` functions** instead of implementing from scratch
5. Handle errors gracefully with helpful messages

**Tool Creation Best Practice:**
```python
from app.tool_services import *
import json

def my_tool(param: str) -> str:
    # Use tool_services functions
    result = llm(f"Process: {param}")
    saved = save(result, "Processing results")
    return json.dumps({"filepath": saved["filepath"]})
```

### Extending Error Handling
- Add new error classes to `app/agent_errors.py`
- Update component error handling to use specific classes
- Provide helpful suggestions and troubleshooting steps
- Tool services provides automatic error handling for common operations

## Troubleshooting Guide

### Common Issues and Solutions

**Agent Not Found**: Check agent file exists in `/agents/{name}.md` with correct YAML frontmatter

**Tool Loading Failures**: Verify `TOOL_METADATA` exists and tool function is properly defined

**Conversation History Issues**: Check `/runs/{run_id}/run.json` exists and is valid JSON

**MCP Server Problems**: Verify `.cursor/mcp.json` configuration and server availability

**Model API Errors**: Validate `OPENROUTER_API_KEY` and model name against OpenRouter catalog

**File Context Not Working**: Ensure agent template includes `{% include "provided_content.md" %}`

**Tool Services Issues**: Check that tools use `from app.tool_services import *` and follow patterns

**Artifact Organization**: Verify run ID is set correctly for proper file organization

### Debug Mode
Enable comprehensive debugging with `--debug` flag for detailed execution traces, configuration loading, and error context.

### Logfire Integration
Use Logfire traces for deep debugging of agent execution, tool calls, and LLM interactions when `LOGFIRE_WRITE_TOKEN` is configured. Tool services operations are automatically instrumented.

## System Maintenance

### Regular Tasks
- Monitor `/runs` directory size and clean old conversations
- Monitor `/artifacts` directory and archive old generated files
- Update model configurations as new models become available
- Review Logfire traces for performance optimization opportunities
- Test agent configurations after system updates
- Verify tool services functions are used consistently across tools

### Performance Considerations
- **Token Usage**: Monitor and optimize prompt lengths
- **Tool Selection**: Minimize unnecessary tool loading
- **Conversation Length**: Implement conversation pruning for long runs
- **File Processing**: Optimize multimodal content handling
- **Tool Services**: Leverage caching and efficient file operations

### Tool Services Benefits
- **Reduced Boilerplate**: 80% less code in typical tools
- **Consistent Error Handling**: Automatic retry logic and graceful failures
- **Performance Optimization**: Built-in caching and efficient operations
- **Automatic Instrumentation**: All operations logged to Logfire
- **Run-Aware Organization**: Files automatically organized by conversation

This architecture provides a robust foundation for specialized AI agent orchestration while maintaining flexibility for extension and customization. The tool services system ensures consistent, efficient tool implementation across the entire framework.