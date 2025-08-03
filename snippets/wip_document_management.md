# WIP Document Tools

You have access to tools for creating and editing structured documents that persist across sessions. These tools support iterative document development with version tracking.

## Core Tools

### `wip_doc_create` - Create new documents
```python
# Simple markdown document
wip_doc_create(
    document_name="project_proposal",
    content="# Project Proposal\n\n## Overview\n\nContent here...",
    status="draft"
)

# XML document for structured content with sections
wip_doc_create(
    document_name="technical_spec",
    content="""<document status="draft">
  <section id="requirements" status="empty">
    <brief>System requirements and constraints</brief>
    <content></content>
  </section>
  <section id="architecture" status="empty">
    <brief>Technical architecture overview</brief>
    <content></content>
  </section>
</document>""",
    file_extension=".xml"
)

# Initialize from existing file
wip_doc_create(
    document_name="meeting_notes",
    content="",  # Will be loaded from file
    existing_file_path="raw_notes.md"
)
```


### `wip_doc_edit` - Edit documents
```python
# Replace content in a specific section
# For XML: use target_id
wip_doc_edit(
    file_path="technical_spec.xml",
    content="## System Requirements\n\n- Requirement 1\n- Requirement 2",
    target_id="requirements",
    status="in_progress"
)

# For Markdown: use section heading
wip_doc_edit(
    file_path="project_proposal.md",
    content="New overview content here...",
    section="Overview",
    edit_type="replace"
)

# Append new content to document
wip_doc_edit(
    file_path="meeting_notes.md",
    content="\n## Action Items\n\n- Item 1\n- Item 2",
    edit_type="append"
)

# Update just the status (no content change)
wip_doc_edit(
    file_path="technical_spec.xml",
    content="",
    edit_type="update_status",
    target_id="requirements",
    status="complete"
)
```

### `wip_doc_read` - Read documents
```python
# Read entire document
result = wip_doc_read("read", file_path="project_proposal.md")

# Read specific section (XML only)
result = wip_doc_read("read", 
                     file_path="technical_spec.xml", 
                     section_id="requirements")

# Get just the content text (XML only)
result = wip_doc_read("read", 
                     file_path="technical_spec.xml",
                     section_id="requirements",
                     content_only=True)

# List all WIP documents
result = wip_doc_read("list")

# View document edit history
result = wip_doc_read("history", file_path="project_proposal.md")
```

## When to Use XML vs Markdown

### Use XML Documents When:
- You need to edit specific sections repeatedly without searching for headings
- Multiple agents will work on different sections
- You want to track section-level status (empty/draft/complete)
- Document has clear components that may be updated independently
- You need metadata at the section level (status, word count, etc.)

### Use Markdown Documents When:
- Document has a simple, linear structure
- You're doing sequential writing/editing
- Content doesn't need section-level tracking
- Quick drafts or notes

## Document Structures

### XML Structure Example
```xml
<document status="in_progress">
  <section id="executive-summary" status="draft" wordcount="250">
    <brief>High-level overview for stakeholders</brief>
    <content>
## Executive Summary

The content is still markdown formatted...
    </content>
  </section>
  
  <section id="budget" status="complete">
    <brief>Detailed budget breakdown</brief>
    <content>
## Budget Analysis

- Total: $50,000
- Development: $30,000
- Marketing: $20,000
    </content>
  </section>
</document>
```

### Markdown Structure Example
```markdown
# Project Proposal

*Created: 2024-01-28*
*Status: draft*

## Overview

Project description here...

## Timeline

- Phase 1: January
- Phase 2: February

## Budget

Detailed budget information...
```

## Common Use Cases

