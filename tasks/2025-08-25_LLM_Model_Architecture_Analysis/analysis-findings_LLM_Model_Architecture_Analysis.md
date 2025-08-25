# Analysis Findings - LLM Model Architecture Analysis

**Generated:** 2025-08-25T04:52:51.141Z  
**Status:** Complete  
**Critical Discovery:** Config.yaml changes DO NOT propagate system-wide - multiple override points exist

---

## Executive Summary 🚨

**CRITICAL FINDING**: Our `config.yaml` model changes from `gpt-4o-mini` to `gpt-5-nano` will **NOT automatically apply to all agents and tools**. The oneshot architecture has multiple override points that bypass the global configuration.

### Key Discoveries:

1. **✅ Global Default Works**: `config.yaml` sets system-wide default via `model_settings.model`
2. **❌ Agent Overrides**: Many agents explicitly override the model in their YAML frontmatter
3. **❌ Tool Hardcoding**: Several tools hardcode specific models and bypass agent settings entirely
4. **❌ Blocked Models**: Some tools use models that are now in our blocked list

---

## Model Selection Architecture Flow

```mermaid
flowchart TD
    A[config.yaml<br/>model_settings.model] --> B[AgentConfigManager]
    B --> C{Agent Has<br/>Model Override?}
    
    C -->|Yes| D[Agent-Specific Model<br/>from YAML frontmatter]
    C -->|No| E[Use Global Default<br/>gpt-5-nano]
    
    D --> F[AgentExecutor]
    E --> F
    
    F --> G[_create_openrouter_model()]
    G --> H[Pydantic AI Agent]
    
    I[Tool Direct LLM Calls] --> J[tool_services.llm()]
    J --> K[Tool-Specific Model<br/>BYPASSES Agent]
    
    style A fill:#e1f5fe
    style D fill:#fff3e0
    style K fill:#ff5252,color:#fff
    style I fill:#ff5252,color:#fff
```

---

## Configuration Hierarchy Analysis

### 1. Global Configuration (config.yaml)
**Location**: `config.yaml` → `model_settings.model`  
**Current Value**: `"openai/gpt-5-nano"`  
**Inheritance**: Applied via `AgentConfigManager.parse_agent_config()` lines 74-77

```python
# Lines 74-77 in app/agent_config.py
model_defaults = self.config.get('model_settings', {})
for key, default_value in model_defaults.items():
    if key not in config_data:
        config_data[key] = default_value
```

### 2. Agent-Level Overrides (HIGH IMPACT)
**Location**: Individual agent `.md` files → YAML frontmatter  
**Override Mechanism**: Direct specification in agent configuration

#### Agents Currently Overriding Global Config:
| Agent | Current Model | Status | Impact |
|-------|---------------|--------|---------|
| `web_agent.md` | `openai/gpt-4.1-mini` | ✅ Valid (expensive) | Will use expensive model |
| `search_agent.md` | `openai/gpt-5-mini` | ✅ Valid | Will use mid-cost model |
| `research_agent.md` | `openai/gpt-4o-mini` | ❌ BLOCKED | Will trigger fallback |
| `search_analyst_agent.md` | `openai/gpt-4o-mini` | ❌ BLOCKED | Will trigger fallback |

### 3. Tool-Level Hardcoding (CRITICAL ISSUE)
**Location**: Individual tool Python files  
**Override Mechanism**: Direct model specification in `llm()` calls

#### Tools With Hardcoded Models:
| Tool | Hardcoded Model | Status | Issue Level |
|------|-----------------|--------|-------------|
| `web_search.py` | `openai/gpt-4o-mini-search-preview` | ❌ BLOCKED | HIGH - Breaks search |
| `web_news_search.py` | `openai/gpt-4o-mini-search-preview` | ❌ BLOCKED | HIGH - Breaks news |
| `web_image_search.py` | `openai/gpt-4o-mini-search-preview` | ❌ BLOCKED | HIGH - Breaks images |
| `structured_search.py` | `openai/gpt-4o-mini-search-preview` | ❌ BLOCKED | HIGH - Breaks structured search |
| `generate_nrl_report.py` | `openai/gpt-4o-mini-search-preview` | ❌ BLOCKED | MEDIUM - Breaks NRL reports |

---

## Code Analysis Details

### Agent Configuration Loading
**File**: `app/agent_config.py`  
**Key Logic**: Lines 74-77 apply defaults from `config.yaml` only if not already specified in agent config

**Inheritance Pattern**:
1. Load agent YAML frontmatter
2. If `model` specified → use agent override
3. If `model` missing → apply `config.yaml` default
4. Pass to `AgentExecutor._create_openrouter_model()`

### Tool Service LLM Calls
**File**: `app/tool_services.py`  
**Key Method**: `llm()` and `_llm_async()` (lines 330-368)

**Override Pattern**:
```python
# Line 337-346 in tool_services.py
current_model = self.model  # From agent config
if model:  # Tool-specific override
    current_model = OpenAIModel(
        model_name=model,  # BYPASSES agent configuration
        provider=OpenAIProvider(...)
    )
```

