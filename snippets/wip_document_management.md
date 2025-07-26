# WIP Document Management

You have access to the `wip_document_manager` tool for collaborative, iterative document development. This tool uses a **single living document + comprehensive audit log** system that eliminates file proliferation while maintaining complete version history and multi-agent collaboration tracking.

## System Overview

**Architecture:**
- **One .md file** per document (always current version)
- **One .json audit file** per document (complete edit history)
- **Shared storage** across all conversation runs (`artifacts/shared/wip_documents/`)
- **Multi-agent collaboration** with full attribution tracking
- **Cross-run persistence** - documents survive across different agent conversations

**Perfect for:** Proposals, reports, business plans, technical documentation, creative content, research papers, meeting notes, and any document requiring iterative refinement with full traceability.

## When to Use WIP Documents

Use the WIP document system when:

1. **Iterative Development Required** - Documents that need multiple rounds of refinement and improvement
2. **Multi-Agent Collaboration** - When different agents will contribute to the same document over time
3. **Cross-Run Persistence** - Documents that need to persist across multiple conversation sessions
4. **Professional Documentation** - Formal documents requiring version control and audit trails
5. **Long-term Projects** - Documents that will be developed over extended periods
6. **Status Workflow Management** - Documents that progress through draft → in_progress → review → revision → complete
7. **Content Requiring Attribution** - When you need to track who made what changes and when

## When NOT to Use WIP Documents

Skip the WIP system for:

1. **One-time Content** - Simple content that doesn't require iteration or version tracking
2. **Temporary Notes** - Quick notes or scratch content that won't be refined
3. **Static Information** - Reference materials that don't change
4. **Simple Responses** - Direct answers to user questions that don't need documentation

## Core Actions

### Creating Documents (`action: "create"`)

**When to use:** Starting a new document that will be developed iteratively.

**Required parameters:**
- `document_name`: Unique identifier (e.g., "project_proposal", "meeting_notes_2025")
- `title`: Human-readable title (e.g., "Digital Hub Expansion Strategy 2025")
- `content`: Initial document content with Markdown formatting

**Optional parameters:**
- `status`: Initial status (default: "draft")
- `notes`: Context about document creation
- `agent_name`: Attribution (auto-detected if not provided)

**Example:**
```python
wip_document_manager(
    action="create",
    document_name="ai_strategy_2025",
    title="AI Implementation Strategy for Peregian Digital Hub",
    content="""## Executive Summary
[TODO: Synthesize findings from all sections below into compelling overview highlighting strategic value, key initiatives, and expected outcomes]

## Current State Analysis
[TODO: Research current technology infrastructure, existing AI usage, gaps and opportunities. Include staff capabilities and budget constraints]

## Proposed AI Initiatives
[TODO: Based on current state analysis, propose 3-5 specific AI initiatives with clear business value. Research industry best practices and similar implementations]

## Implementation Roadmap
[TODO: Create phased implementation plan with timelines, dependencies, and resource requirements]

## Budget and Resources
[TODO: Research costs for proposed initiatives, staffing needs, and ROI projections]

## Risk Assessment
[TODO: Identify potential risks, challenges, and mitigation strategies for AI implementation]""",
    status="draft",
    notes="Initial strategy document with detailed section plans for systematic development",
    agent_name="strategy_agent"
)
```

### Reading Documents (`action: "read"`)

**When to use:** 
- Before editing to understand current content
- Reviewing document status and metadata
- Understanding document structure and sections

**Required parameters:**
- `document_name`: The document to read

**Returns:** Complete document content, metadata, section breakdown, contributor information, and file paths.

**Example:**
```python
wip_document_manager(
    action="read",
    document_name="ai_strategy_2025"
)
```

### Editing Documents (`action: "edit"`)

**When to use:** Making any changes to document content.

**Edit Types:**

1. **`append`** - Add content to the end of the document
   ```python
   wip_document_manager(
       action="edit",
       document_name="ai_strategy_2025",
       content="## Risk Assessment\n- Technical complexity risks\n- Budget overrun potential\n- Staff training requirements",
       edit_type="append",
       notes="Added comprehensive risk analysis section"
   )
   ```

