---
id: oneshot-specification
owner: oneshot-system  
last_updated: 2025-08-25
status: active
summary: Functional requirements and acceptance criteria for the oneshot framework
---

# Scope & Non-Goals

## In Scope
- Specialist AI agent orchestration for knowledge work tasks
- Artifact-first workflow design with file-based agent communication  
- Cross-platform compatibility (Windows, Mac, Linux)
- MCP server integration with Cursor IDE and other AI systems
- Tool services infrastructure for consistent tool development
- Task management with automated testing and git workflows
- Real-time observability through Logfire integration

## Out of Scope  
- General-purpose LLM chat interfaces (use Claude/ChatGPT directly)
- Complex multi-user collaboration features
- Real-time agent-to-agent messaging (use artifact passing)
- Visual agent workflow builders (markdown configuration only)
- Production deployment automation (development-focused)

# Functional Requirements

## FR-1: Agent Specialization
**Requirement**: Each agent must have focused expertise and specific tool allocations
**Rationale**: Specialist agents outperform general-purpose agents in domain-specific tasks

## FR-2: Artifact-First Design  
**Requirement**: Agents must produce files as primary outputs, enabling clean workflow chaining
**Rationale**: Prevents context window pollution and enables scalable multi-agent workflows

## FR-3: Tool Services Infrastructure
**Requirement**: All tools must use shared tool services for LLM, file, and API operations
**Rationale**: Reduces boilerplate by 80%, ensures consistent error handling and instrumentation

## FR-4: Cross-Platform Compatibility
**Requirement**: System must work identically on Windows, Mac, and Linux
**Rationale**: Users across different platforms must have consistent experience

## FR-5: MCP Integration
**Requirement**: System must operate as MCP server for integration with AI development tools  
**Rationale**: Enables orchestration by sophisticated AI agents like Claude Sonnet 4

## FR-6: Conversation Continuity
**Requirement**: All operations must maintain run IDs for stateful conversations across stateless LLM calls
**Rationale**: Enables complex multi-turn workflows and proper artifact organization

## FR-7: Task Management Integration
**Requirement**: Complex development tasks must follow 7-step SOP with automated testing and git workflows
**Rationale**: Ensures quality, documentation, and version control for significant work

# Acceptance Criteria (executable style)

## Agent Execution
- **Given** a valid agent name and message, **when** executing via CLI or MCP, **then** agent responds within SLA timeouts
- **Given** an agent with file context, **when** processing multimodal inputs, **then** all supported formats are processed correctly
- **Given** a failed agent execution, **when** error occurs, **then** diagnostic information is provided with recovery suggestions

## Tool Operations  
- **Given** a tool using tool services, **when** making LLM calls, **then** automatic retry logic and usage tracking is applied
- **Given** a tool saving files, **when** using save() function, **then** files are organized by run ID with metadata
- **Given** missing tool dependencies, **when** agent loads, **then** graceful degradation occurs with clear error messages

## MCP Communication
- **Given** Cursor IDE with oneshot MCP enabled, **when** calling agents, **then** stdio transport works without stalling
- **Given** multiple concurrent MCP requests, **when** processing, **then** no resource conflicts or deadlocks occur
- **Given** large agent outputs, **when** returning via MCP, **then** proper chunking and buffer management prevents hangs

## Task Workflow
- **Given** a complex development task, **when** following 7-step SOP, **then** all required artifacts are created and documented
- **Given** task completion, **when** running automated tests, **then** exit code 0 is required before marking complete
- **Given** successful task completion, **when** executing git workflow, **then** automatic commit/push occurs with detailed messages

## Cross-Platform Support
- **Given** Windows environment, **when** executing any operation, **then** path separators and process execution work correctly
- **Given** different Python environments, **when** starting system, **then** dependencies are correctly detected and loaded
- **Given** various file encodings, **when** processing files, **then** proper Unicode handling prevents corruption

# Edge Cases & Constraints  

## Rate Limits & Usage
- OpenRouter API calls: Respect provider rate limits with exponential backoff
- Token usage tracking: Enforce configurable limits to prevent runaway costs
- Concurrent agent execution: Max 10 parallel agents to prevent resource exhaustion
- File size limits: 10MB per file for multimodal processing, configurable per agent

## Environment Constraints
- Python 3.8+ required for PydanticAI compatibility
- Minimum 4GB RAM for multi-agent workflows
- Internet connectivity required for LLM APIs and external tool integrations
- Git repository initialization required for task management workflows

## Error Conditions
- Missing API keys: Graceful degradation with clear setup instructions
- Corrupted configuration files: Validation with specific error messages and examples
- Network failures: Automatic retry with circuit breaker patterns
- Disk space limitations: Early detection and cleanup recommendations

# Telemetry

## Events
- `agent.execution.started` - Agent name, model, run ID, timestamp
- `agent.execution.completed` - Duration, token usage, success/failure status  
- `tool.called` - Tool name, parameters, execution time, success/failure
- `mcp.request.received` - Request type, agent name, processing time
- `task.workflow.step` - Step number, status, artifacts created
- `error.occurred` - Error type, context, recovery action taken

## Metrics  
- `agents.executions.total` - Counter of total agent executions by agent name
- `agents.execution.duration` - Histogram of agent execution times by agent and model
- `tools.usage.total` - Counter of tool usage by tool name and agent
- `mcp.requests.total` - Counter of MCP requests by request type
- `tokens.usage.total` - Counter of LLM token usage by model and operation type
- `tasks.completed.total` - Counter of completed tasks by type and success/failure

## Golden Test Cases
- [research_agent comprehensive workflow](tasks/2025-08-25_Oneshot_Windows_Testing/tests/)
- [MCP server integration tests](tasks/2025-08-24_OneShot_Windows_Compatibility/tests/)  
- [Cross-platform compatibility tests](tasks/2025-08-25_Oneshot_Windows_Testing/tests/)
- [Task management SOP validation](tasks/2025-08-25_CursorAgent_StallPrevention/tests/)
