# Implementation Plan - LLM Model Architecture Analysis

**Generated:** 2025-08-25T04:52:51.141Z  
**Task:** Comprehensive analysis of LLM model selection across oneshot architecture

---

## Objective

Determine if our `config.yaml` model changes (default: `gpt-4o-mini` → `gpt-5-nano`) propagate correctly throughout the entire oneshot system, and identify all points where LLM models are configured or overridden.

---

## Implementation Steps

### 1. Core Configuration Analysis ⏳
**Status**: Not Started  
**Priority**: High  
**Dependencies**: None

**Subtasks:**
- [ ] Analyze `app/agent_config.py` for model configuration loading
- [ ] Examine `app/agent_runner.py` for model selection logic  
- [ ] Check `app/agent_executor.py` for model handling
- [ ] Review `app/mcp_config.py` for MCP model configuration
- [ ] Trace configuration inheritance patterns

**Deliverables:**
- Configuration loading flow documentation
- Model selection logic analysis
- Configuration hierarchy mapping

---

### 2. Codebase Model Reference Search ⏳
**Status**: Not Started  
**Priority**: High  
**Dependencies**: None

**Subtasks:**
- [ ] Search for all "model" keyword references
- [ ] Search for specific model names (gpt-4o-mini, gpt-4, etc.)
- [ ] Find hardcoded model specifications
- [ ] Identify OpenAI API calls with model parameters
- [ ] Locate OpenRouter API calls with model parameters

**Search Patterns:**
```
- "model"
- "gpt-4"
- "gpt-3"
- "openai/"
- "anthropic/"
- "model_name"
- "model_settings"
```

**Deliverables:**
- Complete list of model references in codebase
- Categorization by type (config, hardcoded, dynamic)

---

### 3. Agent-Level Model Configuration Analysis ⏳
**Status**: Not Started  
**Priority**: Medium  
**Dependencies**: Step 1

**Subtasks:**
- [ ] Examine all agent markdown files in `/agents/` directory
- [ ] Check for agent-specific model specifications
- [ ] Analyze agent template processing for model handling
- [ ] Review `app/agent_template_processor.py`
- [ ] Identify override mechanisms

**Agent Files to Check:**
- news_search_agent.md
- nrl_agent.md
- oneshot_agent.md
- research_agent.md
- search_agent.md
- search_analyst_agent.md
- vision_agent.md
- web_agent.md

**Deliverables:**
- Agent model configuration matrix
- Override pattern documentation

---

### 4. Tool-Level Model Analysis ⏳
**Status**: Not Started  
**Priority**: Medium  
**Dependencies**: Step 2

**Subtasks:**
- [ ] Analyze all Python scripts in `/tools/` directory
- [ ] Check `app/tool_services.py` for model handling
- [ ] Identify tools that make direct LLM API calls
- [ ] Review tool model inheritance patterns
- [ ] Check for tool-specific model requirements

**Key Files to Analyze:**
- app/tool_services.py
- tools/*.py (all tool scripts)
- app/agent_tools.py

**Deliverables:**
- Tool model usage documentation
- Direct API call identification

---

### 5. MCP Integration Model Handling ⏳
**Status**: Not Started  
**Priority**: Medium  
**Dependencies**: Step 1

**Subtasks:**
- [ ] Examine `app/oneshot_mcp.py` for model configuration
- [ ] Check MCP server tools in `app/oneshot_mcp_tools/`
- [ ] Analyze MCP config inheritance
- [ ] Review local MCP servers in `tools/local_mcp_servers/`
- [ ] Verify MCP tool model selection

**MCP Files to Analyze:**
- app/oneshot_mcp.py
- app/oneshot_mcp_tools/*.py
- tools/local_mcp_servers/*.py

**Deliverables:**
- MCP model configuration documentation
- MCP override behavior analysis

---

### 6. Runtime Model Selection Testing ⏳
**Status**: Not Started  
**Priority**: High  
**Dependencies**: Steps 1-5

**Subtasks:**
- [ ] Create test script to verify actual model usage
- [ ] Test default agent execution
- [ ] Test agent with model override
- [ ] Test tool-specific model selection
- [ ] Verify blocked model fallback behavior
- [ ] Monitor actual API calls and costs

**Test Scenarios:**
1. Default agent call (should use gpt-5-nano)
2. Agent with explicit model override
3. Tool requiring specific model
4. Blocked model triggering fallback
5. MCP server tool execution

**Deliverables:**
- Runtime testing results
- Actual vs expected model usage report

---

### 7. Documentation and Recommendations ⏳
**Status**: Not Started  
**Priority**: Medium  
**Dependencies**: Steps 1-6

**Subtasks:**
- [ ] Document complete model selection flow
- [ ] Create configuration best practices guide
- [ ] Identify configuration improvement opportunities
- [ ] Generate model architecture diagram
- [ ] Create troubleshooting guide

**Deliverables:**
- Complete model selection documentation
- Configuration best practices
- Architecture improvement recommendations

---

## Definition of Done

### Technical Criteria
- [ ] All model references in codebase identified and categorized
- [ ] Complete model selection flow documented with UML diagrams
- [ ] Configuration hierarchy fully mapped
- [ ] Runtime testing confirms config.yaml changes take effect
- [ ] All override mechanisms identified and documented

### Validation Criteria
- [ ] Test execution confirms gpt-5-nano is used as default
- [ ] Blocked models trigger appropriate fallbacks
- [ ] No hardcoded expensive models bypass cost controls
- [ ] MCP tools inherit model configuration correctly
- [ ] Agent-specific overrides work as expected

### Documentation Criteria
- [ ] Architecture diagrams reflect actual implementation
- [ ] Configuration guide enables future model updates
- [ ] Troubleshooting guide addresses common issues
- [ ] Best practices prevent configuration drift

---

## Risk Mitigation

### Identified Risks
1. **Hardcoded Models**: Some tools may bypass config.yaml entirely
2. **Override Conflicts**: Multiple override sources may cause unpredictable behavior
3. **Legacy References**: Old agent files may reference deprecated models
4. **Cost Control Bypass**: Direct API calls may ignore cost restrictions

### Mitigation Strategies
- Comprehensive search for all model references
- Runtime testing to verify actual model usage
- Documentation of all override mechanisms
- Recommendations for centralizing model configuration

---

## Success Metrics

### Primary Metrics
- **Configuration Coverage**: % of agents/tools using config.yaml settings
- **Cost Control Effectiveness**: Verification that expensive models are blocked
- **Override Documentation**: Complete mapping of all override mechanisms

### Secondary Metrics
- **Documentation Quality**: Clear understanding of model selection flow
- **Testing Coverage**: All model selection paths tested
- **Future Maintainability**: Easy to update models system-wide

---

**Status**: Planning complete, ready to begin implementation  
**Next Action**: Start with core configuration analysis and codebase search