2. **`prepend`** - Add content after the document header
   ```python
   wip_document_manager(
       action="edit",
       document_name="ai_strategy_2025",
       content="**Document Status:** Under active development\n**Next Review:** March 15, 2025",
       edit_type="prepend",
       notes="Added document status information"
   )
   ```

3. **`replace_section`** - Replace specific section by heading
   ```python
   wip_document_manager(
       action="edit",
       document_name="ai_strategy_2025",
       content="Our analysis reveals three critical gaps in current infrastructure:\n1. Limited API integration capabilities\n2. Insufficient data storage for AI workloads\n3. Need for enhanced security protocols",
       edit_type="replace_section",
       section="Current State Analysis",
       notes="Updated with detailed infrastructure assessment"
   )
   ```

4. **`ai_enhance`** - AI-powered content improvement
   ```python
   wip_document_manager(
       action="edit",
       document_name="ai_strategy_2025",
       edit_type="ai_enhance",
       notes="Applied AI enhancement for clarity and professional tone"
   )
   ```

5. **`ai_rewrite`** - Significant AI-powered restructuring
   ```python
   wip_document_manager(
       action="edit",
       document_name="ai_strategy_2025",
       edit_type="ai_rewrite",
       notes="Complete rewrite for better structure and flow"
   )
   ```

6. **`replace_all`** - Replace all content while keeping header
   ```python
   wip_document_manager(
       action="edit",
       document_name="ai_strategy_2025",
       content="[Completely new document content...]",
       edit_type="replace_all",
       notes="Major revision based on stakeholder feedback"
   )
   ```

### Status Management (`action: "status_update"`)

**Document Lifecycle:**
- **`draft`** - Initial version, still being written
- **`in_progress`** - Actively being developed
- **`review`** - Ready for feedback and review
- **`revision`** - Incorporating changes based on feedback
- **`complete`** - Finalized version

**Example:**
```python
wip_document_manager(
    action="status_update",
    document_name="ai_strategy_2025",
    status="review",
    notes="Ready for stakeholder review - all sections complete"
)
```

### Document Discovery

**List All Documents (`action: "list"`):**
```python
wip_document_manager(action="list")
```

**Find Documents (`action: "find"`):**
```python
wip_document_manager(
    action="find",
    document_name="strategy"  # Searches names and titles
)
```

**View Edit History (`action: "history"`):**
```python
wip_document_manager(
    action="history",
    document_name="ai_strategy_2025"
)
```

## Systematic Document Development Workflow

### Using the Document as Progress Tracker

**Key Pattern**: Use detailed section notes within the document itself to track progress and maintain focus during iterative development. This prevents context window noise from derailing systematic completion.

**Recommended Workflow:**

1. **Create Structured Template with Detailed Notes**
   ```python
   wip_document_manager(
       action="create",
       document_name="research_report",
       title="Comprehensive Market Analysis Report",
       content="""## Executive Summary
   [TODO: After completing all sections below, synthesize key findings into 3-4 paragraphs highlighting main insights, recommendations, and strategic implications]

   ## Market Overview
   [TODO: Research current market size, growth trends, key players. Focus on 2023-2025 data. Include statistical data and credible sources]

   ## Competitive Analysis  
   [TODO: Identify top 5-7 competitors, analyze their strategies, strengths/weaknesses. Create comparison framework]

   ## Customer Insights
   [TODO: Research target demographics, buying patterns, pain points. Look for recent surveys and behavioral data]

   ## Technology Trends
   [TODO: Investigate emerging technologies affecting this market. Focus on AI, automation, digital transformation impacts]

   ## Future Opportunities
   [TODO: Based on above research, identify 3-5 key opportunities with supporting evidence and market validation]

   ## Recommendations
   [TODO: Provide specific, actionable recommendations based on all research findings. Include priority levels and success metrics]""",
       status="draft"
   )
   ```

