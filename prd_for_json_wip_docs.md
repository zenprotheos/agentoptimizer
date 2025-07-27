# Response 7

I'll analyze what would be involved in supporting JSON WIP documents alongside the current markdown format. Let me examine the current WIP tool architecture and identify the changes needed.
Read file: tools/wip_doc_create.py
Read file: tools/wip_doc_edit.py
Read file: tools/wip_doc_read.py
Let me also examine the markdown-specific helper functions:
Read file: tools/wip_doc_edit.py
Read file: tools/wip_doc_read.py
Now let me examine the tool metadata to understand the current parameter structure:
Read file: tools/wip_doc_create.py
Based on my analysis, here's a comprehensive assessment of what would be involved in supporting JSON WIP documents:

## Analysis: Supporting JSON WIP Documents

### Current Architecture Analysis

The current WIP tools are **heavily markdown-centric** with the following assumptions:

1. **File Extension**: Hard-coded `.md` extension
2. **Content Structure**: Markdown headers (`#`), metadata lines (`*Created:*`), line-based operations
3. **Section Operations**: Markdown heading detection (`#`, `##`, etc.)
4. **Content Parsing**: Line-based splitting and text manipulation
5. **Metadata Integration**: Inline markdown metadata rather than structured data

### Required Changes by Component

#### 1. **Core Architecture Changes** (Major)

**File Format Detection & Routing:**
- Add `document_format` parameter to all WIP tools (`"markdown"` | `"json"`)
- Implement format detection logic based on file extension or explicit parameter
- Create separate code paths for markdown vs JSON operations
- Update file naming logic (`.md` vs `.json`)

**Content Structure Redesign:**
- **Markdown**: Current string-based line manipulation
- **JSON**: Structured object with sections, metadata, content hierarchy

```json
// Example JSON WIP document structure
{
  "metadata": {
    "title": "Research Report",
    "created": "2025-07-27T...",
    "status": "draft",
    "document_name": "research_plan"
  },
  "sections": {
    "introduction": {
      "content": "...",
      "created": "...",
      "last_modified": "..."
    },
    "methods": {
      "content": "...",
      "subsections": {
        "data_collection": "..."
      }
    }
  },
  "content": "Main document content if not sectioned"
}
```

#### 2. **wip_doc_create.py Changes** (Medium-High)

**New Parameters:**
- `document_format`: `"markdown"` | `"json"`
- `initial_structure`: For JSON, define initial sections/schema

**Logic Changes:**
- Format-specific content creation
- JSON schema initialization
- Different file extension handling
- Format-specific validation

**Complexity**: Medium-High (new content creation patterns)

#### 3. **wip_doc_edit.py Changes** (High Complexity)

**Current Edit Types Need Complete Reimplementation for JSON:**

- **`append`**: 
  - Markdown: String concatenation
  - JSON: Add to specific section or content array
  
- **`prepend`**: 
  - Markdown: Insert after header detection
  - JSON: Insert at beginning of specific section
  
- **`replace_section`**: 
  - Markdown: Find `#` headers, replace content between
  - JSON: Navigate object structure, replace section content
  
- **`replace_all`**: 
  - Markdown: Keep header, replace body
  - JSON: Keep metadata, replace content/sections

**New JSON-Specific Operations Needed:**
- `add_section`: Add new top-level section
- `remove_section`: Remove section entirely
- `update_metadata`: Modify document metadata
- `restructure`: Change section hierarchy

**Helper Functions Required:**
- `_json_find_section()`: Navigate JSON structure
- `_json_replace_section()`: Update section content
- `_json_update_metadata()`: Update JSON metadata
- `_json_validate_structure()`: Ensure valid structure

#### 4. **wip_doc_read.py Changes** (Medium)

**Reading Logic:**
- Format detection from file extension
- JSON parsing and pretty-printing
- Section extraction for JSON documents
- Different metadata extraction patterns

**New Parameters:**
- `output_format`: Return as JSON object vs formatted text
- `section_filter`: For JSON, return specific sections only

#### 5. **Tool Metadata Updates** (Low-Medium)

**Parameter Changes:**
- Add `document_format` to all tools
- Update descriptions to mention JSON support
- Add JSON-specific parameters (schema, section operations)
- Update examples and documentation

### Implementation Complexity Assessment

#### **High Complexity Areas:**

1. **Edit Operations**: Complete reimplementation needed for JSON
2. **Section Management**: JSON path navigation vs markdown header parsing
3. **Content Validation**: JSON schema validation vs markdown syntax
4. **Backward Compatibility**: Ensuring existing markdown workflows continue working

#### **Medium Complexity Areas:**

1. **File Format Detection**: Logic to determine and handle different formats
2. **Content Creation**: Different initialization patterns for each format
3. **Metadata Management**: Structured vs inline metadata approaches
4. **Error Handling**: Format-specific error scenarios

#### **Low Complexity Areas:**

1. **File Organization**: Same artifacts directory structure works for both
2. **Audit Logging**: Already JSON-based, no changes needed
3. **Tool Services Integration**: Same reading/writing patterns apply

### Design Decisions Required

#### **1. JSON Document Structure**
- **Flat vs Hierarchical**: Simple content field vs nested sections
- **Schema Flexibility**: Fixed structure vs arbitrary JSON
- **Metadata Location**: Top-level vs embedded in sections

#### **2. Edit Operation Mapping**
- **Section Concept**: How to define "sections" in JSON (object keys? array items?)
- **Content Addressing**: Path-based (`sections.introduction`) vs key-based
- **Validation**: Strict schema vs flexible structure

#### **3. Backward Compatibility**
- **Default Format**: Markdown to maintain existing behavior
- **Migration Path**: Convert existing markdown WIPs to JSON?
- **Tool Naming**: Same tools with format parameter vs separate JSON tools

### Recommended Implementation Approach

#### **Phase 1: Foundation** (2-3 days)
1. Add `document_format` parameter to all tools
2. Implement format detection logic
3. Create JSON document structure schema
4. Update file naming and organization

#### **Phase 2: Core Operations** (3-4 days)
1. Implement JSON content creation in `wip_doc_create`
2. Build JSON helper functions for navigation/manipulation
3. Implement basic JSON edit operations (append, replace_all)
4. Update read operations for JSON format

#### **Phase 3: Advanced Operations** (2-3 days)
1. Implement complex JSON edit operations (replace_section, prepend)
2. Add JSON-specific operations (add_section, restructure)
3. Comprehensive testing and validation
4. Documentation updates

#### **Phase 4: Polish & Integration** (1-2 days)
1. Error handling improvements
2. Performance optimization
3. Integration testing with research agent
4. Final documentation and examples

### Total Estimated Effort: 8-12 days

### Risks & Considerations

1. **Complexity Explosion**: JSON operations much more complex than markdown
2. **User Experience**: JSON editing less intuitive than markdown
3. **Tool Proliferation**: May need specialized JSON-only operations
4. **Testing Overhead**: Need to test both formats for all operations
5. **Agent Adaptation**: Research agents may need updates to handle JSON format effectively

### Alternative Approaches

1. **Separate JSON Tools**: Create `json_doc_*` tools instead of extending WIP tools
2. **Hybrid Approach**: JSON storage with markdown rendering for editing
3. **Schema-First**: Define strict JSON schemas for different document types
4. **Conversion Tools**: Tools to convert between markdown and JSON formats

The implementation would be **significant but achievable**, with the main complexity being the complete reimplementation of edit operations for structured JSON data versus text-based markdown manipulation.