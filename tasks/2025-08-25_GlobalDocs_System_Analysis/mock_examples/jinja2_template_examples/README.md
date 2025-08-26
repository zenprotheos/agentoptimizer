---
title: "Jinja2 Template Examples for Intelligent Context Management"
purpose: "Demonstrates practical implementation of context optimization using Jinja2 templates"
created: "2025-08-26T08:56:06.573Z"
tags: ["jinja2", "context-optimization", "templates", "examples"]
integration_with: ["2025-08-26_Understand_Jinja2_Templates_and_Snippets"]
---

# Jinja2 Template Examples

This directory contains practical examples demonstrating how to integrate Jinja2 template patterns for intelligent context management in the OneShot system.

## 📁 Examples Included

### [`intelligent_file_selection_agent.md`](intelligent_file_selection_agent.md)
**Purpose**: Complete agent template demonstrating smart file handling  
**Features**:
- Dynamic strategy selection based on file count
- Context-aware file processing
- Efficient template patterns for large file sets
- User communication about selection rationale

### [`session_index_example.md`](session_index_example.md)  
**Purpose**: Practical example of session-level indexing  
**Features**:
- Real-world session with 12 files
- Token efficiency comparison (83% reduction)
- Metadata-driven file prioritization
- Integration with existing OneShot components

## 🎯 Key Patterns Demonstrated

### **1. Adaptive Context Strategy**
```jinja2
{% if provided_filepaths | length > 5 %}
  <!-- Large file set: Use index-first approach -->
  Available: {{ provided_filepaths | length }} files
  Strategy: Selective reading via tools
{% else %}
  <!-- Small file set: Include all content -->
  {% for filepath, content in provided_files.items() %}
    {{ content }}
  {% endfor %}
{% endif %}
```

### **2. Intelligent File Selection**
- **Relevance-based filtering**: File names, extensions, paths
- **Task-aware selection**: Choose files based on current request
- **Context optimization**: 90%+ token reduction for large sessions
- **Transparent communication**: Explain selection rationale to users

### **3. Session Index Integration**
- **Metadata extraction**: Purpose, type, priority from front-matter
- **Token estimation**: Calculate context impact before loading
- **Recent file tracking**: Prioritize latest artifacts
- **Cross-file relationships**: Maintain session coherence

## 🔗 Integration with OneShot Architecture

### **Leverages Existing Components**
- ✅ **`build-index.cjs`**: Front-matter extraction and indexing
- ✅ **`AgentTemplateProcessor`**: Jinja2 template rendering engine
- ✅ **Template Variables**: `provided_files`, `provided_filepaths`, `provided_files_summary`
- ✅ **Tool System**: `read_file_contents` for selective loading

### **Extends Current Capabilities**
- 🆕 **Context optimization thresholds**: Smart strategy selection
- 🆕 **Session-level indexing**: Automated metadata compilation
- 🆕 **Intelligent selection logic**: AI-driven file prioritization
- 🆕 **Token efficiency**: 90%+ reduction for large sessions

## 🚀 Implementation Benefits

### **Performance Improvements**
- **Token Efficiency**: Massive reduction in context size
- **Response Speed**: Faster processing with focused content
- **Cost Optimization**: Lower API costs for large sessions
- **Scalability**: Handles 20+ files without context overflow

### **User Experience Benefits**
- **Transparency**: Clear explanation of file selection
- **Relevance**: AI chooses most appropriate content
- **Flexibility**: Adapts strategy based on session size
- **Control**: Users can request specific files if needed

### **Developer Benefits**
- **Reusable Patterns**: Template examples for common scenarios
- **Backward Compatibility**: Works with existing OneShot architecture
- **Modular Design**: Easy to extend and customize
- **Clear Documentation**: Well-documented examples and patterns

## 📋 Usage Guidelines

### **When to Use Large File Set Strategy**
- 6+ files in session artifacts
- Mixed file types (docs, code, logs, etc.)
- Token budget concerns
- Need for intelligent selection

### **When to Use Small File Set Strategy**  
- ≤5 files in session
- All files are relevant
- Comprehensive analysis needed
- Simple content types

### **Template Selection Logic**
```python
def get_template_strategy(file_count: int, total_tokens: int):
    if file_count > 5 or total_tokens > 8000:
        return "index_first"
    else:
        return "full_content"
```

## 🔄 Future Enhancements

### **Planned Improvements**
- **Vector Search**: Semantic similarity for file selection
- **Learning Systems**: Improve selection based on user feedback
- **Cross-Session Context**: Link related sessions intelligently
- **Advanced Indexing**: Include content summaries in indexes

### **Integration Opportunities**
- **Persona Knowledge Bases**: Apply same patterns to persona documents
- **Project-Level Indexing**: Scale up to project organization
- **Real-Time Updates**: Dynamic index updates as files change
- **Collaborative Features**: Share indexes across team members

These examples demonstrate the practical implementation of the hybrid Template+AI system with intelligent context management! 🎯