2. **Systematically Replace Each Section**
   ```python
   # Replace sections one by one with researched content
   wip_document_manager(
       action="edit",
       document_name="research_report",
       content="The current market is valued at $X billion with Y% growth...",
       edit_type="replace_section",
       section="Market Overview",
       notes="Completed market research using industry reports and statistical sources"
   )
   ```

3. **Save Executive Summary for Last**
   ```python
   # Always complete executive summary after all other sections
   wip_document_manager(
       action="edit", 
       document_name="research_report",
       content="This analysis reveals three critical market insights...",
       edit_type="replace_section",
       section="Executive Summary",
       notes="Synthesized findings from all completed sections into strategic overview"
   )
   ```

### Benefits of This Approach

- **Prevents Section Skipping**: Clear TODO notes remind you what each section needs
- **Maintains Focus**: Detailed notes keep research targeted and relevant
- **Context Window Efficiency**: Document serves as external memory, reducing token usage
- **Quality Assurance**: Systematic approach ensures comprehensive coverage
- **Progress Visibility**: Easy to see which sections are complete vs. still need work
- **Handoff Ready**: Other agents can easily understand what's needed in incomplete sections

### Section Note Best Practices

**Good Section Notes:**
- `[TODO: Research X, Y, Z with focus on recent data from credible sources]`
- `[TODO: After completing sections A and B, synthesize findings into strategic recommendations]`
- `[TODO: Include 3-5 specific examples with quantitative data where possible]`

**Poor Section Notes:**
- `[TODO: Add content here]`
- `(placeholder)`
- `TBD`

## Multi-Agent Collaboration Patterns

### Sequential Development
```
Research Agent → Creates initial document with findings
     ↓
Analysis Agent → Enhances with detailed analysis
     ↓
Writing Agent → Improves structure and clarity
     ↓
Review Agent → Adds feedback and recommendations
```

### Parallel Contribution
```
Content Agent → Develops main sections
Technical Agent → Adds technical specifications  
Business Agent → Contributes business analysis
     ↓
Coordination Agent → Integrates all contributions
```

### Iterative Refinement
```
Draft Creation → Initial Review → Revision → Final Review → Completion
     ↑                                ↓
     ←----- Continuous Improvement -----←
```

## Best Practices

### Document Naming
- Use lowercase with underscores: `project_proposal`, `meeting_notes_2025`
- Be descriptive but concise: `ai_implementation_strategy` not `doc1`
- Include version/date if needed: `budget_proposal_q1_2025`

### Content Structure
- Use clear Markdown formatting with proper headings
- Structure content logically with consistent hierarchy
- Include executive summaries for complex documents
- Use bullet points and numbered lists for clarity

### Status Management
- Start documents as `draft`
- Move to `in_progress` when actively developing
- Use `review` when ready for feedback
- Apply `revision` when incorporating changes
- Mark `complete` only when truly finalized

### Edit Notes
- Be specific about changes: "Enhanced market analysis with Q4 2024 data"
- Explain reasoning: "Restructured for better stakeholder presentation"
- Reference sources: "Updated based on team feedback from 2025-01-15 meeting"
- Track decisions: "Removed technical section per executive request"

### Collaboration Etiquette
- Always read document before editing to understand current state
- Use descriptive edit notes for team visibility
- Coordinate major changes through status updates
- Respect document workflow - don't skip from draft to complete

## Advanced Features

### Audit Trail Analysis
Every edit is tracked with:
- Timestamp and version number
- Agent attribution and run ID
- Word count changes and diff summaries
- Content hashes for change verification
- Status change history

### Cross-Run Persistence
Documents persist across:
- Different agent conversations
- Multiple run sessions
- Various agent types working on same document
- Extended development timelines

### Version Control
- Automatic version incrementing
- Complete edit history with detailed metadata
- Content change tracking with diff summaries
- Contributor analysis across agents and runs

## Example Workflows

### Creating a Business Proposal (Systematic Approach)