### Model Restrictions Logic
**File**: `config.yaml` → `model_restrictions.blocked_models`  
**Fallback**: `model_restrictions.fallback_model`

**Current Blocks**:
- `openai/gpt-4o-mini-search-preview` ❌ (Used by 5 tools)
- `openai/gpt-4o-mini` ❌ (Used by 2 agents)
- Other expensive models

---

## Impact Assessment

### 🔴 Critical Issues (Require Immediate Fix)

1. **Search Tools Broken**: 5 tools use blocked `gpt-4o-mini-search-preview`
   - `web_search.py`, `web_news_search.py`, `web_image_search.py`
   - `structured_search.py`, `generate_nrl_report.py`
   - **Result**: Search functionality will fail or use expensive fallback

2. **Agent Fallback Triggering**: 2 agents use blocked `gpt-4o-mini`
   - `research_agent.md`, `search_analyst_agent.md` 
   - **Result**: Will use `gpt-5-nano` fallback (good for cost)

### 🟡 Medium Issues (Monitor)

3. **Expensive Agent Models**: 2 agents use costly models
   - `web_agent.md` uses `gpt-4.1-mini` (~$0.40/$1.60)
   - `search_agent.md` uses `gpt-5-mini` (~$0.25/$2.00)
   - **Result**: Higher costs than intended

### ✅ Working as Expected

4. **Default Inheritance**: Agents without model specification will use `gpt-5-nano`
5. **Cost Controls**: Blocked models should trigger fallback to `gpt-5-nano`

---

## Root Cause Analysis

### Why Config Changes Don't Propagate

1. **Agent Override Priority**: YAML frontmatter takes precedence over global config
2. **Tool Direct Calls**: Tools bypass agent config with `llm(model="specific-model")`
3. **Search-Specific Models**: Tools use specialized search models that don't exist in our new preferred list
4. **Legacy References**: Old agent/tool files reference deprecated models

### Architecture Weakness

The current architecture allows **three levels of model specification**:
1. Global (`config.yaml`) 
2. Agent-level (YAML frontmatter)
3. Tool-level (direct `llm()` calls)

This creates **configuration drift** where updates to global settings don't propagate to overrides.

---

## Recommendations

### Immediate Actions Required

#### 1. Fix Blocked Search Models 🚨
**Priority**: CRITICAL  
**Action**: Update search tools to use compatible models

```python
# In web_search.py, web_news_search.py, etc.
# Change from:
model="openai/gpt-4o-mini-search-preview"  # BLOCKED
# To:
model="openai/gpt-5-nano"  # Or remove to inherit from agent
```

#### 2. Update Agent Overrides
**Priority**: HIGH  
**Action**: Update agent YAML frontmatter

```yaml
# In research_agent.md, search_analyst_agent.md
# Change from:
model: openai/gpt-4o-mini  # BLOCKED
# To:
model: openai/gpt-5-nano  # Or remove to inherit global default
```

#### 3. Review Expensive Agent Models
**Priority**: MEDIUM  
**Action**: Evaluate if `web_agent` and `search_agent` need expensive models

### Long-Term Architecture Improvements

#### 1. Centralized Model Configuration
Create a model selection service that enforces global policies:

```python
class ModelSelectionService:
    def get_model_for_task(self, task_type: str, agent_preference: str = None):
        # Apply global policies and restrictions
        # Return validated model based on task requirements
```

#### 2. Configuration Validation
Add startup validation to detect override conflicts:

```python
def validate_model_configuration():
    # Check all agents and tools for blocked models
    # Warn about cost-inefficient overrides
    # Suggest replacements for deprecated models
```

#### 3. Model Usage Tracking
Implement runtime tracking to monitor actual model usage:

```python
def track_model_usage(model_name: str, tokens_used: int, cost: float):
    # Monitor actual vs intended model usage
    # Alert on unexpected expensive model usage
```

---

## Next Steps

### Phase 1: Immediate Fixes (Today)
- [ ] Update 5 search tools to use compatible models
- [ ] Update 2 agents with blocked models  
- [ ] Test search functionality works with new models
- [ ] Verify fallback behavior for blocked models

### Phase 2: Validation (This Week)
- [ ] Create test script to verify actual model usage
- [ ] Monitor costs after changes
- [ ] Document model selection guidelines
- [ ] Create troubleshooting guide

### Phase 3: Architecture Enhancement (Future)
- [ ] Implement centralized model selection service
- [ ] Add configuration validation checks
- [ ] Create model usage monitoring
- [ ] Establish model update procedures

---

## Conclusion

The oneshot architecture allows extensive customization through agent and tool-level model overrides, but this flexibility creates **configuration drift risks**. Our `config.yaml` changes will only affect agents without explicit overrides.

**Immediate action required**: Fix the 5 search tools using blocked models to prevent functionality breaks.

**Long-term**: Consider architectural improvements to better centralize model configuration while maintaining flexibility for specialized use cases.

---

**Status**: Analysis complete - Ready for implementation phase  
**Critical Path**: Fix search tools first to prevent system breakage
