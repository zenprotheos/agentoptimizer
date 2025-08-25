---
name: "Master Architecture UMLs - Oneshot Windows Testing"
purpose: "Comprehensive system architecture diagrams for Oneshot Windows compatibility testing"
created: "2025-08-25T00:11:32.179Z"
---

# Master Architecture UMLs - Oneshot Windows Testing

## System Testing Architecture Overview

```mermaid
graph TB
    subgraph "Test Framework Architecture"
        TR[Test Runner] --> AT[Agent Tests]
        TR --> TT[Tool Tests]
        TR --> IT[Integration Tests]
        TR --> WT[Windows Compatibility Tests]
        
        AT --> A1[news_search_agent]
        AT --> A2[nrl_agent]
        AT --> A3[oneshot_agent]
        AT --> A4[research_agent]
        AT --> A5[search_agent]
        AT --> A6[search_analyst]
        AT --> A7[vision_agent]
        AT --> A8[web_agent]
        
        TT --> T1[File Operations Tools]
        TT --> T2[Web Operations Tools]
        TT --> T3[Research Tools]
        TT --> T4[Agent Management Tools]
        TT --> T5[Document Tools]
        
        IT --> E2E[End-to-End Workflows]
        IT --> ATC[Agent-Tool Combinations]
        
        WT --> PE[Path Handling]
        WT --> CE[Command Execution]
        WT --> EV[Environment Variables]
        WT --> PS[PowerShell Integration]
    end
    
    subgraph "Oneshot System Under Test"
        OS[Oneshot System] --> AG[Agents]
        OS --> TO[Tools]
        OS --> MCP[MCP Servers]
        OS --> API[API Layer]
        
        AG --> LLM[LLM Providers]
        TO --> FS[File System]
        TO --> WEB[Web Services]
        MCP --> EXT[External Systems]
    end
    
    TR --> OS
    
    style TR fill:#e1f5fe
    style OS fill:#f3e5f5
    style WT fill:#fff3e0
```

## Agent Testing Flow Diagram

```mermaid
sequenceDiagram
    participant TF as Test Framework
    participant A as Agent
    participant T as Tools
    participant LLM as LLM Provider
    participant FS as File System
    
    TF->>A: Initialize Agent Test
    A->>LLM: API Call with Prompt
    LLM->>A: Response
    A->>T: Execute Tool
    T->>FS: File/Web Operation
    FS->>T: Result
    T->>A: Tool Response
    A->>TF: Agent Response
    TF->>TF: Validate Result
    
    Note over TF: Windows-specific validations:<br/>- Path normalization<br/>- PowerShell compatibility<br/>- Environment variables
```

## Tool Testing Matrix

```mermaid
graph LR
    subgraph "Tool Categories"
        FC[File Creator Tools] --> FCT[file_creator<br/>read_file_contents<br/>read_file_metadata<br/>export_as_pdf<br/>export_as_screenshot]
        
        WC[Web Crawling Tools] --> WCT[web_search<br/>web_read_page<br/>web_news_search<br/>web_image_search<br/>structured_search]
        
        RC[Research Tools] --> RCT[research_planner<br/>research_prompt_rewriter<br/>search_analyst<br/>wip_doc_create<br/>wip_doc_edit<br/>wip_doc_read]
        
        AC[Agent Control Tools] --> ACT[agent_caller<br/>list_agents<br/>list_tools]
        
        UT[Utility Tools] --> UTT[usage_status<br/>todo_read<br/>todo_write<br/>test_tool<br/>read_howto_docs<br/>generate_nrl_report]
    end
    
    subgraph "Windows Test Scenarios"
        FCT --> WTS1[Path Validation]
        WCT --> WTS2[Network Access]
        RCT --> WTS3[File I/O Operations]
        ACT --> WTS4[Process Management]
        UTT --> WTS5[System Integration]
    end
```

## Integration Test Architecture

