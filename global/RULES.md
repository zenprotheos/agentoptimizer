---
id: oneshot-rules
owner: oneshot-system
last_updated: 2025-08-25
status: active
summary: Agent and contributor rules for the oneshot framework, enforced via Cursor global rules
---

# Agent & Contributor Rules

## Core Development Rules

### Always Read Documentation First
- **MANDATORY**: Read `/global/GLOBAL_INDEX.md` and `/global/ARCHITECTURE.md` before coding
- **For new agents/tools**: Read `app/guides/how_to_create_agents.md` and `app/guides/how_to_create_tools.md` 
- **For core changes**: Read `app/guides/onboarding.md` and `app/guides/how_oneshot_works.md`
- **Never**: Skip documentation and jump to solutions - this WILL break the system

### Specification Compliance
- Implement only what's defined in `/global/SPEC.md`
- If functionality is missing from SPEC.md, create an RFC and update the document first
- All new features must have corresponding acceptance criteria
- Maintain backward compatibility unless explicitly documented otherwise

### Architecture Adherence  
- Never violate invariants without updating `/global/ARCHITECTURE.md` first
- Respect system boundaries and ownership defined in ARCHITECTURE.md
- Use appropriate entry points (CLI vs MCP) for different use cases
- Maintain separation of concerns across system layers

### API Compatibility
- Don't change public surfaces without updating `/global/API.md`
- Maintain CLI parameter compatibility across versions
- Preserve MCP tool interfaces and response formats
- Document breaking changes with migration guides

### Documentation Maintenance
- After behavior changes, add entry to `GLOBAL_INDEX.md` → Changelog (last 5)
- Update relevant global docs when making architectural changes
- Maintain accuracy between code and documentation
- Include examples in API.md for new interfaces

## Oneshot-Specific Rules

### Agent Development
- **Specialization**: Each agent must have focused expertise, never create general-purpose agents
- **Tool Services**: Always use `from app.tool_services import *` instead of direct implementations
- **Configuration**: Use YAML frontmatter format with required fields (name, description, model, tools)
- **System Prompts**: Write clear, specific instructions with examples and behavioral guidelines
- **Testing**: Create test scenarios for each agent's core capabilities

### Tool Development  
- **Metadata**: Always include properly formatted `TOOL_METADATA` dictionary
- **Tool Services**: Use shared infrastructure functions (llm, save, read, api, template)
- **Error Handling**: Implement graceful degradation with helpful error messages
- **Parameters**: Define clear parameter schemas with types and descriptions
- **Documentation**: Include CLI test examples in docstrings

### Cross-Platform Compatibility
- **Windows Support**: All code must work on Windows, Mac, and Linux
- **Path Handling**: Use `pathlib.Path` for cross-platform path operations
- **Process Execution**: Use tool services or proper subprocess patterns with timeouts
- **File Operations**: Handle different file encodings and line endings
- **Testing**: Validate functionality across platforms

### Task Management Integration
- **Complex Tasks**: Use 7-step SOP workflow for significant development work
- **Testing Requirements**: All task completions require passing automated tests (exit code 0)
- **Git Workflow**: All task completions require automated commit/push with detailed messages
- **Documentation**: Create comprehensive UML diagrams and architecture analysis
- **Progress Tracking**: Maintain real-time status updates and completion verification

## Quality Standards

### Code Quality
- Follow PEP 8 style guidelines for Python code
- Use type hints for all function parameters and return values
- Implement proper error handling with specific exception types
- Include comprehensive docstrings with examples
- Maintain test coverage for critical functionality

### Configuration Management
- Validate all YAML configurations on load with helpful error messages
- Provide sensible defaults that work out of the box
- Support environment variable overrides for sensitive configuration
- Implement graceful degradation when optional services are unavailable
- Document all configuration options with examples

### Performance Requirements
- Agent execution must complete within SLA timeouts (30s standard, 90s complex)
- Tool operations should use efficient algorithms and caching where appropriate
- Implement connection pooling and retry logic for external API calls
- Monitor and optimize token usage to control costs
- Use lazy loading patterns for heavy resources

### Security Practices
- Never hardcode API keys or sensitive data in source code
- Validate all user inputs and file paths to prevent injection attacks
- Limit file system access to project directory and explicitly provided paths
- Implement proper authentication for external service integrations
- Log security-relevant events for audit purposes

## Cursor Global Rules Integration

These rules are enforced through Cursor's global rules system in `.cursor/rules/`:

### Automatic Rule Application
- `main_rule.mdc`: Role determination and system overview
- `coding-tasks.mdc`: 7-step SOP workflow enforcement
- `cursor-windows-rule.mdc`: Windows compatibility requirements
- `mermaid-rule.mdc`: Diagram creation standards
- `date.mdc`: Standardized date tooling usage

### Rule Compliance Checking
- All task completions must verify compliance with applicable rules
- Use `fetch_rules()` tool to retrieve and review relevant rule sets
- Document any rule violations and propose improvements
- Update global rules based on lessons learned from task execution

## Enforcement Mechanisms

### Automated Validation
- Pre-commit hooks for code quality checks
- Automated testing requirements with exit code validation
- Configuration schema validation on system startup
- API compatibility testing across versions

### Review Requirements
- All changes to `/global/*` require documentation review
- New agents and tools require capability validation
- Cross-platform testing for Windows compatibility
- Performance impact assessment for core system changes

### Continuous Improvement
- Regular review of global rules for completeness and accuracy
- Integration of lessons learned from task execution
- Performance monitoring and optimization recommendations
- User feedback incorporation for rule effectiveness

## Emergency Procedures

### System Recovery
- If core system breaks: `git checkout -- app/` to revert changes
- If configuration corruption: Restore from known-good config.yaml backup
- If MCP server issues: Restart Cursor and toggle MCP server on/off
- If dependency conflicts: Reinstall from requirements.txt in clean environment

### Rule Violations
- Document violation details and impact assessment
- Implement immediate fixes to restore system stability
- Update documentation to prevent future occurrences  
- Propose rule enhancements based on failure analysis

---

**Enforcement**: These rules are automatically applied through Cursor's global rules system and are mandatory for all development work in the oneshot repository.
