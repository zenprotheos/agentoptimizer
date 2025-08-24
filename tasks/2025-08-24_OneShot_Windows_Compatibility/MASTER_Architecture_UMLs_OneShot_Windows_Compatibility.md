---
title: "OneShot MCP Architecture - Windows Compatibility Analysis"
date: "2025-08-24"
task: "OneShot Windows Compatibility"
status: "In Progress"
priority: "High"
tags: ["architecture", "mcp", "windows", "compatibility", "uml"]
---

# OneShot MCP Architecture - Windows Compatibility Analysis

## Overview

This document provides comprehensive UML documentation and architectural analysis of the OneShot MCP system, with specific focus on Windows compatibility issues and required modifications.

## System Architecture Overview

```mermaid
graph LR
    subgraph "Cursor IDE Environment"
        CUR["Cursor Agent"]
        MCP_CLIENT["MCP Client"]
    end
    
    subgraph "OneShot System"
        MCP_SERVER["OneShot MCP Server|oneshot_mcp.py"]
        AGENT_RUNNER["Agent Runner|agent_runner.py"]
        AGENT_EXECUTOR["Agent Executor|agent_executor.py"]
        TOOL_SERVICES["Tool Services|tool_services.py"]
        
        subgraph "Agent Management"
            AGENT_CONFIG["Agent Config|agent_config.py"]
            AGENT_VALIDATION["Agent Validation|agent_validation.py"]
            TEMPLATE_PROC["Template Processor|agent_template_processor.py"]
        end
        
        subgraph "Agents Directory"
            RESEARCH_AGENT["research_agent.md"]
            VISION_AGENT["vision_agent.md"]
            WEB_AGENT["web_agent.md"]
            NRL_AGENT["nrl_agent.md"]
            NEWS_AGENT["news_search_agent.md"]
        end
        
        subgraph "Tools Directory"
            WEB_SEARCH["web_search.py"]
            FILE_CREATOR["file_creator.py"]
            PDF_EXPORT["export_as_pdf.py"]
            TODO_TOOLS["todo_read.py|todo_write.py"]
            MCP_SERVERS["local_mcp_servers/"]
        end
        
        subgraph "Runtime Environment"
            PERSISTENCE["Run Persistence|run_persistence.py"]
            MULTIMODAL["Multimodal Processor|multimodal_processor.py"]
            CONFIG["config.yaml"]
        end
    end
    
    subgraph "External Dependencies"
        OPENROUTER["OpenRouter API"]
        LOGFIRE["Logfire Logging"]
        BRAVE_SEARCH["Brave Search API"]
        EXTERNAL_MCPS["External MCP Servers"]
    end
    
    CUR --> MCP_CLIENT
    MCP_CLIENT <--> MCP_SERVER
    MCP_SERVER --> AGENT_RUNNER
    AGENT_RUNNER --> AGENT_EXECUTOR
    AGENT_EXECUTOR --> TOOL_SERVICES
    TOOL_SERVICES --> WEB_SEARCH
    TOOL_SERVICES --> FILE_CREATOR
    TOOL_SERVICES --> PDF_EXPORT
    TOOL_SERVICES --> TODO_TOOLS
    
    AGENT_RUNNER --> AGENT_CONFIG
    AGENT_CONFIG --> RESEARCH_AGENT
    AGENT_CONFIG --> VISION_AGENT
    AGENT_CONFIG --> WEB_AGENT
    AGENT_CONFIG --> NRL_AGENT
    AGENT_CONFIG --> NEWS_AGENT
    
    AGENT_EXECUTOR --> PERSISTENCE
    AGENT_EXECUTOR --> MULTIMODAL
    
    TOOL_SERVICES --> OPENROUTER
    TOOL_SERVICES --> LOGFIRE
    TOOL_SERVICES --> BRAVE_SEARCH
    TOOL_SERVICES --> EXTERNAL_MCPS
```

## Windows Compatibility Issues Analysis

### 1. Path Handling Issues

```mermaid
graph TD
    subgraph "Current Mac-Centric Paths"
        MAC_PATHS[Unix-style paths<br/>/Users/user/...]
        FORWARD_SLASH[Forward slash separators]
        POSIX_PATHS[POSIX path conventions]
    end
    
    subgraph "Windows Requirements"
        WIN_PATHS[Windows-style paths<br/>C:\Users\user\...]
        BACKSLASH[Backslash separators]
        DRIVE_LETTERS[Drive letter conventions]
        UNC_PATHS[UNC path support]
    end
    
    subgraph "Problem Areas"
        FILE_OPS[File Operations]
        CONFIG_PATHS[Configuration Paths]
        TEMP_FILES[Temporary File Creation]
        EXECUTABLE_PATHS[Executable Discovery]
    end
    
    MAC_PATHS --> PROBLEM_1[Path resolution failures]
    FORWARD_SLASH --> PROBLEM_2[Separator conflicts]
    POSIX_PATHS --> PROBLEM_3[Platform incompatibility]
    
    PROBLEM_1 --> FILE_OPS
    PROBLEM_2 --> CONFIG_PATHS
    PROBLEM_3 --> TEMP_FILES
```