```mermaid
flowchart TD
    subgraph "Integration Test Flows"
        ITE[Integration Test Engine] --> RT[Research Task Flow]
        ITE --> ST[Search Task Flow]
        ITE --> FT[File Processing Flow]
        ITE --> AT[Agent Orchestration Flow]
        
        RT --> RA[research_agent] --> RP[research_planner]
        RP --> WS[web_search] --> WRP[web_read_page]
        WRP --> WDC[wip_doc_create] --> WDE[wip_doc_edit]
        
        ST --> SA[search_agent] --> SS[structured_search]
        SS --> WNS[web_news_search] --> WIS[web_image_search]
        
        FT --> VA[vision_agent] --> FC[file_creator]
        FC --> RFC[read_file_contents] --> EPA[export_as_pdf]
        
        AT --> OA[oneshot_agent] --> LA[list_agents]
        LA --> AC[agent_caller] --> LT[list_tools]
    end
    
    subgraph "Windows Compatibility Layer"
        WCL[Windows Compatibility Layer] --> PNE[Path Normalization Engine]
        WCL --> PSE[PowerShell Execution Engine]
        WCL --> EVE[Environment Variable Engine]
        WCL --> FPE[File Permission Engine]
    end
    
    ITE --> WCL
    
    style ITE fill:#e8f5e8
    style WCL fill:#fff3e0
```

## Error Handling and Recovery Architecture

```mermaid
stateDiagram-v2
    [*] --> TestInitialization
    TestInitialization --> AgentTest : Start Agent Test
    TestInitialization --> ToolTest : Start Tool Test
    TestInitialization --> IntegrationTest : Start Integration Test
    
    AgentTest --> AgentSuccess : Test Passes
    AgentTest --> AgentFailure : Test Fails
    AgentFailure --> ErrorAnalysis
    ErrorAnalysis --> WindowsSpecificError : Windows Issue Detected
    ErrorAnalysis --> ConfigurationError : Config Issue Detected
    ErrorAnalysis --> NetworkError : Network Issue Detected
    
    ToolTest --> ToolSuccess : Test Passes
    ToolTest --> ToolFailure : Test Fails
    ToolFailure --> ErrorAnalysis
    
    IntegrationTest --> IntegrationSuccess : Test Passes
    IntegrationTest --> IntegrationFailure : Test Fails
    IntegrationFailure --> ErrorAnalysis
    
    WindowsSpecificError --> RetryWithFix : Apply Windows Fix
    ConfigurationError --> RetryWithConfig : Apply Config Fix
    NetworkError --> RetryWithTimeout : Apply Network Fix
    
    RetryWithFix --> [*]
    RetryWithConfig --> [*]
    RetryWithTimeout --> [*]
    
    AgentSuccess --> [*]
    ToolSuccess --> [*]
    IntegrationSuccess --> [*]
```

## Data Flow Analysis

```mermaid
graph LR
    subgraph "Test Data Flow"
        TD[Test Data] --> TI[Test Input]
        TI --> AT[Agent/Tool Processing]
        AT --> TR[Test Result]
        TR --> TV[Test Validation]
        TV --> TO[Test Output]
        
        subgraph "Windows-Specific Data Handling"
            WP[Windows Paths] --> PN[Path Normalization]
            PN --> FO[File Operations]
            
            WE[Windows Environment] --> EV[Environment Variables]
            EV --> PS[PowerShell Commands]
        end
        
        AT --> WP
        AT --> WE
        FO --> TR
        PS --> TR
    end
    
    style TD fill:#e3f2fd
    style TO fill:#e8f5e8
    style WP fill:#fff3e0
    style WE fill:#fff3e0
```

## Test Coverage Matrix

| Component Type | Test Coverage | Windows Specific | Integration Coverage |
|---------------|---------------|------------------|---------------------|
| Agents (8) | ✅ Unit Tests | ✅ Path Validation | ✅ End-to-End |
| Tools (25) | ✅ Unit Tests | ✅ Command Execution | ✅ Tool Chains |
| MCP Integration | ✅ Connection Tests | ✅ PowerShell Compatibility | ✅ Multi-Agent |
| File Operations | ✅ CRUD Tests | ✅ Windows Permissions | ✅ Workflow Tests |
| Web Operations | ✅ API Tests | ✅ Network Configuration | ✅ Search Workflows |

## Performance Testing Architecture

```mermaid
graph TB
    subgraph "Performance Test Framework"
        PTF[Performance Test Framework] --> LT[Load Testing]
        PTF --> ST[Stress Testing]
        PTF --> RT[Response Time Testing]
        PTF --> MT[Memory Testing]
        
        LT --> CA[Concurrent Agents]
        ST --> HL[High Load Scenarios]
        RT --> API[API Response Times]
        MT --> MU[Memory Usage Monitoring]
        
        subgraph "Windows Performance Metrics"
            WPM[Windows Performance Metrics] --> CPU[CPU Usage]
            WPM --> MEM[Memory Consumption]
            WPM --> DISK[Disk I/O]
            WPM --> NET[Network I/O]
        end
        
        PTF --> WPM
    end
    
    style PTF fill:#e1f5fe
    style WPM fill:#fff3e0
```

