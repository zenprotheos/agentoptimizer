---
title: "Session Index Example - Intelligent Context Management"
purpose: "Demonstrates how session indexing works with Jinja2 templates"
type: "example"
session_id: "jwt_auth_bug_fix_0826_144542"
created: "2025-08-26T08:56:06.573Z"
tags: ["session-index", "context-optimization", "jinja2"]
---

# Session Index Example: JWT Auth Bug Fix

## Session Overview
- **Session ID**: `jwt_auth_bug_fix_0826_144542`
- **Type**: Coding/Debugging Session  
- **Total Files**: 12 artifacts
- **Context Strategy**: Index-first (large file set)

## Generated Session Index

### 📋 File Metadata Summary

| File | Purpose | Type | Priority |
|------|---------|------|----------|
| `MASTER_Architecture_UMLs_AuthFix.md` | System architecture documentation | doc | High |
| `auth_bug_analysis.md` | Root cause analysis | analysis | High |
| `jwt_token_validator.py` | Fixed validation logic | code | High |
| `test_jwt_validation.py` | Comprehensive test suite | test | Medium |
| `security_audit_report.md` | Security implications | doc | Medium |
| `deployment_checklist.md` | Go-live requirements | checklist | Medium |
| `performance_metrics.json` | Before/after metrics | data | Low |
| `debug_logs_raw.txt` | Raw debug output | log | Low |
| `meeting_notes_0826.md` | Team discussion notes | notes | Low |
| `research_links.md` | Reference material | reference | Low |
| `old_jwt_implementation.py` | Legacy code (archived) | archive | Low |
| `temp_debugging_script.py` | Temporary utilities | temp | Low |

### 🎯 Intelligent Selection Strategy

**For Current Task: "Summarize the authentication fix"**

**Selected Files** (based on relevance):
1. `MASTER_Architecture_UMLs_AuthFix.md` - Core documentation
2. `auth_bug_analysis.md` - Problem understanding  
3. `jwt_token_validator.py` - Solution implementation

**Skipped Files** (low relevance for summary):
- Raw logs, temp scripts, meeting notes, archived code

**Context Savings**: 
- **Without Index**: ~15,000 tokens (all files)
- **With Index**: ~2,500 tokens (selected files + metadata)
- **Reduction**: 83% token savings

### 📊 Token Efficiency Comparison

```markdown
Traditional Approach (provided_files):
{% for filepath, content in all_files.items %}
### {{ filepath }}
{{ content }}  <!-- 15,000+ tokens -->
{% endfor %}

Index-First Approach (provided_filepaths):
Available: {{ provided_filepaths | length }} files
Strategy: Read only relevant files based on task
Savings: 83% context reduction
```

### 🔄 Dynamic Context Adjustment

**Template Logic**:
```jinja2
{% if provided_filepaths | length > 5 %}
  <!-- Use index-first strategy -->
  **Large Session**: Intelligent file selection active
  **Available**: {{ provided_filepaths | join(', ') }}
  **Strategy**: Use read_file_contents for relevant files only
  
{% else %}
  <!-- Use full content strategy -->
  **Small Session**: Reading all file contents
  {% for filepath, content in provided_files.items() %}
    ### {{ filepath }}
    {{ content }}
  {% endfor %}
{% endif %}
```

### 💡 Benefits Demonstrated

1. **Token Efficiency**: 83% reduction in context size
2. **Intelligent Selection**: AI chooses based on task relevance
3. **Scalability**: Handles 20+ files without context overflow
4. **Flexibility**: Adapts strategy based on file count
5. **Transparency**: Clear explanation of selection rationale

## Integration with OneShot Architecture

### **Existing Components Used**
- ✅ `build-index.cjs` - Leveraged for front-matter extraction
- ✅ `AgentTemplateProcessor` - Enhanced with index-first logic
- ✅ Jinja2 templates - Extended with intelligent selection patterns
- ✅ `provided_filepaths` - Used for large file set optimization

### **New Components Added**
- 🆕 Session index generator 
- 🆕 Template selection logic
- 🆕 Context optimization thresholds
- 🆕 Metadata-driven file prioritization

This example demonstrates how the proposed hybrid system intelligently manages context while preserving OneShot's existing architecture!