### 2. Process Execution Architecture

```mermaid
sequenceDiagram
    participant MCP as MCP Server
    participant AR as Agent Runner
    participant AE as Agent Executor
    participant TS as Tool Services
    participant OS as Operating System
    
    Note over MCP,OS: Current Mac-focused execution flow
    
    MCP->>AR: Execute agent request
    AR->>AE: Load agent configuration
    AE->>TS: Initialize tool services
    TS->>OS: Execute subprocess (Unix-style)
    
    Note over OS: Windows Issues:
    Note over OS: - Shell command differences
    Note over OS: - Environment variable handling
    Note over OS: - Process spawning mechanisms
    Note over OS: - Permission models
    
    OS-->>TS: Process results
    TS-->>AE: Tool execution results
    AE-->>AR: Agent execution results
    AR-->>MCP: Final response
```

### 3. Dependency Management Issues

```mermaid
graph LR
    subgraph "Python Environment"
        PYTHON_VER[Python Version Compatibility]
        VENV_HANDLING[Virtual Environment Handling]
        PKG_PATHS[Package Path Resolution]
    end
    
    subgraph "External Tools"
        NODE_DEPS[Node.js Dependencies]
        CHROME_PATH[Chrome/Chromium Paths]
        UV_TOOL[UV Tool Installation]
    end
    
    subgraph "Windows Challenges"
        STORE_ALIAS[Microsoft Store Python Alias]
        PATH_CONFLICTS[PATH Environment Conflicts]
        PERMISSION_ISSUES[Permission & Execution Policy]
        SHELL_DIFFERENCES[PowerShell vs Bash]
    end
    
    PYTHON_VER --> STORE_ALIAS
    VENV_HANDLING --> PATH_CONFLICTS
    PKG_PATHS --> PERMISSION_ISSUES
    NODE_DEPS --> SHELL_DIFFERENCES
    CHROME_PATH --> PATH_CONFLICTS
    UV_TOOL --> PERMISSION_ISSUES
```

## Data Flow Analysis

### 1. MCP Communication Flow

```mermaid
sequenceDiagram
    participant Cursor as Cursor IDE
    participant MCP_Client as MCP Client
    participant MCP_Server as OneShot MCP Server
    participant Agent_System as Agent System
    participant External as External APIs
    
    Cursor->>MCP_Client: User request
    MCP_Client->>MCP_Server: MCP protocol message
    
    Note over MCP_Server: Windows Issue: stdio vs SSE transport
    
    MCP_Server->>Agent_System: Parse and route request
    Agent_System->>Agent_System: Load agent configuration
    Agent_System->>External: Execute tools/API calls
    
    Note over External: Windows Issue: Process execution
    
    External-->>Agent_System: Results
    Agent_System-->>MCP_Server: Formatted response
    MCP_Server-->>MCP_Client: MCP protocol response
    MCP_Client-->>Cursor: Display results
```

### 2. File System Operations

```mermaid
flowchart TD
    START[File Operation Request] --> CHECK_PATH{Path Type?}
    
    CHECK_PATH -->|Absolute| ABS_PATH[Process Absolute Path]
    CHECK_PATH -->|Relative| REL_PATH[Process Relative Path]
    
    ABS_PATH --> WIN_CHECK{Windows Path?}
    WIN_CHECK -->|Yes| WIN_PROCESS[Windows Path Processing]
    WIN_CHECK -->|No| CONVERT[Convert to Windows Format]
    
    REL_PATH --> BASE_PATH[Determine Base Path]
    BASE_PATH --> COMBINE[Combine Paths]
    
    WIN_PROCESS --> VALIDATE[Validate Path Exists]
    CONVERT --> VALIDATE
    COMBINE --> VALIDATE
    
    VALIDATE -->|Valid| EXECUTE[Execute Operation]
    VALIDATE -->|Invalid| ERROR[Return Error]
    
    EXECUTE --> RESULT[Return Result]
    ERROR --> RESULT
    
    style WIN_PROCESS fill:#ffcccc
    style CONVERT fill:#ffcccc
    style ERROR fill:#ff6b6b
```

## Race Condition Mapping

### 1. Agent Execution Concurrency

