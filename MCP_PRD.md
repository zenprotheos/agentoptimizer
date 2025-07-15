# MCP Client Integration PRD

## Overview

This document outlines the requirements for integrating Model Context Protocol (MCP) client capabilities into our AI Agent Framework, enabling agents to connect to and use MCP servers alongside their native Python tools.

## Background

Our current agent framework supports native Python tools but lacks the ability to connect to MCP servers. The [Pydantic AI MCP client](https://ai.pydantic.dev/mcp/client/index.md) provides robust support for MCP integration, offering three transport types and advanced features like tool prefixing and sampling.

### Current State
- Agents are configured via markdown files with YAML frontmatter
- Tools are loaded from Python files in the `/tools` directory
- Agents already have an `mcp` field in their configuration (currently unused)
- System has access to MCP servers via `/Users/chrisboden/.cursor/mcp.json`

## Requirements

### Functional Requirements

#### FR1: MCP Server Configuration
- **FR1.1**: Support loading MCP server configurations from:
  - Local `./mcp.json` (repo-specific, highest priority)
  - Global `~/.cursor/mcp.json` (system-wide fallback)
- **FR1.2**: Parse existing MCP server configurations including:
  - Server name and command
  - Transport type (stdio, HTTP SSE, Streamable HTTP)
  - Arguments and environment variables
  - Authentication tokens

#### FR2: Transport Support
- **FR2.1**: Support `MCPServerStdio` for subprocess-based servers
- **FR2.2**: Support `MCPServerSSE` for HTTP Server-Sent Events transport
- **FR2.3**: Support `MCPServerStreamableHTTP` for Streamable HTTP transport
- **FR2.4**: Automatic transport detection based on server configuration

#### FR3: Agent Configuration
- **FR3.1**: Extend existing agent YAML configuration to support MCP servers:
  ```yaml
  mcp:
    - name: supabase
      prefix: "db"           # Optional tool prefix
      allow_sampling: true   # Optional sampling control
  ```
- **FR3.2**: Maintain backward compatibility with existing agent configurations
- **FR3.3**: Support both simple string format (`mcp: [supabase]`) and detailed object format

#### FR4: Tool Integration
- **FR4.1**: MCP tools appear alongside native Python tools to the LLM
- **FR4.2**: Support tool prefixing to avoid naming conflicts between servers
- **FR4.3**: Automatic prefix handling (prefix added for display, removed for execution)

#### FR5: Sampling Support
- **FR5.1**: Enable MCP sampling by default (allows MCP servers to make LLM calls via client)
- **FR5.2**: Allow per-server sampling control via agent configuration
- **FR5.3**: Proper handling of sampling requests and responses

#### FR6: Lifecycle Management
- **FR6.1**: Proper startup and shutdown of MCP servers
- **FR6.2**: Use `async with agent.run_mcp_servers():` context manager
- **FR6.3**: Graceful cleanup on errors or interruptions

#### FR7: Error Handling
- **FR7.1**: Graceful degradation when MCP servers are unavailable
- **FR7.2**: Clear error messages for configuration issues
- **FR7.3**: Robust handling of server connection failures
- **FR7.4**: Continue operation with available servers if some fail

### Non-Functional Requirements

#### NFR1: Performance
- **NFR1.1**: Minimal overhead when MCP servers aren't used
- **NFR1.2**: Efficient connection pooling and reuse
- **NFR1.3**: Parallel tool execution where possible

#### NFR2: Compatibility
- **NFR2.1**: Maintain backward compatibility with existing agents
- **NFR2.2**: Support Python 3.10+ (MCP requirement)
- **NFR2.3**: Work with existing sync interface while handling async MCP operations

#### NFR3: Security
- **NFR3.1**: Secure handling of API keys and tokens from MCP configuration
- **NFR3.2**: Proper isolation between different MCP servers
- **NFR3.3**: Safe execution of MCP tools with appropriate sandboxing

#### NFR4: Maintainability
- **NFR4.1**: Clean separation between MCP and native tool systems
- **NFR4.2**: Extensible architecture for future MCP features
- **NFR4.3**: Comprehensive error logging and debugging support

## Technical Architecture

### Dependencies
- Add `pydantic-ai[mcp]` to `requirements.txt`
- Requires Python 3.10+ for MCP support

### Key Components

#### 1. MCP Configuration Manager
```python
class MCPConfigManager:
    def load_mcp_config(self) -> Dict[str, Any]
    def get_server_config(self, server_name: str) -> Dict[str, Any]
    def create_mcp_server(self, server_name: str, config: Dict) -> MCPServer
```

#### 2. Enhanced Agent Configuration
```python
class MCPServerConfig(BaseModel):
    name: str
    prefix: Optional[str] = None
    allow_sampling: bool = True

class AgentConfig(BaseModel):
    # ... existing fields ...
    mcp: List[Union[str, MCPServerConfig]] = []
```

#### 3. MCP Server Factory
```python
class MCPServerFactory:
    def create_stdio_server(self, config: Dict) -> MCPServerStdio
    def create_sse_server(self, config: Dict) -> MCPServerSSE  
    def create_streamable_http_server(self, config: Dict) -> MCPServerStreamableHTTP
```

#### 4. Enhanced Agent Runner
- Extend `AgentRunner` to support MCP server loading and management
- Bridge async MCP operations with sync interface
- Handle server lifecycle within agent execution context

### Configuration Examples

#### Simple Configuration
```yaml
---
name: web_agent
mcp:
  - supabase
  - browsermcp
---
```

#### Advanced Configuration
```yaml
---
name: data_agent
mcp:
  - name: supabase
    prefix: "db"
    allow_sampling: true
  - name: python_runner
    prefix: "py"
    allow_sampling: false
---
```

#### MCP Server Configuration (mcp.json)
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase", "--access-token", "..."]
    },
    "python_runner": {
      "command": "deno",
      "type": "stdio",
      "args": ["run", "-N", "jsr:@pydantic/mcp-run-python", "stdio"]
    }
  }
}
```

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. Update dependencies and imports
2. Create MCP configuration loading system
3. Implement server factory pattern
4. Basic stdio server support

### Phase 2: Core Integration (Week 2)
1. Extend agent configuration parsing
2. Integrate MCP servers into agent creation
3. Implement async/sync bridge
4. Basic error handling

### Phase 3: Advanced Features (Week 3)
1. Tool prefixing support
2. HTTP transport support (SSE and Streamable)
3. Sampling configuration
4. Enhanced error handling

### Phase 4: Polish & Testing (Week 4)
1. Comprehensive testing
2. Documentation updates
3. Performance optimization
4. Edge case handling

## Testing Strategy

### Unit Tests
- MCP configuration loading
- Server factory creation
- Agent configuration parsing
- Tool prefixing logic

### Integration Tests
- End-to-end agent execution with MCP servers
- Multiple server configurations
- Error scenarios and recovery
- Tool conflict resolution

### Manual Testing
- Test with existing MCP servers (supabase, browsermcp)
- Verify backward compatibility
- Performance under load
- Error message clarity

## Success Criteria

### Primary Success Metrics
1. **Functional**: Agents can successfully use MCP server tools alongside native tools
2. **Compatibility**: All existing agents continue to work without modification
3. **Performance**: <100ms overhead for MCP server initialization
4. **Reliability**: 99%+ success rate for MCP server connections

### Secondary Success Metrics
1. **Developer Experience**: Clear error messages and debugging information
2. **Extensibility**: Easy to add new MCP servers and transport types
3. **Documentation**: Comprehensive examples and troubleshooting guides

## Risks and Mitigations

### Technical Risks
1. **Async/Sync Complexity**: Mitigate with robust async context management
2. **Server Lifecycle**: Implement comprehensive cleanup and error handling
3. **Tool Conflicts**: Use prefixing and clear naming conventions

### Operational Risks
1. **Breaking Changes**: Maintain strict backward compatibility
2. **Performance Impact**: Implement lazy loading and connection pooling
3. **Security Issues**: Audit MCP server configurations and sandboxing

## Future Enhancements

### Phase 2 Features
1. **Hot Reloading**: Dynamic MCP server configuration updates
2. **Monitoring**: Health checks and performance metrics for MCP servers
3. **Custom Transports**: Support for additional transport protocols
4. **Tool Caching**: Cache MCP tool responses for performance

### Long-term Vision
1. **MCP Server Marketplace**: Easy discovery and installation of MCP servers
2. **Visual Configuration**: GUI for MCP server management
3. **Advanced Sampling**: Custom sampling strategies and LLM routing
4. **Federation**: Connect multiple agent frameworks via MCP

## Conclusion

This MCP client integration will significantly expand the capabilities of our agent framework by providing access to the growing ecosystem of MCP servers. The implementation prioritizes backward compatibility, robust error handling, and developer experience while laying the foundation for future enhancements.

The integration leverages Pydantic AI's mature MCP client support, ensuring reliability and adherence to MCP specifications. With proper implementation, this feature will enable agents to seamlessly combine native Python tools with powerful MCP server capabilities, creating a more versatile and capable AI agent system. 