1. **Initial Creation with Detailed Section Plans**
   ```python
   wip_document_manager(
       action="create",
       document_name="hub_expansion_proposal",
       title="Peregian Digital Hub Expansion Proposal 2025",
       content="""## Executive Summary
   [TODO: After completing all sections, synthesize into compelling 3-paragraph overview highlighting strategic value, financial projections, and timeline]

   ## Market Analysis
   [TODO: Research Queensland tech sector growth, competitor analysis, demand for co-working spaces. Include 2024-2025 data and regional economic indicators]

   ## Expansion Strategy
   [TODO: Detail physical expansion plans, new services, target member growth. Include architectural concepts and space utilization analysis]

   ## Financial Projections
   [TODO: Create 3-year financial model with revenue projections, expansion costs, ROI analysis. Research comparable expansions]

   ## Implementation Timeline
   [TODO: Develop phased rollout plan with key milestones, dependencies, and risk mitigation strategies]

   ## Risk Assessment
   [TODO: Identify potential challenges (economic, regulatory, competitive) with specific mitigation strategies]""",
       status="draft",
       notes="Created structured template with specific research tasks for each section"
   )
   ```

2. **Systematic Section Completion**
   ```python
   # Complete each section systematically based on TODO notes
   wip_document_manager(
       action="edit",
       document_name="hub_expansion_proposal",
       content="The Queensland tech sector has grown 23% annually, with Noosa specifically showing increased demand for flexible workspace solutions...",
       edit_type="replace_section",
       section="Market Analysis",
       notes="Completed market research using ABS data, Tech Council reports, and local economic indicators"
   )
   
   wip_document_manager(
       action="edit",
       document_name="hub_expansion_proposal", 
       content="Our expansion strategy focuses on three key areas: doubling physical space to 200 workstations, introducing premium private offices, and launching innovation labs...",
       edit_type="replace_section",
       section="Expansion Strategy",
       notes="Developed comprehensive expansion plan based on member feedback and space utilization analysis"
   )
   ```

3. **Executive Summary Last**
   ```python
   # Always complete executive summary after all other sections
   wip_document_manager(
       action="edit",
       document_name="hub_expansion_proposal",
       content="This proposal outlines a strategic expansion of Peregian Digital Hub that will double our capacity while introducing premium services, generating projected revenues of $2.3M annually...",
       edit_type="replace_section", 
       section="Executive Summary",
       notes="Synthesized all section findings into compelling executive overview"
   )
   ```

4. **Status Progression**
   ```python
   wip_document_manager(
       action="status_update",
       document_name="hub_expansion_proposal",
       status="review",
       notes="Ready for stakeholder review"
   )
   ```

### Multi-Agent Technical Documentation

1. **Technical Agent** - Creates initial technical specifications
2. **Business Agent** - Adds business requirements and constraints  
3. **Writing Agent** - Improves structure and clarity
4. **Review Agent** - Validates completeness and accuracy

Each agent contributes while maintaining full audit trail of who did what and when.

## Error Handling

**Common Issues:**
- Document not found: Use `list` or `find` to locate documents
- Invalid edit_type: Check available options in tool description
- Missing required parameters: Ensure action-specific requirements are met
- Section not found: Verify exact section heading for `replace_section`

**Recovery Strategies:**
- Use `read` to understand current document state
- Check `history` to understand recent changes
- Use `find` to locate documents by partial name/title match
- Verify document_name spelling and format

---

## Quick Reference

**Essential Actions:**
- `create` - Start new document
- `read` - View current content  
- `edit` - Modify document
- `status_update` - Change workflow status
- `list` - See all documents
- `history` - View edit trail

**Edit Types:**
- `append` - Add to end
- `prepend` - Add after header
- `replace_section` - Replace by heading
- `ai_enhance` - AI improvement
- `ai_rewrite` - AI restructuring
- `replace_all` - Replace all content

**Status Flow:**
`draft` → `in_progress` → `review` → `revision` → `complete`

Use this system for any document requiring iterative development, multi-agent collaboration, or professional version control with complete audit trails. 