```mermaid
sequenceDiagram
    participant MCP1 as MCP Request 1
    participant MCP2 as MCP Request 2
    participant Runner as Agent Runner
    participant Resources as Shared Resources
    
    Note over MCP1,Resources: Potential Race Conditions
    
    par
        MCP1->>Runner: Agent Request A
        and
        MCP2->>Runner: Agent Request B
    end
    
    par
        Runner->>Resources: Access config files
        and
        Runner->>Resources: Access temp directory
    end
    
    Note over Resources: Windows Issues:
    Note over Resources: - File locking differences
    Note over Resources: - Temp file conflicts
    Note over Resources: - Process isolation
    
    par
        Resources-->>Runner: Result A
        and
        Resources-->>Runner: Result B
    end
    
    par
        Runner-->>MCP1: Response A
        and
        Runner-->>MCP2: Response B
    end
```

### 2. File System Race Conditions

```mermaid
stateDiagram-v2
    [*] --> FileRequest
    FileRequest --> CheckExists
    CheckExists --> FileExists : File found
    CheckExists --> FileNotExists : File not found
    
    FileExists --> AttemptRead
    FileNotExists --> AttemptCreate
    
    AttemptRead --> ReadSuccess : Success
    AttemptRead --> ReadFail : Windows lock/permission
    
    AttemptCreate --> CreateSuccess : Success
    AttemptCreate --> CreateFail : Windows permission/path
    
    ReadSuccess --> [*]
    CreateSuccess --> [*]
    ReadFail --> RetryLogic
    CreateFail --> RetryLogic
    
    RetryLogic --> CheckExists : Retry
    RetryLogic --> [*] : Max retries
    
    note right of ReadFail
        Windows-specific issues:
        File locking
        Antivirus interference
        Permission models
    end note
    note right of CreateFail
        Windows-specific issues:
        Path length limits
        Reserved names
        Case sensitivity
    end note
```

## State Management Audit

### 1. Configuration State

```mermaid
classDiagram
    class ConfigurationManager {
        +config_path: str
        +loaded_config: dict
        +load_config()
        +save_config()
        +validate_paths()
    }
    
    class WindowsConfigManager {
        +normalize_windows_paths()
        +check_executable_paths()
        +handle_drive_letters()
        +validate_permissions()
    }
    
    class AgentConfig {
        +agent_definitions: dict
        +tool_mappings: dict
        +load_agents()
        +validate_agent_tools()
    }
    
    ConfigurationManager <|-- WindowsConfigManager : "extends"
    ConfigurationManager --> AgentConfig : "uses"
    
    note for WindowsConfigManager "Windows-specific|path handling needed"
```

### 2. Runtime State

```mermaid
stateDiagram-v2
    [*] --> SystemInit
    SystemInit --> LoadConfig
    LoadConfig --> ValidateEnvironment
    
    ValidateEnvironment --> EnvironmentValid : All checks pass
    ValidateEnvironment --> EnvironmentInvalid : Windows compatibility issues
    
    EnvironmentValid --> MCPServerStart
    EnvironmentInvalid --> ErrorHandling
    
    MCPServerStart --> ReadyState
    ErrorHandling --> [*]
    
    ReadyState --> ProcessingRequest : MCP request
    ProcessingRequest --> AgentExecution
    AgentExecution --> ToolExecution
    ToolExecution --> ProcessingRequest : Continue
    ToolExecution --> ReadyState : Complete
    
    ReadyState --> Shutdown : Stop signal
    Shutdown --> [*]
    
    note right of EnvironmentInvalid
        Windows-specific validation:
        Python environment
        Path accessibility
        Permission levels
        Dependency availability
    end note
```

## Critical Windows Compatibility Points

### 1. High Priority Issues
- **Path Separator Handling**: Convert all Unix paths to Windows format
- **Process Execution**: Replace Unix subprocess calls with Windows-compatible versions
- **Environment Variables**: Handle Windows environment variable differences
- **File Permissions**: Implement Windows permission model compatibility

### 2. Medium Priority Issues
- **Shell Command Differences**: PowerShell vs Bash command adaptations
- **Temporary File Handling**: Windows temp directory conventions
- **Unicode Handling**: Windows filesystem encoding considerations

### 3. Low Priority Issues
- **Performance Optimizations**: Windows-specific performance tuning
- **Error Message Localization**: Windows error message formatting
- **Integration Improvements**: Better Windows ecosystem integration

## Next Steps

1. **Detailed Code Analysis**: Examine each Python module for Unix-specific code
2. **Test Environment Setup**: Create Windows-specific test scenarios
3. **Implementation Planning**: Design Windows compatibility layer
4. **Validation Strategy**: Define comprehensive testing approach

---

*This document will be continuously updated as we progress through the Windows compatibility implementation.*
