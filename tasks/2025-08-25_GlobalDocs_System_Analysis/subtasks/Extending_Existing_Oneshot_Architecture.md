---
title: "Extending Existing Oneshot Architecture - Minimal Changes, Maximum Leverage"
date: "2025-08-25T23:59:59.999Z"
task: "GlobalDocs_System_Analysis"
status: "Extension Strategy"
priority: "High"
tags: ["extension", "existing-system", "minimal-changes", "leverage"]
---

# Extending Existing Oneshot Architecture - Minimal Changes, Maximum Leverage

## Philosophy: Extend, Don't Replace

**Core Principle**: Leverage the existing oneshot infrastructure and guides system. Make minimal, targeted extensions rather than wholesale changes.

## Current System Analysis

### ✅ What Already Exists and Works Well

#### 1. **Guide System (`app/guides/`)**
```
app/guides/
├── how_oneshot_works.md          # System architecture overview
├── how_to_create_agents.md       # Agent creation guide
├── how_to_create_tools.md        # Tool creation guide  
├── how_to_use_tool_services.md   # Tool services reference
├── onboarding.md                 # Developer onboarding
└── how_to_setup.md               # Setup instructions
```

#### 2. **Tool Services Infrastructure (`app/tool_services.py`)**
- **Single Import Pattern**: `from app.tool_services import *`
- **LLM Integration**: `llm()`, `llm_json()`, `llm_structured()`
- **File Operations**: `save()`, `save_json()`, `read()`
- **Context Management**: Automatic run ID tracking
- **Artifact Organization**: Run-aware file organization

#### 3. **Artifact System**
- **Current Structure**: `/artifacts/{run_id}/`
- **Automatic Organization**: Via `tool_services.save()`
- **Rich Metadata**: YAML frontmatter injection
- **Run Persistence**: Conversation continuity

#### 4. **MCP Integration**
- **Existing Tools**: `read_instructions_for()`, `list_agents()`, `list_tools()`
- **Guide Access**: Dynamic guide loading system
- **Expert System**: `ask_oneshot_expert()` for architecture questions

## Extension Strategy: Minimal Additions

### 1. **Extend Tool Services with Vault Awareness**

Instead of replacing `tool_services.py`, extend it with vault capabilities:

```python
# EXTENSION: Add to existing app/tool_services.py
class ToolHelper:
    def _initialize(self):
        # ... existing initialization ...
        self.vault_mode = self._check_vault_mode()
        self.vault_manager = VaultManager() if self.vault_mode else None
    
    def _check_vault_mode(self) -> bool:
        """Check if vault mode is enabled in existing config.yaml"""
        return self.config.get("vault", {}).get("enabled", False)
    
    # EXTEND existing save() method
    def save(self, content: str, description: str = "", filename: str = None, 
             add_frontmatter: bool = True, **kwargs) -> Dict[str, Any]:
        """Enhanced save with optional vault organization"""
        
        # Use existing save logic as fallback
        if not self.vault_mode:
            return self._original_save(content, description, filename, add_frontmatter)
        
        # Vault-aware organization (new functionality)
        return self._vault_aware_save(content, description, filename, add_frontmatter, **kwargs)
```

### 2. **Add New Guides to Existing Guide System**

Leverage the existing `read_instructions_for()` system:

```python
# ADD to app/oneshot_mcp.py guide list:
@mcp.tool()
def read_instructions_for(guide_name: str) -> str:
    """... existing docstring ...
    
    Available guides:
        - "onboarding": Guide for AI Coding agents...
        - "how_oneshot_works": Technical details...
        - "how_to_create_agents": Use this guide...
        - "how_to_create_tools": Use this guide...
        - "how_to_use_tool_services": Guide for understanding...
        - "how_to_create_mcp_servers": Guide for creating...
        - "how_to_use_vault_organization": NEW - Guide for intelligent organization  # ADD
        - "how_to_create_templates": NEW - Guide for session templates            # ADD
        - "how_to_extend_checkpoints": NEW - Guide for validation checkpoints     # ADD
    """
```

### 3. **Create Minimal New Tools Using Existing Patterns**

Follow the established tool creation pattern:

```python
# NEW: tools/organize_content.py (follows existing patterns)
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "organize_content",
        "description": "Intelligently organize content using templates or AI",
        "parameters": {
            "type": "object", 
            "properties": {
                "content": {"type": "string", "description": "Content to organize"},
                "session_type": {"type": "string", "description": "Optional session type hint"},
                "force_ai": {"type": "boolean", "description": "Force AI organization", "default": False}
            },
            "required": ["content"]
        }
    }
}

def organize_content(content: str, session_type: str = None, force_ai: bool = False) -> str:
    """Organize content using hybrid template/AI approach"""
    
    try:
        # Leverage existing tool_services for everything possible
        helper = ToolHelper()  # Uses existing singleton pattern
        
        # Use existing LLM integration for AI decisions
        if force_ai or not session_type:
            organization_decision = llm_json(f"""
            Analyze this content and suggest organization:
            {content[:500]}...
            
            Return JSON with: {{"session_type": "...", "use_template": true/false}}
            """)
        
        # Use existing save() method with new vault awareness
        result = helper.save(
            content=content,
            description="Intelligently organized content",
            vault_organization=True  # New parameter, backward compatible
        )
        
        return json.dumps({
            "success": True,
            "organization_method": "hybrid",
            "result": result
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Organization failed: {str(e)}"}, indent=2)
```

### 4. **Extend Existing Config Structure**

Add vault configuration to existing `config.yaml`:

```yaml
# EXISTING config.yaml structure preserved
model:
  provider: "openai" 
  default_model: "claude-3-5-sonnet-20241022"

logfire:
  enabled: true
  service_name: "oneshot"

# NEW: Add vault configuration (backward compatible)
vault:
  enabled: false  # Disabled by default, no breaking changes
  path: "vault"
  templates:
    coding_development:
      enabled: true
      structure: "sop_compliant"
    troubleshooting:
      enabled: true
      structure: "systematic"
  ai_organization:
    model: "openai/gpt-5-nano"  # Cost-effective for organization decisions
    confidence_threshold: 0.7
    fallback_enabled: true
```

## Implementation: Leverage Existing Patterns

### Phase 1: Extend Tool Services (Week 1)

**Files to Modify (Minimal)**:
1. `app/tool_services.py` - Add vault awareness to existing ToolHelper
2. `config.yaml` - Add vault configuration section

**New Files**:
1. `app/vault_manager.py` - New module following existing patterns
2. `app/guides/how_to_use_vault_organization.md` - New guide following existing format

```python
# MINIMAL EXTENSION: app/tool_services.py
class ToolHelper:
    # ... existing code unchanged ...
    
    def _get_artifacts_dir(self) -> Path:
        """ENHANCED: existing method with vault awareness"""
        if hasattr(self, 'vault_mode') and self.vault_mode:
            return self._get_vault_artifacts_dir()
        else:
            # UNCHANGED: existing logic for backward compatibility
            return Path("artifacts") / self._current_run_id
    
    def _get_vault_artifacts_dir(self) -> Path:
        """NEW: vault-aware artifact directory"""
        # Implementation that extends existing patterns
        pass
```

### Phase 2: Add New Tools (Week 2)

**Leverage Existing**:
- Use existing tool discovery system (automatic loading from `/tools`)
- Follow existing `TOOL_METADATA` pattern
- Use existing `from app.tool_services import *` import pattern

**New Tools** (follow existing patterns):
```python
# tools/create_session_template.py
# tools/promote_to_project.py  
# tools/analyze_session_type.py
# tools/validate_organization.py
```

### Phase 3: Template System (Week 3)

**Leverage Existing**:
- Use existing Jinja2 template engine in `tool_services.py`
- Store templates in new `/templates` directory (follows existing `/agents`, `/tools` pattern)
- Use existing YAML frontmatter pattern

### Phase 4: Integration (Week 4)

**Leverage Existing**:
- Use existing MCP integration for new tools
- Follow existing guide documentation patterns
- Use existing error handling and logging

## Benefits of Extension Approach

### ✅ **Minimal Risk**
- **Backward Compatibility**: All existing functionality preserved
- **Gradual Adoption**: Vault mode is opt-in
- **Proven Patterns**: Following established oneshot conventions
- **No Breaking Changes**: Existing tools and agents continue working

### ✅ **Resource Efficiency**
- **Reuse Infrastructure**: Leverage existing tool_services, MCP, guides
- **Minimal Development**: Most functionality already exists
- **Fast Implementation**: Building on proven foundation
- **Lower Maintenance**: Following established patterns

### ✅ **Natural Integration**
- **Consistent UX**: New features feel native to oneshot
- **Familiar Patterns**: Developers already know the conventions
- **Easy Learning**: Extends existing mental models
- **Smooth Migration**: Users can migrate gradually

## Specific Extensions Needed

### 1. New Guide Files (Following Existing Format)
```
app/guides/
├── how_to_use_vault_organization.md    # NEW
├── how_to_create_templates.md          # NEW  
├── how_to_extend_checkpoints.md        # NEW
└── ... (existing guides unchanged)
```

### 2. New Tools (Following Existing Pattern)
```
tools/
├── organize_content.py                 # NEW
├── create_template.py                  # NEW
├── promote_to_project.py              # NEW
├── validate_checkpoints.py            # NEW
└── ... (existing tools unchanged)
```

### 3. Configuration Extension (Backward Compatible)
```yaml
# config.yaml - ADD vault section, preserve existing
vault:
  enabled: false  # Safe default
  # ... vault config
```

### 4. Minimal Core Changes
```python
# app/tool_services.py - EXTEND existing ToolHelper class
# app/oneshot_mcp.py - ADD new guides to existing list
```

## Migration Strategy

### For Users:
1. **Phase 1**: Everything works exactly as before
2. **Phase 2**: Enable vault mode when ready: `vault.enabled: true`
3. **Phase 3**: Start using new organization tools
4. **Phase 4**: Migrate existing content at their own pace

### For Developers:
1. **Familiar Patterns**: All new code follows existing oneshot conventions
2. **Existing Tools**: Continue working with existing tool_services patterns
3. **Easy Extension**: Add new functionality using proven patterns

## Implementation Example

### Extending save() Method (Minimal Change)
```python
# BEFORE (existing):
def save(self, content: str, description: str = "", filename: str = None) -> Dict:
    # existing implementation

# AFTER (extended):
def save(self, content: str, description: str = "", filename: str = None, 
         vault_organization: bool = None) -> Dict:
    
    # NEW: vault organization if enabled
    if vault_organization and self.vault_mode:
        return self._vault_aware_save(content, description, filename)
    
    # UNCHANGED: existing implementation for backward compatibility
    return self._original_save(content, description, filename)
```

This approach gives you **all the benefits of intelligent organization** while **preserving the existing oneshot system** and **minimizing development effort**. You get sophisticated capabilities through small, targeted extensions rather than large architectural changes.