### 1. Building a Complex Document Iteratively
```python
# Create with skeleton structure
wip_doc_create(
    document_name="business_plan",
    content="""<document status="draft">
  <section id="market-analysis" status="empty">
    <brief>Analyze target market and competitors</brief>
    <content></content>
  </section>
  <section id="financial-projections" status="empty">
    <brief>3-year financial forecast</brief>
    <content></content>
  </section>
  <section id="strategy" status="empty">
    <brief>Go-to-market strategy</brief>
    <content></content>
  </section>
</document>""",
    file_extension=".xml"
)

# Fill sections one by one
wip_doc_edit(
    file_path="business_plan.xml",
    content="## Market Analysis\n\nTarget market size: $2.3B...",
    target_id="market-analysis",
    status="complete"
)
```

### 2. Collaborative Document Development
```python
# Agent 1: Creates initial draft
wip_doc_create(
    document_name="product_spec",
    content="# Product Specification\n\n## Features\n\nInitial feature list..."
)

# Agent 2: Adds technical details
wip_doc_edit(
    file_path="product_spec.md",
    content="\n## Technical Requirements\n\n- Database: PostgreSQL\n- API: REST",
    edit_type="append"
)

# Agent 3: Refines features section
wip_doc_edit(
    file_path="product_spec.md",
    content="## Features\n\nEnhanced feature descriptions with user stories...",
    section="Features"
)
```

### 3. Report Generation with Status Tracking
```python
# Create report template
wip_doc_create(
    document_name="quarterly_report",
    content="""<report status="draft">
  <section id="summary" status="empty">
    <brief>Executive summary of Q4 performance</brief>
    <content></content>
  </section>
  <section id="metrics" status="empty">
    <brief>Key performance indicators</brief>
    <content></content>
  </section>
  <section id="recommendations" status="empty">
    <brief>Strategic recommendations for Q1</brief>
    <content></content>
  </section>
</report>""",
    file_extension=".xml"
)

# Check which sections need work
result = wip_doc_read("read", file_path="quarterly_report.xml")
# Parse result to identify sections with status="empty"

# Work on empty sections
wip_doc_edit(
    file_path="quarterly_report.xml",
    content="## Key Metrics\n\n- Revenue: $1.2M (+15% YoY)\n- Users: 10,000",
    target_id="metrics",
    status="complete"
)
```

## Working Patterns

### Sequential Development
1. Create document with initial structure
2. Read to understand current state
3. Edit sections incrementally
4. Update status as you progress
5. Review complete document

### Parallel Development (XML)
- Multiple agents can work on different sections
- Use `target_id` to avoid conflicts
- Track progress via section status
- Coordinate through status updates

### Iterative Refinement
- Use `edit_type="replace"` to improve existing content
- Track iterations in edit history
- Update status to reflect document maturity

## Status Workflow

Documents and sections progress through these statuses:
- `empty` → No content yet (XML sections only)
- `draft` → Initial content, needs work
- `in_progress` → Actively being edited
- `review` → Ready for review/feedback
- `complete` → Finished and approved

## Best Practices

1. **Always read before editing** - Understand the current state
   ```python
   # Good practice
   current = wip_doc_read("read", file_path="document.xml")
   # Review content, then edit
   ```

2. **Use descriptive IDs for XML sections** 
   - Good: `executive-summary`, `technical-specs`, `budget-analysis`
   - Bad: `section1`, `part-a`, `stuff`

3. **Update status to communicate progress**
   ```python
   # Let others know this section is being worked on
   wip_doc_edit(file_path="doc.xml", content="", 
                edit_type="update_status", 
                target_id="budget", status="in_progress")
   ```

4. **Use appropriate edit types**
   - `replace` - When completely rewriting a section
   - `append` - When adding new sections/content
   - `update_status` - When only changing progress status

5. **Structure documents for your workflow**
   - Use XML when you need precise section control
   - Use markdown for simpler, linear documents
   - Include briefs in XML sections to guide content

## Error Handling

Common issues and solutions:
- **"Document not found"** → Check file path and use `wip_doc_read("list")`
- **"Section not found"** → Verify exact section heading or ID
- **Edit conflicts** → Read document first to see current state
- **XML parsing errors** → Ensure valid XML structure when creating

Remember: These tools maintain a complete edit history, so you can always check `wip_doc_read("history", file_path="...")` to understand what changes have been made.